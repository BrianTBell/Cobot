#!/home/brian/miniconda3/envs/env_isaaclab/bin/python
"""
Minimal IsaacLab sim wrapper for Phase 0 babbling: no ball, no reward-driven
task, no PPO training. Just the arm, driven by OU noise, logging transitions
to the replay buffer for later (Phase 1) world-model training.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import utilities.paths as paths

sys.path.append(str(Path(__file__).resolve().parent.parent))
from cobot_control.utilities import load_joint_limits

import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Cobot babbling for IMOL Phase 0.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of sim environments to spawn.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import torch
import numpy as np
import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from ou_noise import OUNoise
from replay_buffer import ReplayBuffer


##
# Scene
##

@configclass
class CobotSceneCfg(InteractiveSceneCfg):
    """Configuration for Cobot Scene."""

    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
    )

    cobot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Cobot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(paths.USD_PATH),
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
                joint_names_expr=["Joint0", "Joint1", "Joint2", "Joint3"],
                effort_limit=1.47,
                velocity_limit=4.7123,
                # STS3215 has onboard position PID; these approximate it as an
                # external PD gain, taken from mujoco_menagerie's SO-ARM100
                # (same servo, values reverse-engineered from real hardware)
                stiffness=17.8,
                damping=0.6,
            )
        }
    )


##
# MDP settings
##

JOINT_NAMES = ["Joint0", "Joint1", "Joint2", "Joint3"]
JOINT_LIMITS = load_joint_limits()  # [(min_rad, max_rad), ...] in Joint0..Joint3 order


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""
    # OUNoise already outputs real joint angles (radians) bounded by JOINT_LIMITS,
    # so the action is applied as-is: no additional scale/offset needed.
    joint_pos = mdp.JointPositionActionCfg(
        asset_name="cobot",
        joint_names=JOINT_NAMES,
        scale=1.0,
        offset=0.0,
        use_default_offset=False,
    )


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP -- low-dim state only, no vision (M2 not built yet)."""

    @configclass
    class PolicyCfg(ObsGroup):
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("cobot")})
        joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("cobot")})

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""
    reset_cobot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("cobot", joint_names=["Joint0", "Joint1", "Joint2", "Joint3"]),
            "position_range": (-0.75, 0.75),
            "velocity_range": (-0.05, 0.05),
        }
    )


@configclass
class RewardsCfg:
    """Placeholder only -- ManagerBasedRLEnv requires a reward term to construct.
    Nothing trains on this in Phase 0; the value is unused."""
    alive = RewTerm(func=mdp.is_alive, weight=1.0)


@configclass
class TerminationCfg:
    """Time-out only. No task-specific termination (no ball to escape)."""
    time_out = DoneTerm(func=mdp.time_out, time_out=True)


@configclass
class CobotEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the cobot babbling environment."""

    scene: CobotSceneCfg = CobotSceneCfg(num_envs=1, env_spacing=3.0)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationCfg = TerminationCfg()

    def __post_init__(self) -> None:
        self.decimation = 2
        self.episode_length_s = 60
        self.viewer_eye = (8.0, 0.0, 5.0)
        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation


##
# Babbling loop
##

NUM_BABBLE_STEPS = 100_000
BUFFER_CAPACITY = 100_000
OBS_DIM = 8   # 4 joint_pos_rel + 4 joint_vel_rel
ACTION_DIM = 4


def main():
    env_cfg = CobotEnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env = ManagerBasedRLEnv(cfg=env_cfg)

    OUnoise = OUNoise(joint_limits=JOINT_LIMITS)
    buffer = ReplayBuffer(capacity=BUFFER_CAPACITY, obs_dim=OBS_DIM, action_dim=ACTION_DIM)

    obs_dict, _ = env.reset()
    obs = obs_dict["policy"][0].cpu().numpy()

    for step in range(NUM_BABBLE_STEPS):
        action = OUnoise.sample()
        action_tensor = torch.tensor(action, dtype=torch.float32, device=env.device).unsqueeze(0)

        next_obs_dict, _, terminated, truncated, _ = env.step(action_tensor)
        next_obs = next_obs_dict["policy"][0].cpu().numpy()

        done = bool(terminated[0]) or bool(truncated[0])
        buffer.add(obs, action, next_obs, done=done)
        obs = next_obs

        if done:
            obs_dict, _ = env.reset()
            obs = obs_dict["policy"][0].cpu().numpy()
            OUnoise.reset()

        if step % 1000 == 0:
            print(f"step {step}, buffer size {buffer.size}")

            if step % 10_000 == 0 and step > 0:
                buffer.save(paths.BUFFER_SAVE_PATH)
                print(f"checkpointed buffer at step {step}")

    buffer.save(paths.BUFFER_SAVE_PATH)
    print("final buffer saved")


if __name__ == "__main__":
    main()
    simulation_app.close()