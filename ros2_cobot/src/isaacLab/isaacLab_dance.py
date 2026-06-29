"""
Creating a scene for RL with my own cobot.

Adapted from Isaac Lab & LycheeAI Tutorials. Need to run out of an IsaacLab env
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import utilities.song_extraction as Song

import argparse
from isaaclab.app import AppLauncher

##
# CLI Args
##

parser = argparse.ArgumentParser(description="Setting up and running an interactive RL scene with my own cobot.")
parser.add_argument("--num_envs", type=int, default=248, help="Number of sim environments to spawn.")
parser.add_argument("--playback", action="store_true", help="Play song audio synced to env 0.")
parser.add_argument("--phase", type=int, default=1, help="Trainin phase: 1=dance only, 2=dance+standing_up.")
parser.add_argument("--agent", action="store_true", help="Load the agent path stored in main().")
parser.add_argument("--eval", action="store_true", help="Loads agent evaluation in liue of default training.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import torch
import torch.nn as nn
import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from skrl.agents.torch.base import ExperimentCfg
from isaaclab.assets import RigidObject, RigidObjectCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.sim import SimulationContext
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from skrl.agents.torch.ppo import PPO, PPO_CFG
from skrl.envs.wrappers.torch import wrap_env
from skrl.memories.torch import RandomMemory
from skrl.resources.preprocessors.torch import RunningStandardScaler
from skrl.models.torch import DeterministicMixin, GaussianMixin, Model
from skrl.trainers.torch import SequentialTrainer

import numpy as np
import math
import librosa
if args_cli.playback:
    import sounddevice as sd



##
# Create Scene
##

@configclass
class CobotSceneCfg(InteractiveSceneCfg):
    """Configuration for Cobot Scene."""

    # Define ground and lights
    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
        )
    

    # Define Cobot w/ articulation config
    cobot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Cobot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=f"/home/brian/Projects/Cobot/ros2_cobot/src/usd/Cobot.usd",
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                fix_root_link=True,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            joint_pos={
                "Joint0": 0.0,
                "Joint1": 0.0,
                "Joint2": 0.0,
                "Joint3": 0.0,
            }
        ),
        actuators={
            "all_joints": ImplicitActuatorCfg(
                joint_names_expr=["Joint0","Joint1","Joint2","Joint3"],
                effort_limit=1.47, #Nm Stall
                velocity_limit=4.7123, #ras/s no load
                stiffness = 0.0,
                damping=0.5,
            )
        }
    )



##
# Custom Obs & Reward Funcs
## 

def audio_obs(env) -> torch.Tensor:
    # Get parallel env runtime for current episode
    elapsed_time = env.episode_length_buf * env.step_dt

    # Convert seconds to matching song frame index
    idx = (elapsed_time * env.sr / env.hop_length).long().clamp(0, len(env.beat_phase) -1)
    i = idx.cpu().numpy()

    # Grab all the audio features in the current frame
    return torch.tensor(
        np.stack([
            env.beat_phase[i],
            env.beat_confidence[i],
            env.low_db[i],
            env.mid_db[i],
            env.high_db[i],
        ], axis=-1),
        device=env.device,
        dtype=torch.float32,
    )   # shape: (num_envs,5)

def joint_sma_obs(env) -> torch.Tensor:
    return env.joint_sma # (num_envs, 4)

def beat_reward(env):
    """Reward if moving fast when beat phase = 0, and slow when beat phase = 0.5"""
    # Joint params
    joint_vels = env.scene["cobot"].data.joint_vel
    
    # Get the fastest joint for each environment → shape (num_envs,)
    max_vel = joint_vels.abs().max(dim=-1).values

    # Get beat phase
    audio = audio_obs(env)
    phase = audio[:,0]

    # invert beat phase to go from 1 to 0, aligns to motion peaks more
    inv_phase = 1 - phase

    # Do funky shift to have dance phase  
    dance_phase = torch.maximum(phase, inv_phase) - 0.75

    # Penalize high velocities too
    max_joint_vel = 1.5 #rad/s?

    # Reward states that arent moving too fast
    reward = dance_phase * max_vel

    # Penalize those that are moving too fast — torch.where needs (condition, if_true, if_false)
    #reward = torch.where(max_vel > max_joint_vel, torch.full_like(reward, -3.0), reward)

    return reward

def lean_penalty(env):    
    """linear penalty for bending over too much"""
    
    # Get link0 as the joint of interest. Desired as this is the cobots shoulder (not pan)
    joint_pos = env.scene["cobot"].data.joint_pos #(num_envs, 4)
    joint1_pos = joint_pos[:,1].abs()

    # Define angle penalty threshold, try to stay within this from upright...
    thresh_angle_deg = 45
    thresh_angle_rad = thresh_angle_deg * torch.pi / 180
    reward = -1 * joint1_pos + thresh_angle_rad
    
    # Dont reward staying perfectly upright
    reward = torch.clamp(-1 * joint1_pos + thresh_angle_rad, max=0.0)

    return reward

def variety_reward(env):
    """Penalize all joints for staying near their recent average position"""
    joint_pos = env.scene["cobot"].data.joint_pos  # (num_envs, 4)

    # how far each joint is from its n-step average → (num_envs, 4)
    dist_from_sma = (joint_pos - env.joint_sma).abs()

    #min_dist_from_sma = dist_from_sma.min(dim=-1).values

    thresh = 10 * torch.pi / 180 

    # penalty per joint, then sum across joints → (num_envs,)
    penalty = torch.clamp(thresh - dist_from_sma, min=0.0).sum(dim=-1)

    return -penalty



##
# MDP Settings
##

@configclass
class RewardsCfg:
    """Reward terms for the MDP"""

    # Reward for dancing to the sweet beat
    #dance = RewTerm(func=beat_reward, weight = 1)

    # linear decreasing reward to keep cobot mostly upright (see lean_penalty())
    #lean = RewTerm(func=lean_penalty, weight = 0.5 if args_cli.phase == 2 else 0.0)

    # 
    move_around = RewTerm(func=variety_reward, weight = 1)# if args_cli.phase == 2 else 0.0)

@configclass
class ObservationsCfg:
    """Observations specifications for the MDP"""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations policy"""

        audio = ObsTerm(func=audio_obs)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("cobot")})
        joint_q_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("cobot")})
        sma = ObsTerm(func=joint_sma_obs)

        def __post_init__(self) -> None:
            self.enable_corruption = False # Not sure exactly what this is doing.
            self.concatenate_terms = True # Same for this, not sure
    
    # Obersvation groups
    policy: PolicyCfg = PolicyCfg()

