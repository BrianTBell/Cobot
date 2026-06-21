"""
Creating a scene for RL with my own cobot.

Per Isaac Lab & LycheeAI Tutorials.
"""


import argparse
from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Setting up an interactive scene with my own cobot.")
parser.add_argument("--num_envs", type=int, default=2, help="Number of sim environments to spawn.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg, AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
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



def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    """Runs the simulation loop."""
    # Extract scene entities
    # note: we only do this here for readability. In general, it is better to access the entities directly from
    #   the dictionary. This dictionary is replaced by the InteractiveScene class in the next tutorial.
    robot = scene["cobot"]
    # Define simulation stepping
    sim_dt = sim.get_physics_dt()
    count = 0
    # Simulation loop
    while simulation_app.is_running():
        # Reset
        if count % 1000 == 0:
            # reset counter
            count = 0
            # reset the scene entities
            # root state
            # we offset the root state by the origin since the states are written in simulation world frame
            # if this is not done, then the robots will be spawned at the (0, 0, 0) of the simulation world
            root_state = robot.data.default_root_state.clone()
            root_state[:, :3] += scene.env_origins
            robot.write_root_pose_to_sim(root_state[:, :7])
            robot.write_root_velocity_to_sim(root_state[:, 7:])
            # set joint positions with some noise
            joint_pos, joint_vel = robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone()
            joint_pos += torch.rand_like(joint_pos) * 0.1
            robot.write_joint_state_to_sim(joint_pos, joint_vel)
            # clear internal buffers
            robot.reset()
            print("[INFO]: Resetting cobot state...")

        # Apply random action every so often
        torque_scalar = 1.2
        # -- generate random joint efforts
        efforts = torch.randn_like(robot.data.joint_pos) * torque_scalar
        # -- apply action to the robot
        robot.set_joint_effort_target(efforts)
        # -- write data to sim
        robot.write_data_to_sim()
        # Perform step
        sim.step()
        # Increment counter
        count += 1
        # Update buffers
        robot.update(sim_dt)


def main():
    """Main function."""
    # Load kit helper
    sim_cfg = sim_utils.SimulationCfg(device=args_cli.device)
    sim = SimulationContext(sim_cfg)
    # Set main camera
    sim.set_camera_view([2.5, 0.0, 4.0], [0.0, 0.0, 2.0])
    # Design scene
    scene_cfg = CobotSceneCfg(num_envs=args_cli.num_envs, env_spacing=1.0)
    scene = InteractiveScene(scene_cfg)
    # Play the simulator
    sim.reset()
    # Now we are ready!
    print("[INFO]: Setup complete...")
    # Run the simulator
    run_simulator(sim, scene)


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
