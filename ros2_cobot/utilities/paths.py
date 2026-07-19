"""Shared path constants, computed relative to this file's location so
nothing breaks when the repo lives at a different path on a different
machine."""

from pathlib import Path

UTILITIES_DIR = Path(__file__).resolve().parent   # .../ros2_cobot/utilities
PROJECT_ROOT = UTILITIES_DIR.parent             # .../ros2_cobot

USD_PATH = PROJECT_ROOT / "src" / "cobot_description" / "usd" /"Cobot.usd"
ISAACLAB_RUNS_DIR = PROJECT_ROOT / "isaacLab" / "runs"
BUFFER_SAVE_PATH = PROJECT_ROOT / "src" / "cobot_imol" / "babble_buffer"

