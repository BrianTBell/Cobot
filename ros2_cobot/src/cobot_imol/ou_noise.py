"""
OU Noise... this makes the arm explore explore / babble in a smooth sweeping motion rather 
than eratically jitter.
"""

import numpy as np 

class OUNoise:
    def __init__(self, size, mu=0.0, theta=0.15, sigma=0.2, dt=1e-2, seed=None):
        self.size = size # The number of OU processes running in parallel, four for my cobot arm
        self. mu = mu
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.rng = np.random.default_rng(seed)
        self.state = np.full(size, mu, dtype=np.float64)


    def reset(self):
        self.state = np.full(self.size, self.mu, dtype=np.float64)

    
    def sample(self):
        noise = self.rng.normal(size=self.size)
        # The OU equation that creates smooth exploration rather than random jitter
        dx = self.theta * (self.mu - self.state) * self.dt + self.sigma * np.sqrt(self.dt) * noise
        self.state += dx
        return self.state.copy()


if __name__ == "__main__":
    joint_count = 4
    ou = OUNoise(joint_count)
    for i in range (50):
        print(f"OU sample {i} = {ou.sample()}")
