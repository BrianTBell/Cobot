"""
OU Noise... this makes the arm explore explore / babble in a smooth sweeping motion rather
than eratically jitter.
"""

import numpy as np

class OUNoise:
    def __init__(self, joint_limits, mu=0.5, theta=0.02, sigma=0.06, dt=1 / 60, seed=None):
        # Adjust sigma to play with volatility
        self.joint_limits = np.asarray(joint_limits, dtype=np.float64)  # (N, 2) = [(min_rad, max_rad), ...]
        self.size = len(self.joint_limits)  # The number of OU processes running in parallel, four for my cobot arm
        self. mu = mu
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.rng = np.random.default_rng(seed)
        self.state = np.full(self.size, mu, dtype=np.float64)


    def reset(self):
        self.state = np.full(self.size, self.mu, dtype=np.float64)


    def sample(self):
        noise = self.rng.normal(size=self.size)
        # The OU equation that creates smooth exploration rather than random jitter
        dx = self.theta * (self.mu - self.state) * self.dt + self.sigma * np.sqrt(self.dt) * noise
        self.state += dx
        # state is an internal [0, 1] fraction; clip before mapping to real joint angles
        self.state = np.clip(self.state, 0.0, 1.0)

        min_rad = self.joint_limits[:, 0]
        max_rad = self.joint_limits[:, 1]
        return min_rad + self.state * (max_rad - min_rad)


if __name__ == "__main__":
    joint_limits = [(-3.14, 3.14), (-1.48, 1.48), (-2.09, 2.09), (-1.92, 1.92)]
    ou = OUNoise(joint_limits)
    for i in range (500):
        print(f"OU sample {i} = {ou.sample()}")
