import os
from pathlib import Path

_env = os.environ.get("TALKMOVES_DIR")
if _env is None:
    raise EnvironmentError(
        "Set TALKMOVES_DIR to the local clone of SumnerLab/TalkMoves."
    )

TALKMOVES_DIR = Path(_env)
TRAIN_FILE = TALKMOVES_DIR / "data" / "train_data_504.xlsx"
TEST_FILE = TALKMOVES_DIR / "data" / "test_data_63.xlsx"


# Experiment repository paths (independent of TALKMOVES_DIR).
REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAL_FILE = REPO_ROOT / "manual" / "chapter1.txt"

# Derived data files written by build_frame.py (git-ignored under data/).
DATA_DIR = REPO_ROOT / "data"
FRAME_FILE = DATA_DIR / "frame.csv"
SCORING_LABELS_FILE = DATA_DIR / "scoring_labels.csv"

# Sampled target lists and reports (committed).
SAMPLES_DIR = REPO_ROOT / "samples"
DEV_TARGETS_FILE = SAMPLES_DIR / "dev_targets.csv"
MAIN_TARGETS_FILE = SAMPLES_DIR / "main_targets.csv"
REPORTS_DIR = REPO_ROOT / "reports"
