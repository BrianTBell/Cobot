"""Shared path constants, computed relative to this file's location so
nothing breaks when the repo lives at a different path on a different
machine."""

from pathlib import Path

UTILITIES_DIR = Path(__file__).resolve().parent   # .../ros2_cobot/utilities
ROS2_COBOT_DIR = UTILITIES_DIR.parent             # .../ros2_cobot

USD_PATH = ROS2_COBOT_DIR / "src" / "usd" / "Cobot.usd"
ISAACLAB_RUNS_DIR = ROS2_COBOT_DIR / "isaacLab" / "runs"
BUFFER_SAVE_PATH = ROS2_COBOT_DIR / "src" / "cobot_imol" / "babble_buffer"
