"""Joint-space trajectory execution: solves IK per waypoint, interpolates joint angles between them."""

import math
import time
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import controllers.joint_controller as jc
import kinematics.ik_solver as ik


class Trajectory:
    def __init__(self):
        self.controller = jc.JointController()
        self.kinematics = ik.IKSolver()
        self.last_angles = [0.0] + self.controller.getJointPositions(units='rad')
        for i in range(1, 5):
            lo, hi = self.kinematics.chain.links[i].bounds
            self.last_angles[i] = max(lo, min(hi, self.last_angles[i]))

    def getPose(self):
        angles = [0.0] + self.controller.getJointPositions(units='rad')
        return self.kinematics.forwardKinematics(angles)

    def moveTo(self, pose, **kwargs):
        return self.moveThrough([pose], **kwargs)

    def moveThrough(self, waypoints, max_step_rad=0.05, step_delay=0.05, tolerance=1e-2, wait=True):
        # solve IK once per waypoint, each warm-started from the previous solution
        solved = []
        guess = self.last_angles
        for pose in waypoints:
            angles = self.kinematics.inverseKinematics(pose, initial_position=guess)
            solved.append(angles)
            guess = angles
        self.last_angles = solved[-1]

        # interpolate joint angles between consecutive solved waypoints and stream commands
        current = [0.0] + self.controller.getJointPositions(units='rad')
        path = [current] + solved
        for start, end in zip(path, path[1:]):
            distance = max(abs(end[i] - start[i]) for i in range(len(start)))
            steps = max(2, round(distance / max_step_rad))
            for step in range(1, steps + 1):
                t = step / steps
                t_smooth = 3 * t ** 2 - 2 * t ** 3  # ease in/out: zero velocity at each segment's ends
                interp = [start[i] + (end[i] - start[i]) * t_smooth for i in range(len(start))]
                self.controller.setPosition([math.degrees(a) for a in interp[1:]])
                time.sleep(step_delay)

        if not wait:
            return

        target = solved[-1]
        iter, max_iter = 0, 500
        while True:
            time.sleep(0.1)
            current = [0.0] + self.controller.getJointPositions(units='rad')
            error = sum((a - b) ** 2 for a, b in zip(current[1:], target[1:])) ** 0.5
            if error <= tolerance:
                break
            if iter >= max_iter:
                print("Could not complete movement to position")
                break
            iter += 1


if __name__ == "__main__":
    tr = Trajectory()
    #tr.moveTo([-0.0073, -0.0563, 0.3321])

    waypoints = [
        [-0.075, -0.075, 0.30],
        [0.075, -0.075, 0.45],
        [-0.075, -0.075, 0.45],
        [0.075, -0.075, 0.30],
        [-0.075, -0.075, 0.30]
    ]

    tr.moveThrough(waypoints)