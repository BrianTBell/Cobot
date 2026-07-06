import controllers.joint_controller as jc
import kinematics.ik_solver as ik
import trajectory.planner as tr

from pynput import keyboard
from pynput.keyboard import Key, Controller

import time
import math

class Cobot:
    def __init__(self):
        self.controller = jc.JointController()
        self.kinematics = ik.IKSolver()
        self.trajectory = tr.Trajectory()

        # Default poses
        self.rest_pose = [0, -30, 120, -1]
        self.stand_pose = [0, 0, 0, 90]
        self.sleep_pose_approach = [0, -30, 120, -110]
        self.sleep_pose = [0, 75, 90, -110]

        # Get most recent pose
        self.last_angles = [0.0] + self.controller.getJointPositions(units='rad')
        for i in range(1, 5):
            lo, hi = self.kinematics.joint_limits[i-1]
            self.last_angles[i] = max(lo, min(hi, self.last_angles[i]))
        self.pose = self.controller.getJointPositions


    def rest(self):
        self.controller.setPosition(self.rest_pose)
    def stand(self):
        self.controller.setPosition(self.stand_pose)
    def sleep(self):
        self.controller.setPosition(self.rest_pose)
        time.sleep(2)
        self.controller.setPosition(self.sleep_pose_approach, speed=1000)
        time.sleep(.5)
        self.controller.setPosition(self.sleep_pose, speed=300)


if __name__ == "__main__":
   cobot = Cobot()
   cobot.rest()
   cobot.sleep()
   #time.sleep(3)
   #cobot.stand()