@configclass
class ActionsCfg:
    """Action specifications for the MDP"""

    # I think we're scaling torque for randomized actions movement,
    # and making it so this scalad torque is a random action for the joints
    joint_effort = mdp.JointEffortActionCfg(asset_name="cobot", joint_names=["Joint0","Joint1","Joint2","Joint3"], scale=1.25)

@configclass
class EventCfg:
    """Configuration for events"""

    # reset scene
    reset_cobot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("cobot", joint_names=["Joint0","Joint1","Joint2","Joint3"]),
            "position_range": (-0.75, 0.75),
            "velocity_range": (-0.05, 0.05),
        }
    )

@configclass
class TerminationCfg:
    """Termination terms for the MDP"""

    # (1) Time out on sim
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    # (2) Ball out of bounds / reach



##
# Cobot Environment Config
##

@configclass
class CobotEnvCfg(ManagerBasedRLEnvCfg):
    "Configuration for the cobot environment"

    # Scene settings
    scene: CobotSceneCfg = CobotSceneCfg(num_envs=10, env_spacing=1.0)
    # Basic settings
    observations : ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    # MDP Settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationCfg = TerminationCfg()

    # Render settings
    def __post_init__(self) -> None:
        """Render initialization"""
        # general settings
        self.decimation = 2   # Frames rendered relative to sim steps   
        self.episode_length_s = 30   # Define max episode length
        # viewer settings
        self.viewer_eye = (8.0, 0.0, 5.0)
        # simulation settings
        self.sim.dt = 1/120
        self.sim.render_interval = self.decimation



##
#   Create Dance Environment
## 

class DanceEnvironment(ManagerBasedRLEnv):
    """
    Extends isaac RL environment to include precomputed song observations.
    """
    def __init__(self, cfg, song_path):
        # Load song before super().__init__() — Isaac Lab calls audio_obs during setup
        # to determine obs dimensions, so these attributes must exist first
        song = Song.SongExtraction(song_path)
        self.beat_phase      = song.beat_info[0]
        self.beat_confidence = song.beat_info[1]
        self.low_db          = song.beat_info[2]['bass']
        self.mid_db          = song.beat_info[2]['mid']
        self.high_db         = song.beat_info[2]['high']
        self.sr              = 22050  # default librosa sample rate
        self.hop_length      = 512    # must match song_extraction.py

        # pre-init SMA as zeros so joint_sma_obs works during super().__init__() obs setup
        self.joint_sma = torch.zeros(cfg.scene.num_envs, 4)

        # now run Isaac Lab setup
        super().__init__(cfg)

        self.sma_len           = 10  # number of steps in the joint-position SMA window
        # circular buffer tracking all 4 joint positions over last sma_len steps, per env
        self.joint_history     = torch.zeros(self.num_envs, self.sma_len, 4, device=self.device)
        self.joint_history_idx = 0  # current write position in the buffer
        self.joint_sma         = torch.zeros(self.num_envs, 4, device=self.device)


        # audio playback — only started if --playback flag is set
        self._audio_stream = None
        if args_cli.playback:
            self.audio_data, _ = librosa.load(song_path, sr=self.sr, mono=True)
            self.audio_sample_pos = 0

            def audio_callback(outdata, frames, time, status):
                # seek to where env 0 currently is in the song
                self.audio_sample_pos = int(self.episode_length_buf[0].item() * self.step_dt * self.sr)
                chunk = self.audio_data[self.audio_sample_pos : self.audio_sample_pos + frames]
                if len(chunk) < frames:  # pad if we hit the end of the song
                    chunk = np.pad(chunk, (0, frames - len(chunk)))
                outdata[:, 0] = chunk

            self._audio_stream = sd.OutputStream(
                samplerate=self.sr,
                channels=1,
                callback=audio_callback,
                blocksize=512,
            )
            self._audio_stream.start()

    def step(self, action):
        result = super().step(action)
        joint_pos = self.scene["cobot"].data.joint_pos  # (num_envs, 4)
        self.joint_history[:, self.joint_history_idx, :] = joint_pos
        self.joint_history_idx = (self.joint_history_idx + 1) % self.sma_len
        self.joint_sma = self.joint_history.mean(dim=1)  # avg over sma_len steps → (num_envs, 4)
        return result


    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        self.joint_history[env_ids] = 0.0  # wipe stale history for reset envs
        if self._audio_stream and 0 in env_ids.tolist():
            self.audio_sample_pos = 0



