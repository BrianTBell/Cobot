"""
Viewer for watching the trained cobot dance agent in real time.
Audio plays at wall-clock speed, independent of sim rate.

Usage:
    python isaacLab_viewer.py --agent <path/to/agent.pt> [--song <key>]
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import utilities.song_extraction as Song
import utilities.paths as paths

import argparse
from isaaclab.app import AppLauncher

##
# CLI Args
##

parser = argparse.ArgumentParser(description="Watch the trained cobot dance agent.")
parser.add_argument("--agent", type=str, required=True, help="Path to trained agent checkpoint (.pt).")
parser.add_argument("--song", type=str, default="Billie Jean", help="Song key: 'Billie Jean' or 'Oh Darling'.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of parallel viewer envs (default 1).")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import time
import torch
import torch.nn as nn
import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from skrl.agents.torch.base import ExperimentCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass
from skrl.agents.torch.ppo import PPO, PPO_CFG
from skrl.envs.wrappers.torch import wrap_env
from skrl.memories.torch import RandomMemory
from skrl.resources.preprocessors.torch import RunningStandardScaler
from skrl.models.torch import DeterministicMixin, GaussianMixin, Model
from skrl.trainers.torch import SequentialTrainer
import sounddevice as sd
import numpy as np
import librosa


##
# Songs
##

SONGS = {
    "Oh Darling":  "/home/brian/Music/Oh! Darling (Remastered 2009).mp3",
    "Billie Jean": "/home/brian/Music/Michael Jackson - Billie Jean.mp3",
}


##
# Scene
##

@configclass
class CobotSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
    )
    cobot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Cobot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(paths.USD_PATH),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(fix_root_link=True),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            joint_pos={"Joint0": 0.0, "Joint1": 0.0, "Joint2": 0.0, "Joint3": 0.0}
        ),
        actuators={
            "all_joints": ImplicitActuatorCfg(
                joint_names_expr=["Joint0", "Joint1", "Joint2", "Joint3"],
                effort_limit=1.47,
                velocity_limit=4.7123,
                stiffness=0.0,
                damping=0.5,
            )
        },
    )


##
# Obs functions — must match training file exactly
##

def audio_obs(env) -> torch.Tensor:
    # Use wall-clock elapsed time so the agent hears the same beat position
    # as the actual audio stream — keeps robot motion in sync with playback
    if env._stream_start is None:
        elapsed = 0.0
    else:
        elapsed = time.time() - env._stream_start
    idx = int(elapsed * env.sr / env.hop_length)
    idx = min(idx, len(env.beat_phase) - 1)
    i = np.full(env.num_envs, idx, dtype=np.int64)
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
    )  # (num_envs, 5)

def joint_sma_obs(env) -> torch.Tensor:
    return env.joint_sma  # (num_envs, 4)


##
# Minimal reward (needed by RewardsCfg but irrelevant during eval)
##

def null_reward(env):
    return torch.zeros(env.num_envs, device=env.device)


##
# MDP config
##

@configclass
class RewardsCfg:
    placeholder = RewTerm(func=null_reward, weight=0.0)

@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        audio      = ObsTerm(func=audio_obs)
        joint_vel  = ObsTerm(func=mdp.joint_vel_rel,  params={"asset_cfg": SceneEntityCfg("cobot")})
        joint_q_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("cobot")})
        sma        = ObsTerm(func=joint_sma_obs)

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()

@configclass
class ActionsCfg:
    joint_effort = mdp.JointEffortActionCfg(
        asset_name="cobot",
        joint_names=["Joint0", "Joint1", "Joint2", "Joint3"],
        scale=1.25,
    )

@configclass
class EventCfg:
    reset_cobot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("cobot", joint_names=["Joint0", "Joint1", "Joint2", "Joint3"]),
            "position_range": (-0.75, 0.75),
            "velocity_range": (-0.05, 0.05),
        },
    )

@configclass
class TerminationCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)

@configclass
class CobotEnvCfg(ManagerBasedRLEnvCfg):
    scene: CobotSceneCfg = CobotSceneCfg(num_envs=1, env_spacing=1.0)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationCfg = TerminationCfg()

    def __post_init__(self) -> None:
        self.decimation = 2
        self.episode_length_s = 300  # long episode — let the song play
        self.viewer_eye = (4.0, 0.0, 3.0)
        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation


##
# Dance Environment (matches training)
##

class DanceEnvironment(ManagerBasedRLEnv):
    def __init__(self, cfg, song_path):
        song = Song.SongExtraction(song_path)
        self.beat_phase      = song.beat_info[0]
        self.beat_confidence = song.beat_info[1]
        self.low_db          = song.beat_info[2]['bass']
        self.mid_db          = song.beat_info[2]['mid']
        self.high_db         = song.beat_info[2]['high']
        self.sr              = 22050
        self.hop_length      = 512

        self.joint_sma = torch.zeros(cfg.scene.num_envs, 4)
        self._stream_start = None  # must exist before super().__init__() calls audio_obs
        super().__init__(cfg)

        self.sma_len           = 25
        self.joint_history     = torch.zeros(self.num_envs, self.sma_len, 4, device=self.device)
        self.joint_history_idx = 0
        self.joint_sma         = torch.zeros(self.num_envs, 4, device=self.device)

        # Load audio for wall-clock playback
        self._audio_data, _ = librosa.load(song_path, sr=self.sr, mono=True)
        self._stream_start: float | None = None
        self._audio_stream = sd.OutputStream(
            samplerate=self.sr,
            channels=1,
            callback=self._audio_callback,
            blocksize=512,
        )

    def _audio_callback(self, outdata, frames, time_info, status):
        # Advance audio position using wall-clock time so it plays at real speed
        if self._stream_start is None:
            outdata[:] = 0
            return
        elapsed = time.time() - self._stream_start
        pos = int(elapsed * self.sr)
        chunk = self._audio_data[pos : pos + frames]
        if len(chunk) < frames:
            chunk = np.pad(chunk, (0, frames - len(chunk)))
        outdata[:, 0] = chunk

    def step(self, action):
        result = super().step(action)
        joint_pos = self.scene["cobot"].data.joint_pos
        self.joint_history[:, self.joint_history_idx, :] = joint_pos
        self.joint_history_idx = (self.joint_history_idx + 1) % self.sma_len
        self.joint_sma = self.joint_history.mean(dim=1)
        return result

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        self.joint_history[env_ids] = 0.0

    def start_audio(self):
        self._stream_start = time.time()
        self._audio_stream.start()

    def close(self):
        self._audio_stream.stop()
        self._audio_stream.close()
        super().close()


##
# Networks — must match training file exactly (obs_dim=17)
##

class Policy(GaussianMixin, Model):
    def __init__(self, observation_space, action_space, device):
        Model.__init__(self, observation_space=observation_space, action_space=action_space, device=device)
        GaussianMixin.__init__(self, clip_actions=False)
        # audio(5) + joint_vel(4) + joint_pos(4) + sma(4) = 17
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

def main():
    song_path = SONGS[args_cli.song]

    env_cfg = CobotEnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs

    env = DanceEnvironment(cfg=env_cfg, song_path=song_path)
    env_wrapped = wrap_env(env)

    models = {
        "policy": Policy(env_wrapped.observation_space, env_wrapped.action_space, env_wrapped.device),
        "value":  Value(env_wrapped.observation_space, env_wrapped.action_space, env_wrapped.device),
    }

    cfg = PPO_CFG(
        rollouts=1024,
        observation_preprocessor=RunningStandardScaler,
        observation_preprocessor_kwargs={"size": env_wrapped.observation_space},
        value_preprocessor=RunningStandardScaler,
        value_preprocessor_kwargs={"size": 1},
        experiment=ExperimentCfg(
            directory=str(paths.ISAACLAB_RUNS_DIR / "cobot"),
            write_interval=0,        # no logging during eval
            checkpoint_interval=0,
        ),
    )

    memory = RandomMemory(memory_size=1, num_envs=env_wrapped.num_envs, device=env_wrapped.device)

    agent = PPO(
        models=models,
        memory=memory,
        cfg=cfg,
        observation_space=env_wrapped.observation_space,
        action_space=env_wrapped.action_space,
        device=env_wrapped.device,
    )

    agent.load(args_cli.agent)

    env.start_audio()

    trainer = SequentialTrainer(cfg={"timesteps": 1_000_000}, env=env_wrapped, agents=agent)
    trainer.eval()


if __name__ == "__main__":
    main()
    simulation_app.close()
