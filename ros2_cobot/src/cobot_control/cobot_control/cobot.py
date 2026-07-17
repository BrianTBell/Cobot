import controllers.joint_controller as jc
import kinematics.ik_solver as ik
import trajectory.planner as tr

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

import time
import math

class Cobot:
    def __init__(self):
        super().__init__('cobot')
        self.controller = jc.JointController()
        self.kinematics = ik.IKSolver()
        self.trajectory = tr.Trajectory()

        # Get most recent pose
        self.last_angles = [0.0] + self.controller.getJointPositions(units='rad')
        for i in range(1, 5):
            lo, hi = self.kinematics.joint_limits[i-1]
            self.last_angles[i] = max(lo, min(hi, self.last_angles[i]))
        self.pose = self.controller.getJointPositions()

        # Joint state publishing
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4']
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_state', 10)
        self.joint_state_timer = self.create_timer(0.1, self.publish_joint_state)


    # joint state publisher
    def publish_joint_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.controller.getJointPositions(units='rad')
        self.joint_state_publisher.publish(msg)


    # Common poses
    def rest(self):
        self.controller.setPosition([0, -30, 120, -1])
    def stand(self):
        self.controller.setPosition([0, 0, 0, 90])
    def sleep(self):
        self.rest()
        time.sleep(2)
        self.controller.setPosition([0, -30, 120, -110], speed=1000)
        time.sleep(.5)
        self.controller.setPosition([0, 75, 90, -110], speed=300)

    

def main(args=None):
    rclpy.init(args=args)
    cobot = Cobot()
    cobot.rest()
    rclpy.spin(cobot)
    cobot.destroy_node()
    rclpy.shutdown
    cobot.sleep()


if __name__ == "__main__":
    main()
    