## 
# Define Networks
##

class Policy(GaussianMixin, Model):
    def __init__(self, observation_space, action_space, device):
        Model.__init__(self, observation_space=observation_space, action_space=action_space, device=device)
        GaussianMixin.__init__(self, clip_actions=False)
        self.net = nn.Sequential(
            nn.Linear(17, 64), nn.ReLU(),  
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, self.num_actions),
        )
        self.log_std = nn.Parameter(torch.zeros(self.num_actions))

    def compute(self, inputs, role):
        return self.net(inputs["observations"]), {"log_std": self.log_std}


class Value(DeterministicMixin, Model):
    def __init__(self, observation_space, action_space, device):
        Model.__init__(self, observation_space=observation_space, action_space=action_space, device=device)
        DeterministicMixin.__init__(self, clip_actions=False)
        self.net = nn.Sequential(
            nn.Linear(17, 64), nn.ReLU(),  
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 1),
        )

    def compute(self, inputs, role):
        return self.net(inputs["observations"]), {}



##
# Main
##

def main(Load_Agent=False):

    #song options
    songs = {
        "Oh Darling" : "/home/brian/Music/Oh! Darling (Remastered 2009).mp3",
        "Billie Jean" : "/home/brian/Music/Michael Jackson - Billie Jean.mp3"
    }

    """Main function."""
    # Load kit helper
    env_cfg = CobotEnvCfg()
    env_cfg.scene.num_envs=args_cli.num_envs
    # Setting up RL environment
    env = DanceEnvironment(cfg=env_cfg, song_path=songs["Billie Jean"])
    env = wrap_env(env)  # skrl wrapper
    obs_space = env.observation_space
    act_space = env.action_space

    memory = RandomMemory(memory_size=1024, num_envs=env.num_envs, device=env.device)

    models = {
        "policy": Policy(env.observation_space, env.action_space, env.device),
        "value":  Value(env.observation_space, env.action_space, env.device),
    }

    cfg = PPO_CFG(
        rollouts=1024,
        learning_epochs=8,
        learning_rate=3e-4,  # also drop from 1e-3
        observation_preprocessor=RunningStandardScaler,
        observation_preprocessor_kwargs={"size": obs_space},
        value_preprocessor=RunningStandardScaler,
        value_preprocessor_kwargs={"size": 1},
        experiment=ExperimentCfg(
            directory="/home/brian/Projects/Cobot/ros2_cobot/src/isaacLab/runs/cobot",
            write_interval=500,
            checkpoint_interval=5000,
        )
    )

    agent = PPO(
        models=models,
        memory=memory,
        cfg=cfg,
        observation_space=env.observation_space,
        action_space=env.action_space,
        device=env.device,
    )

    # Load Trainer
    trainer = SequentialTrainer(cfg={"timesteps": 500_000}, env=env, agents=agent)

    # Load Agent if applicable
    agent_path = "/home/brian/Projects/Cobot/ros2_cobot/src/isaacLab/runs/cobot/26-06-28_17-33-03-484227_PPO/checkpoints/best_agent.pt"
    #agent_path = "/home/brian/Projects/Cobot/ros2_cobot/src/isaacLab/runs/Saves/Dance/phase1_agent_35000.pt"
    if args_cli.agent:
        agent.load(agent_path)
    
    # Train or eval agent
    if args_cli.eval:
        trainer.eval()
    else: 
        trainer.train()



if __name__ == "__main__":
    # run the main function

    Load_Agent = False

    main(Load_Agent)
    # close sim app
    simulation_app.close()
