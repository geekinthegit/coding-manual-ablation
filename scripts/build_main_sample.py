"""Draw the main-experiment sample of 300 target utterances (Roadmap 12).

Basis: decisions/02-3-sampling-design.md line 11 (simple random sampling
without replacement, n = 300, the same 300 utterances in every condition;
seed and script retained in the repository) and line 13 (revision note of
2026-09-23: the sampling frame is the eligible target population minus the
development targets D of 5.7.2, 150,644 - 17 = 150,627; D is excluded at
the target level only, the sample is drawn from the reduced frame, not
drawn first and then replaced on overlap); decisions/05-7-tool-validation.md
5.7.2 (D = 17 utterances in samples/dev_targets.csv).

Inputs are read exactly as scripts/build_dev_targets.py reads them
(pd.read_csv(path, keep_default_na=False, na_values=[""])), eligibility is
decided with the same is_true() test on the `eligible` column, and ids are
cast to int and sorted ascending before the draw.

Reproducibility conditions: the same data/frame.csv (sha256 in the
manifest), the same samples/dev_targets.csv (sha256 in the manifest), the
same --seed, numpy.random.Generator(numpy.random.PCG64(seed)), the same
NumPy version (recorded in the manifest; the bit-generator stream is not
guaranteed across NumPy versions) and the same choice call
(size=300, replace=False, shuffle=True) reproduce the same 300 ids. The seed
is a command-line argument; no seed value is stored in this file.

Outputs (never overwritten; the script stops if either exists):
* samples/main_targets.csv                    one column source_id, ascending
* reports/main-sample-manifest-<date>.json    inputs, hashes, rule, seed, rng,
                                              choice settings, versions, commits,
                                              output hash, post-draw checks

Usage (repository root, conda base, clean working tree):
    python scripts/build_main_sample.py --seed <int> --date YYYY-MM-DD
"""

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from build_dev_targets import is_true
from paths import DEV_TARGETS_FILE, FRAME_FILE, MAIN_TARGETS_FILE, REPO_ROOT, REPORTS_DIR
from run_experiment import sha256_file

N_SAMPLE = 300                    # 02-3:11
EXPECTED_FRAME_SIZE = 150_627     # 02-3:13: 150,644 eligible - 17 development targets
FREEZE_COMMIT = "ed13ec2"         # reports/protocol-freeze-record-2026-09-24.md
SAMPLING_RULE = ("SRS without replacement, n=300, from eligible population minus development "
                 "targets D (02-3 revision note 2026-09-23)")
OUTPUT_COLUMN = "source_id"


class SampleError(Exception):
    """A precondition or post-draw check failed; nothing was written."""


def git_status_porcelain() -> str:
    return subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                          capture_output=True, text=True, check=True).stdout


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()


def require_clean_tree(status: str) -> None:
    """Step 1: refuse to run when `git status --porcelain` output is not empty."""
    if status.strip():
        dirty = [ln for ln in status.splitlines() if ln.strip()]
        raise SampleError("working tree is not clean; nothing written. Dirty entries:\n  " + "\n  ".join(dirty))


