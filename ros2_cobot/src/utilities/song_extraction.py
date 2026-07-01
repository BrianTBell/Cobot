"""
Used to extract observations from music on disk for dance RL.
"""

import librosa
import numpy as np


class SongExtraction:
    def __init__(self, song_path):
        ##
        # Get basic beat params
        ##

        self.song_path = song_path

        # Get the waveform 'y' and sampling rate 'sr'
        y, sr = librosa.load(self.song_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        ##
        # Get normalized DB from different frequency bands
        ##

        hop_length = 512  # shared across STFT and beat tracking so all frame counts align

        # Full-frequency power spectrogram — shape (freq_bins, n_frames)
        S = np.abs(librosa.stft(y, hop_length=hop_length))**2

        freqs = librosa.fft_frequencies(sr=sr)

        bands = {
            "bass": (20,   250),   # kick drum and sub-bass
            "mid":  (250,  4000),  # melody and vocals
            "high": (4000, 12000), # cymbals and air
        }

        db = {}
        for name, (lo, hi) in bands.items():
            band = S[(freqs >= lo) & (freqs < hi)]  # (freq_bins_in_band, n_frames)
            band_power = band.mean(axis=0)           # avg across freq bins → (n_frames,)
            band_db = librosa.power_to_db(band_power, ref=S.max())
            # normalize to 0–1 across the song for bounded RL observations
            db[name] = (band_db - band_db.min()) / (band_db.max() - band_db.min() + 1e-8)


        ##
        #   Get beat phase and confidence
        ##

        # Convert beat frame indices to timestamps in seconds
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

        # Onset strength spikes at rhythmic events (kicks, snares, etc.)
        onset_env  = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

        n_frames    = len(onset_env)
        frame_times = librosa.frames_to_time(np.arange(n_frames), sr=sr, hop_length=hop_length)

        beat_phase = np.zeros(n_frames)
        for i, t in enumerate(frame_times):
            prev = beat_times[beat_times <= t]  # last beat before now
            nxt  = beat_times[beat_times > t]   # next beat coming up
            if len(prev) and len(nxt):
                beat_phase[i] = (t - prev[-1]) / (nxt[0] - prev[-1])  # 0→1 through the beat gap

        beat_confidence = onset_env / (onset_env.max() + 1e-8)  # normalize, avoid div/0

        self.beat_info = [beat_phase, beat_confidence, db]

    
    def __str__(self):
        return f"Filename: {self.song_path}\nBeat Information:\n{self.beat_info}"
    


if __name__ == "__main__":

    filename = "/home/brian/Music/Oh! Darling (Remastered 2009).mp3"
    song = SongExtraction(filename)
    info = song.beat_info
    print(f"Beat Phase:{info[0][100:120]}")
    print(f"Beat Confidence:{info[1][100:120]}")
    print(f"Low DB: {info[2]['bass']}")
    print(f"Mid DB: {info[2]['mid']}")
    print(f"High DB: {info[2]['high']}")
