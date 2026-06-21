"""
Creating a scene for RL with my own cobot.

Per Isaac Lab & LycheeAI Tutorials.
"""


import argparse
from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Setting up and running an interactive RL scene with my own cobot.")
parser.add_argument("--num_envs", type=int, default=16, help="Number of sim environments to spawn.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import torch
import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
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


# Create a class for the cobot scene
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
                damping=1.0,
            )
        }
    )


##
# MDP Settings
## 

@configclass
class ActionsCfg:
    """Action specifications for the MDP"""

    # I think we're scaling torque for randomized actions movement,
    # and making it so this scalad torque is a random action for the joints
    torque_scalar = 1.25
    joint_effort = mdp.JointEffortActionCfg(asset_name="cobot", joint_names=["Joint0","Joint1","Joint2","WristJoint"], scale=torque_scalar)

@configclass
class ObservationsCfg:
    """Observations specifications for the MDP"""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations policy"""

        # I think this would be real time readings of joint positions and velocities.
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel)

        def __pos_init__(self) -> None:
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
            "position_range": (-1.0, 1.0),
            "velocity_range": (-0.5, 0.5)
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

@configclass
class TerminationCfg:
    """Termination terms for the MDP"""

    # (1) Time out on sim
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    # (2) Ball out of bounds / reach
        # Not sure how to implement this, please tutor


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
    rewards = RewardsCfg = RewardsCfg()
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



def main():
    """Main function."""
    # Load kit helper
    env_cfg = CobotEnvCfg()
    env_cfg.scene.num_envs=args_cli.num_envs
    # Setting up RL environment
    env = ManagerBasedRLEnv(cfg=env_cfg)

    # Simulate physics
    count = 0
    while simulation_app.is_running():
        with torch.inference_mode():
            # reset
            if count % 3000 == 0:
                count = 0
                env.reset()
                print("-" * 80)
                print("[INFO]: Resetting Environment...")
                
                # Sample random actions
                joint_efforts = torch.randn_like(env.action_manager.action)
                print(f"[Env 0]: Joint Effort, being scaled afterwards: {joint_efforts[0].item}")

                # Step the environment
                obs, rew, terminated, truncated, info = env.step(joint_efforts)
                print(f"[Env 0]: Reward {rew[0].item()}")
                print(f"[Env 0]: All Observations {obs['policy']}")

            count += 1


    env.close()

if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
