"""Inverse kinematics solver implementation placeholder."""

from ikpy.chain import Chain
import random as rand
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import utilities as utility


class IKSolver:
    def __init__(self):
        urdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "cobot_description", "urdf", "Cobot.urdf")
        self.chain = Chain.from_urdf_file(urdf_path, active_links_mask=[False, True, True, True, True])
        self.joint_limits = utility.load_joint_limits()

    def forwardKinematics(self, angles):
        fk = self.chain.forward_kinematics(angles)
        pos = fk[:3, 3]
        rounded_pose = [float(round(num, 4)) for num in pos] 
        return rounded_pose

    def inverseKinematics(self, target_position, initial_position=None, tolerance=1e-3, max_attempts=10):

        # do not let target pos go below table
        if target_position[2] <= 0.010: target_position[2] = 0.01

        for attempt in range(max_attempts):
            if attempt == 0 and initial_position is not None:
                # stay close to the caller-supplied starting pose first, to avoid large joint jumps
                guess = initial_position
            else:
                guess = [0, 0, 0, 0, 0]
                for i in range(1, 5):
                    joint_min = self.joint_limits[i-1][0]
                    joint_max = self.joint_limits[i-1][1]
                    guess[i] = rand.uniform(joint_min, joint_max)

            angles = self.chain.inverse_kinematics(target_position, initial_position=guess)
            achieved = self.forwardKinematics(angles)
            error = sum((a - b) ** 2 for a, b in zip(achieved, target_position)) ** 0.5
            if error <= tolerance:
                return angles

        raise ValueError(f"IK did not converge after {max_attempts} attempts: target={target_position}, achieved={achieved}")

        
if __name__ == "__main__":
    target_position = [0.1, 0.2, 0.3]
    ik = IKSolver()
    ik.inverseKinematics(target_position)