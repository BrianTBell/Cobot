"""
Fixed-capacity ring buffer storing (obs, action, next_obs) transitions from
babbling, for later offline world-model training. In-memory only -- fine for
early sim phases per the project plan; disk-backed + reservoir sampling comes
later once always-on real-hardware operation needs long-horizon retention.

DreamerV3's world model is recurrent, so it trains on contiguous sequences of
transitions rather than i.i.d. single steps. sample_sequences() guarantees
each sampled chunk is temporally unbroken: it never crosses an episode reset
(tracked via `done`) or the ring buffer's oldest/newest seam (the point where
`ptr` is about to overwrite the oldest surviving entry).
"""

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity, obs_dim, action_dim):
        self.capacity = capacity
        self.obs = np.zeros((capacity, obs_dim), dtype=np.float64)
        self.actions = np.zeros((capacity, action_dim), dtype=np.float64)
        self.next_obs = np.zeros((capacity, obs_dim), dtype=np.float64)
        self.done = np.zeros(capacity, dtype=bool)
        self.ptr = 0
        self.size = 0  # how many valid entries so far (<= capacity)


    def add(self, obs, action, next_obs, done=False):
        self.obs[self.ptr] = obs
        self.actions[self.ptr] = action
        self.next_obs[self.ptr] = next_obs
        self.done[self.ptr] = done
        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)


    def sample_sequences(self, batch_size, seq_len):
        """Sample `batch_size` chunks of `seq_len` consecutive transitions.
        Each chunk is guaranteed contiguous: no episode reset and no ring-buffer
        wraparound seam inside it. Shapes: (batch_size, seq_len, dim)."""
        if self.size < seq_len:
            raise ValueError(f"buffer only has {self.size} transitions, need at least seq_len={seq_len}")

        full = self.size == self.capacity
        newest = (self.ptr - 1) % self.capacity if full else None

        obs_batch = np.empty((batch_size, seq_len, self.obs.shape[1]), dtype=np.float64)
        action_batch = np.empty((batch_size, seq_len, self.actions.shape[1]), dtype=np.float64)
        next_obs_batch = np.empty((batch_size, seq_len, self.obs.shape[1]), dtype=np.float64)

        for b in range(batch_size):
            while True:
                if full:
                    start = np.random.randint(0, self.capacity)
                else:
                    start = np.random.randint(0, self.size - seq_len + 1)
                idx = (start + np.arange(seq_len)) % self.capacity

                # a chunk is broken if any step before the last one ends an
                # episode, or is the newest entry (whose "successor" in raw
                # array order is actually the oldest one, about to be overwritten)
                broken = self.done[idx[:-1]].any()
                if full and newest in idx[:-1]:
                    broken = True

                if not broken:
                    break

            obs_batch[b] = self.obs[idx]
            action_batch[b] = self.actions[idx]
            next_obs_batch[b] = self.next_obs[idx]

        return obs_batch, action_batch, next_obs_batch


    def save(self, path):
        np.savez(
            path,
            obs=self.obs, actions=self.actions, next_obs=self.next_obs, done=self.done,
            ptr=self.ptr, size=self.size, capacity=self.capacity,
        )


    @classmethod
    def load(cls, path):
        data = np.load(path)
        buf = cls(
            capacity=int(data["capacity"]),
            obs_dim=data["obs"].shape[1],
            action_dim=data["actions"].shape[1],
        )
        buf.obs = data["obs"]
        buf.actions = data["actions"]
        buf.next_obs = data["next_obs"]
        buf.done = data["done"]
        buf.ptr = int(data["ptr"])
        buf.size = int(data["size"])
        return buf



if __name__ == "__main__":
    buf = ReplayBuffer(capacity=10, obs_dim=4, action_dim=4)

    for i in range(15):
        fake_obs = np.full(4, i)
        fake_action = np.full(4, i)
        fake_next_obs = np.full(4, i + 1)
        done = (i % 4 == 3)  # fake an episode boundary every 4 steps
        buf.add(fake_obs, fake_action, fake_next_obs, done=done)

    print("size after 15 adds into capacity=10:", buf.size)
    print("done flags:", buf.done)

    obs_batch, action_batch, next_obs_batch = buf.sample_sequences(batch_size=3, seq_len=3)
    print("obs_batch shape:", obs_batch.shape)
    print("obs_batch:\n", obs_batch)
