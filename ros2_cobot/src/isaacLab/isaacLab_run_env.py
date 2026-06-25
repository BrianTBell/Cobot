"""
Creating a scene for RL with my own cobot.

Adapted from Isaac Lab & LycheeAI Tutorials. Need to run out of an IsaacLab env
"""


import argparse
from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Setting up and running an interactive RL scene with my own cobot.")
parser.add_argument("--num_envs", type=int, default=32, help="Number of sim environments to spawn.")
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

    # Spawn Ball
    ball = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Ball",
        spawn=sim_utils.SphereCfg(
            radius=0.05,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.25),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(-0.2, 0.0, 0.1)),
    )

    # Define Cobot w/ articulation config
    cobot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Cobot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=f"/home/brian/Projects/Cobot/ros2_cobot/src/cobot_control/usd/Cobot.usd",
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                fix_root_link=True,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            joint_pos={
                "Joint0": 0.0,
                "Joint1": 0.0,
                "Joint2": 0.0,
                "WristJoint": 0.0,
            }
        ),
        actuators={
            "all_joints": ImplicitActuatorCfg(
                joint_names_expr=["Joint0","Joint1","Joint2","WristJoint"],
                effort_limit=1.47, #Nm Stall
                velocity_limit=4.7123, #ras/s no load
                stiffness = 0.0,
                damping=0.5,
            )
        }
    )


##
# MDP Settings
## 

def reward_ball_speed(env: ManagerBasedRLEnv) -> torch.Tensor:
        vel = env.scene["ball"].data.root_lin_vel_w
        return torch.norm(vel, dim=-1)
    
def reward_wrist_proximity(env: ManagerBasedRLEnv) -> torch.Tensor:
    ball_pos = env.scene["ball"].data.root_pos_w
    wrist_pos = env.scene["cobot"].data.body_pos_w[:, -1, :] # Last body part is wrist
    dist = torch.norm(ball_pos - wrist_pos, dim=-1)
    return torch.exp(-dist * 3.0) # peaks at 1.0 when wrist touches ball, decays with distance

def ball_out_of_reach(env: ManagerBasedRLEnv, max_dist: float = 0.6) -> torch.Tensor:
        ball_pos = env.scene["ball"].data.root_pos_w
        cobot_pos = env.scene["cobot"].data.root_pos_w
        dist_xy = torch.norm(ball_pos[:, :2] - cobot_pos[:, :2], dim=-1)
        return dist_xy > max_dist


@configclass
class ActionsCfg:
    """Action specifications for the MDP"""

    # I think we're scaling torque for randomized actions movement,
    # and making it so this scalad torque is a random action for the joints
    joint_effort = mdp.JointEffortActionCfg(asset_name="cobot", joint_names=["Joint0","Joint1","Joint2","WristJoint"], scale=1.25)

@configclass
class ObservationsCfg:
    """Observations specifications for the MDP"""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations policy"""

        # I think this would be real time readings of joint positions and velocities.
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("cobot")})
        joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("cobot")})

        # Add the wrist and ball too the policy so their interaction can be learned
        ball_pos = ObsTerm(func=mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("ball")})
        ball_vel = ObsTerm(func=mdp.root_lin_vel_w, params={"asset_cfg": SceneEntityCfg("ball")})
        wrist_pos = ObsTerm(func=mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("cobot", body_names=["Wrist"])})

        def __post_init__(self) -> None:
            self.enable_corruption = False # Not sure exactly what this is doing.
            self.concatenate_terms = True # Same for this, not sure
    
    # Obersvation groups
    policy: PolicyCfg = PolicyCfg()

@configclass
class EventCfg:
    """Configuration for events"""

    # reset scene
    reset_cobot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("cobot", joint_names=["Joint0","Joint1","Joint2","WristJoint"]),
            "position_range": (-0.2, 0.2),
            "velocity_range": (0.0, 0.0),
        }
    )

    reset_ball = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("ball"),
            "pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1), "z": (0.5, 1.0)},
            "velocity_range": {"z": (1.0, 2.0)},
        }
    )

@configclass
class RewardsCfg:
    """Reward terms for the MDP"""

    # (1) Staying alive reward
    alive = RewTerm(func=mdp.is_alive, weight=1.0)
    # (2) Dying penalty
    terminating = RewTerm(func=mdp.is_terminated, weight = -0.2)
    # (3) Primary task: keep arm upright
        # I would like to be able to have the arm touch and mvoe a ball that's on the ground, tutor me on how to do this.
    # (4) Shaping task:
        # Not really sure what I would use to shape, maybe something like keeping the ball still and touching it, I'd like it to play with it

    ball_speed = RewTerm(func=reward_ball_speed, weight = 0.5)
    wrist_to_ball = RewTerm(func=reward_wrist_proximity, weight = 1.0)

@configclass
class TerminationCfg:
    """Termination terms for the MDP"""

    # (1) Time out on sim
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    # (2) Ball out of bounds / reach
    
    ball_escaped = DoneTerm(func=ball_out_of_reach, params={"max_dist": 0.6})


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
        self.decimation = 2             # Frames rendered relative to sim steps
        self.episode_length_s = 7.5     # Define max episode length
        # viewer settings
        self.viewer_eye = (8.0, 0.0, 5.0)
        # simulation settings
        self.sim.dt = 1/120
        self.sim.render_interval = self.decimation


## 
# Define Network
##

class Policy(GaussianMixin, Model):
    def __init__(self, observation_space, action_space, device):
        Model.__init__(self, observation_space=observation_space, action_space=action_space, device=device)
        GaussianMixin.__init__(self, clip_actions=False)
        self.net = nn.Sequential(
            nn.Linear(self.num_observations, 64), nn.ReLU(),
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
            nn.Linear(self.num_observations, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 1),
        )

    def compute(self, inputs, role):
        return self.net(inputs["observations"]), {}


##
# Main
##

def main():
    """Main function."""
    # Load kit helper
    env_cfg = CobotEnvCfg()
    env_cfg.scene.num_envs=args_cli.num_envs
    # Setting up RL environment
    env = ManagerBasedRLEnv(cfg=env_cfg)
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
            directory="runs/cobot",
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

    trainer = SequentialTrainer(cfg={"timesteps": 200_000}, env=env, agents=agent)
    trainer.train()

if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
