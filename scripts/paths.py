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