def read_inputs(frame_path: Path, dev_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Step 2: read frame.csv and dev_targets.csv as build_dev_targets.py does (only "" is missing)."""
    frame = pd.read_csv(frame_path, keep_default_na=False, na_values=[""])
    dev = pd.read_csv(dev_path, keep_default_na=False, na_values=[""])
    return frame, dev


def eligible_ids(frame: pd.DataFrame) -> set[int]:
    """Step 3: source_ids of eligible rows (is_true on `eligible`, cast to int), as in build_dev_targets."""
    return set(int(x) for x in frame.loc[is_true(frame["eligible"]), OUTPUT_COLUMN].astype(int))


def dev_ids(dev: pd.DataFrame) -> set[int]:
    """Step 3: development-target source_ids cast to int (5.7.2)."""
    return set(int(x) for x in dev[OUTPUT_COLUMN].astype(int))


def reduced_frame(eligible: set[int], dev: set[int], expected_size: int = EXPECTED_FRAME_SIZE) -> list[int]:
    """Step 4: eligible minus D, sorted ascending as Python ints (02-3:13).

    Raises SampleError when the size differs from expected_size.
    """
    frame_ids = sorted(int(s) for s in eligible - dev)
    if len(frame_ids) != expected_size:
        raise SampleError(f"sampling frame has {len(frame_ids)} ids, expected {expected_size}; nothing written")
    return frame_ids


def draw(frame_ids: list[int], seed: int, n: int = N_SAMPLE) -> list[int]:
    """Steps 5-6: SRS without replacement of n ids from frame_ids (02-3:11).

    The generator is an explicit PCG64 bit generator seeded with `seed`; the
    ids are drawn with one choice call whose arguments are all explicit.
    """
    rng = np.random.Generator(np.random.PCG64(seed))
    drawn = rng.choice(frame_ids, size=n, replace=False, shuffle=True)
    return [int(x) for x in drawn]


def post_checks(drawn: list[int], eligible: set[int], dev: set[int], n: int = N_SAMPLE) -> dict[str, bool]:
    """Step 7: the four post-draw checks, by name."""
    return {
        "len_drawn_equals_n": len(drawn) == n,
        "drawn_ids_unique": len(set(drawn)) == n,
        "drawn_subset_of_eligible": set(drawn) <= eligible,
        "drawn_disjoint_from_dev_targets": not (set(drawn) & dev),
    }


def require_checks(checks: dict[str, bool]) -> None:
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise SampleError(f"post-draw checks failed: {failed}; nothing written")


def write_targets(drawn: list[int], out_path: Path) -> None:
    """Step 8: main_targets.csv with one column source_id, ascending; never overwrites."""
    if out_path.exists():
        raise SampleError(f"{out_path} already exists; not overwritten")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({OUTPUT_COLUMN: sorted(int(x) for x in drawn)}).to_csv(out_path, index=False)


def write_manifest(manifest: dict, manifest_path: Path) -> None:
    """Step 9: the sample manifest as JSON; never overwrites."""
    if manifest_path.exists():
        raise SampleError(f"{manifest_path} already exists; not overwritten")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run(seed: int, date: str, *, frame_path: Path = FRAME_FILE, dev_path: Path = DEV_TARGETS_FILE,
        out_path: Path = MAIN_TARGETS_FILE, manifest_dir: Path = REPORTS_DIR,
        expected_frame_size: int = EXPECTED_FRAME_SIZE, n: int = N_SAMPLE,
        status_fn=git_status_porcelain, head_fn=git_head, script_path: Path | None = None) -> dict:
    """Steps 1-9 in order; returns the manifest. Raises SampleError before any write on failure."""
    require_clean_tree(status_fn())
    manifest_path = manifest_dir / f"main-sample-manifest-{date}.json"
    if out_path.exists():
        raise SampleError(f"{out_path} already exists; not overwritten")
    if manifest_path.exists():
        raise SampleError(f"{manifest_path} already exists; not overwritten")

    frame, dev = read_inputs(frame_path, dev_path)
    eligible = eligible_ids(frame)
    dev_set = dev_ids(dev)
    dev_not_eligible = sorted(dev_set - eligible)
    frame_ids = reduced_frame(eligible, dev_set, expected_frame_size)
    drawn = draw(frame_ids, seed, n)
    checks = post_checks(drawn, eligible, dev_set, n)
    require_checks(checks)

    write_targets(drawn, out_path)
    script_path = Path(script_path or __file__).resolve()
    manifest = {
        "frame_file": str(frame_path), "frame_sha256": sha256_file(frame_path),
        "dev_targets_file": str(dev_path), "dev_targets_sha256": sha256_file(dev_path),
        "dev_targets_count": len(dev_set),
        "dev_targets_not_in_eligible": dev_not_eligible,
        "eligible_count": len(eligible), "frame_size": len(frame_ids),
        "sampling_rule": SAMPLING_RULE,
        "seed": seed,
        "rng": {"generator": "numpy.random.Generator", "bit_generator": "PCG64"},
        "choice": {"size": n, "replace": False, "shuffle": True},
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "freeze_commit": FREEZE_COMMIT,
        "script_path": str(script_path.relative_to(REPO_ROOT)) if script_path.is_relative_to(REPO_ROOT) else str(script_path),
        "script_sha256": sha256_file(script_path),
        "run_commit": head_fn(), "working_tree_clean": True,
        "output_file": str(out_path), "output_sha256": sha256_file(out_path), "output_count": len(drawn),
        "checks": checks,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_manifest(manifest, manifest_path)
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Draw the 300-utterance main sample (02-3).")
    ap.add_argument("--seed", type=int, required=True, help="PCG64 seed (no default)")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD, used in the manifest file name")
    args = ap.parse_args(argv)
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"--date must be YYYY-MM-DD, got {args.date!r}", file=sys.stderr)
        return 1
    try:
        m = run(args.seed, args.date)
    except SampleError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"frame_size: {m['frame_size']}")
    print(f"seed: {m['seed']}")
    print(f"output_sha256: {m['output_sha256']}")
    print(f"manifest: {m['manifest_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
