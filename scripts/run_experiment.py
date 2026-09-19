"""Execution runner: scheduling, API calls, run records, resume (Decision Log 5.6).

What is fixed elsewhere and only reused here
--------------------------------------------
* Request structure: test_api_request.build_request (5.3); the schema is
  imported, never duplicated.
* Prompt text: build_inputs.build_prompt (5.1 / 5.3.3).
* Validity, invalid_reason order, 429 classification: validation.py (5.4, 5.6.7).
* Aggregation and the pass 2 tie list: parse_attempts.py (5.4, 5.6.8).

What this module implements (5.6)
---------------------------------
* 5.6.1 blocks by repeat, seeded within-block shuffle, block boundary.
* 5.6.2 / 5.6.3 manifest_passN.json and prompts.jsonl before any call; pass 2
  (repeat 4) and pass 3 (repeat 5) are built from the tie_pending rows of
  final_labels.csv written by parse_attempts.py.
* 5.6.4 worker pool, max_retries=0 client, Retry-After / backoff waits,
  retry_after_exceeds_max stop.
* 5.6.5 completed_seq, consecutive-failure counter, sticky stop state,
  run_stopped event.
* 5.6.6 resume from the attempts file only, resume verification, run.lock.
* 5.6.7 append-only JSONL with flush + fsync under one lock; --repair.

The API key is read from OPENAI_API_KEY_ABLATION and is never printed or
written to any record.

Usage (repository root, conda base):
    python scripts/run_experiment.py --run-id pilot01 --pass 1 --input data/sample.csv \
        --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 \
        --failure-threshold 10 [--dry-run]
    python scripts/run_experiment.py --run-id pilot01 --pass 1 --resume
    python scripts/run_experiment.py --run-id pilot01 --pass 1 --repair
    python scripts/run_experiment.py --run-id pilot01 --pass 2 [--dry-run]
    python scripts/run_experiment.py --run-id pilot01 --pass 3 [--dry-run]
"""

import argparse
import hashlib
import json
import os
import platform
import random
import shutil
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from build_inputs import CONDITIONS, REPO_ROOT, build_prompt, git_commit_hash
from parse_attempts import (
    R_PLANNED, CorruptedFile, TruncatedLastLine, final_rows, labels_from_records,
    parse_run, read_jsonl_strict, tie_pending_pairs,
)
from test_api_request import MODEL, request_params
from validation import (
    classify_http_status, error_code_from_body, error_type_from_body, parse_retry_after,
    validate_body,
)

RUNS_DIR = REPO_ROOT / "runs"
MAX_ATTEMPTS = 3                                          # 5.4.7
PASS_SEEDS = {1: 20260918, 2: 20260919, 3: 20260920}      # 5.6.1
PASS_REPEAT = {2: R_PLANNED + 1, 3: R_PLANNED + 2}        # tie-break repeats 4 and 5 (5.4.3)
STOP_REASONS = ("failure_threshold", "fatal_error", "retry_after_exceeds_max")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="microseconds")


def from_iso(text: str) -> datetime:
    return datetime.fromisoformat(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_ids(path: Path) -> list[int]:
    """Utterance ids (source_id column) in file order; must be unique."""
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    ids = [int(x) for x in df["source_id"]]
    assert len(ids) == len(set(ids)), "duplicate source_id in input file"
    return ids


class Refused(Exception):
    """The runner refuses to proceed; the message says why."""


@dataclass(frozen=True)
class Settings:
    concurrency: int
    timeout: float
    backoff_initial: float
    backoff_max: float
    failure_threshold: int

    def as_manifest(self) -> dict:
        """The settings as the manifest records them (5.6.2).

        5.6.4 leaves timeout, the backoff values and the failure threshold to
        the pilot and gives the runner no defaults, so the values a pass ran
        under are recoverable only from its manifest. max_retries = 0 is
        recorded although it is not a Settings field, because 5.6.4 requires the
        SDK's own retrying to be off: every attempt must be one this runner
        decided on and wrote a record for. The jitter formula is spelled out
        instead of named so the manifest stays readable without this source file.
        """
        return {
            "sdk_settings": {"max_retries": 0, "timeout": self.timeout},
            "concurrency": self.concurrency,
            "failure_threshold": self.failure_threshold,
            "backoff": {"initial": self.backoff_initial, "max": self.backoff_max,
                        "jitter": "equal: base/2 + U(0, base/2), base = initial*2^(attempt-1) capped at max"},
        }

    @classmethod
    def from_manifest(cls, m: dict) -> "Settings":
        """The settings a pass started under, read back for resume (5.6.6).

        Resume compares the values given on the command line against these.
        5.6.4 fixes the operational values for the whole pass, so a resume that
        quietly adopted new ones would leave the manifest an inaccurate record
        of how part of the attempts file was produced.
        """
        return cls(int(m["concurrency"]), float(m["sdk_settings"]["timeout"]),
                   float(m["backoff"]["initial"]), float(m["backoff"]["max"]),
                   int(m["failure_threshold"]))


# --------------------------------------------------------------------------
# Planning (5.6.1), prompts (5.6.3), manifests (5.6.2)
# --------------------------------------------------------------------------

def plan_pass1(ids: list[int], seed: int) -> list[dict]:
    """Ordered pass 1 call list: one block per repeat, shuffled within (5.6.1).

    5.6.1 blocks by repeat instead of shuffling all calls at once so that a run
    interrupted at any point still leaves complete "all utterances x all
    conditions" units for the repeats that finished, and so that every condition
    stays interleaved within each period of execution time. order_index runs
    across the concatenated blocks and is what the records refer to; the seed is
    stored too, but 5.6.2 makes the stored list, not the seed, the reference for
    reproduction.
    """
    pairs = [(uid, cond) for uid in ids for cond in CONDITIONS]
    rng = random.Random(seed)
    calls: list[dict] = []
    for repeat in range(1, R_PLANNED + 1):
        block = list(pairs)
        rng.shuffle(block)
        for uid, cond in block:
            calls.append({"order_index": len(calls), "utterance_id": uid,
                          "condition": cond, "repeat": repeat})
    return calls


def plan_tiebreak(pairs: list[tuple[int, str]], pass_no: int) -> list[dict]:
    """Ordered tie-break call list for pass 2 or pass 3 (5.6.1, 5.4.3).

    A single block, because a tie-break pass carries exactly one repeat under
    5.4.3 (4 for pass 2, 5 for pass 3). The pairs are sorted before the seeded
    shuffle so the order is a function of the seed and the set of tied pairs
    alone, not of the order the caller happened to collect them in; 5.6.6
    check 1 recomputes this list and compares it with the manifest, which only
    works if the result is reproducible.
    """
    block = sorted(pairs)
    random.Random(PASS_SEEDS[pass_no]).shuffle(block)
    return [{"order_index": i, "utterance_id": uid, "condition": cond, "repeat": PASS_REPEAT[pass_no]}
            for i, (uid, cond) in enumerate(block)]


def write_prompts(path: Path, pairs: list[tuple[int, str]], builder=build_prompt) -> dict:
    """Write prompts.jsonl and return {(uid, cond): (prompt, sha)} (5.6.3).

    5.6.3 keeps the complete user message exactly as sent, once per unique
    (utterance, condition) pair, so attempt records need carry only
    prompt_sha256 while the text stays recoverable. Pairs are sorted and
    de-duplicated so the file is a function of the pair set alone: execution
    order belongs to the manifest call list (5.6.1), and pass 2 and pass 3 reuse
    this same file rather than rebuilding prompts.
    """
    out: dict[tuple[int, str], tuple[str, str]] = {}
    with path.open("w", encoding="utf-8") as f:
        for uid, cond in sorted(set(pairs)):
            prompt = builder(uid, cond)
            sha = sha256_text(prompt)
            f.write(json.dumps({"utterance_id": uid, "condition": cond, "prompt": prompt,
                                "prompt_sha256": sha}, ensure_ascii=False) + "\n")
            out[(uid, cond)] = (prompt, sha)
    return out


def load_prompts(path: Path) -> dict:
    """Read prompts.jsonl, recomputing every sha256 (5.6.6 check 2)."""
    out = {}
    for rec in read_jsonl_strict(path):
        key = (int(rec["utterance_id"]), rec["condition"])
        if sha256_text(rec["prompt"]) != rec["prompt_sha256"]:
            raise Refused(f"prompts.jsonl: sha256 mismatch for {key}")
        if key in out:
            raise Refused(f"prompts.jsonl: duplicate entry for {key}")
        out[key] = (rec["prompt"], rec["prompt_sha256"])
    return out


def environment_record() -> dict:
    """Git commit and interpreter versions for the manifest (5.6.2).

    5.6.2 records the runner commit and the openai and Python versions with
    every pass, and 5.6.6 check 5 refuses a resume whose commit differs or whose
    working tree is dirty. Together these are what tie a set of attempt records
    to the code that produced them.
    """
    import openai  # local import: parse/validation paths do not need the SDK
    return {"git_commit": git_commit_hash(), "openai_version": openai.__version__,
            "python_version": platform.python_version()}


def build_manifest(run_id: str, pass_no: int, calls: list[dict], settings: Settings,
                   prompts_sha: str, input_file: Path, input_sha: str, extra: dict | None = None) -> dict:
    """Assemble manifest_pass{N}.json (5.6.2).

    Carries everything 5.6.6 verifies before a resume: model, request_params and
    the ordered call list (check 1), the prompts file sha256 (check 2), the
    input file path and sha256 (check 4) and the environment (check 5). `extra`
    holds the fields only tie-break manifests have, namely the previous pass's
    attempts sha256, the final_labels.csv sha256 and the parser commit, which is
    what makes the tie selection of pass 2 and pass 3 reproducible. `calls` is
    added last so the long ordered list ends the file and the settings stay
    visible at the top.
    """
    m = {
        "run_id": run_id, "pass": pass_no, "created_at": iso(utc_now()),
        "seed": PASS_SEEDS[pass_no], "model": MODEL, "request_params": request_params(),
        **settings.as_manifest(),
        "prompts_sha256": prompts_sha,
        "input_file": {"path": str(input_file), "sha256": input_sha},
        **environment_record(),
        "n_calls": len(calls),
    }
    if extra:
        m.update(extra)
    m["calls"] = calls
    return m


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def manifest_pairs(manifest: dict) -> set[tuple[int, str]]:
    return {(int(c["utterance_id"]), c["condition"]) for c in manifest["calls"]}


# --------------------------------------------------------------------------
# Resume computation (5.6.6)
# --------------------------------------------------------------------------

@dataclass
class CallState:
    next_attempt: int = 1
    has_success: bool = False
    terminated: bool = False
    last_completed: dict | None = None      # most recent attempt_completed
    prev_completed_at: str | None = None    # completed_at of attempt next_attempt-1, if it completed


def scan_attempts(records: list[dict], calls: list[dict]) -> tuple[dict[int, CallState], int]:
    """Per-call resume state and the highest completed_seq (5.6.6).

    5.6.6 makes a pass's attempts file the single source of progress; there is
    no checkpoint, so the state is rebuilt by reading the records. An attempt is
    consumed as soon as attempt_started is durably on disk, so next_attempt
    counts started and completed attempts alike: an interrupted attempt is never
    reissued under its own number, and whether that request reached the server
    is deliberately not assessed. A call is terminated by a success or by
    reaching the attempt cap (5.4.7).

    An order_index absent from the manifest means the attempts file and the
    manifest belong to different plans, which 5.6.6 treats as a failed resume
    rather than something to skip over.
    """
    states = {c["order_index"]: CallState() for c in calls}
    started: dict[int, set[int]] = {c["order_index"]: set() for c in calls}
    completed: dict[int, dict[int, dict]] = {c["order_index"]: {} for c in calls}
    max_seq = 0
    for rec in records:
        ev = rec.get("event")
        if ev not in ("attempt_started", "attempt_completed"):
            continue
        idx = rec["order_index"]
        if idx not in states:
            raise Refused(f"attempts file has order_index {idx} not in manifest")
        if ev == "attempt_started":
            started[idx].add(rec["attempt"])
        else:
            completed[idx][rec["attempt"]] = rec
            max_seq = max(max_seq, rec["completed_seq"])
    for idx, st in states.items():
        used = max(started[idx] | set(completed[idx]), default=0)
        st.next_attempt = used + 1
        st.has_success = any(r["outcome"] == "success" for r in completed[idx].values())
        st.terminated = st.has_success or used >= MAX_ATTEMPTS
        if completed[idx]:
            st.last_completed = max(completed[idx].values(), key=lambda r: r["completed_seq"])
        st.prev_completed_at = completed[idx][used]["completed_at"] if used in completed[idx] else None
    return states, max_seq


# --------------------------------------------------------------------------
# Runner (5.6.4, 5.6.5, 5.6.7)
# --------------------------------------------------------------------------

class Runner:
    def __init__(self, *, run_id: str, pass_no: int, calls: list[dict], prompts: dict,
                 client, settings: Settings, attempts_path: Path, states: dict[int, CallState],
                 completed_seq_start: int = 0, rng: random.Random | None = None,
                 sleep=time.sleep, now=utc_now):
        self.run_id, self.pass_no = run_id, pass_no
        self.calls = {c["order_index"]: c for c in calls}
        self.prompts, self.client, self.settings = prompts, client, settings
        self.states = states
        self.rng = rng or random.Random()
        self.sleep, self.now = sleep, now
        self.params = request_params()

        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.completed_seq = completed_seq_start
        self.consecutive_failures = 0
        self.stopped = False
        self.stop_info: dict | None = None
        self.remaining = [c["order_index"] for c in calls if not states[c["order_index"]].terminated]
        self.in_flight: set[int] = set()
        self.fh = attempts_path.open("ab")

    # ---- record writing: append + flush + fsync, caller holds self.lock ----
    def _append(self, rec: dict) -> None:
        self.fh.write((json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8"))
        self.fh.flush()
        os.fsync(self.fh.fileno())

    def begin_attempt(self, rec: dict) -> bool:
        """Write attempt_started unless stopped (5.6.5). Returns permission."""
        with self.lock:
            if self.stopped:
                return False
            self._append(rec)
            return True

    def record_completed(self, rec: dict, stop_reason: str | None = None) -> int:
        """Write attempt_completed, count failures, decide the stop (5.6.5, 5.6.7).

        5.6.5 requires completed_seq to be assigned and the consecutive-failure
        counter to be evaluated in that same order, so both happen inside the one
        lock 5.6.7 already requires for the append. That is why the counter is
        global rather than per worker: with concurrency, only the write order
        gives a well-defined sequence to count in.

        A stop_reason supplied by the caller (a fatal outcome, or a Retry-After
        above backoff_max) takes precedence over the threshold, and _stop keeps
        whichever reason arrives first, since 5.6.5 makes the stopped state
        sticky for the rest of the session.
        """
        with self.cond:
            self.completed_seq += 1
            rec["completed_seq"] = self.completed_seq
            self._append(rec)
            outcome = rec["outcome"]
            if outcome == "success":
                self.consecutive_failures = 0
            elif outcome in ("retryable_error", "invalid_response"):
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.settings.failure_threshold and stop_reason is None:
                    stop_reason = "failure_threshold"
            if stop_reason is not None:
                self._stop(stop_reason, rec)
            self.cond.notify_all()
            return self.completed_seq

    def _stop(self, reason: str, rec: dict) -> None:
        assert reason in STOP_REASONS, reason
        if not self.stopped:                    # sticky: the first reason stands
            self.stopped = True
            self.stop_info = {"reason": reason, "completed_seq_at_stop": rec["completed_seq"],
                              "triggering": {"order_index": rec["order_index"], "attempt": rec["attempt"]}}

    def write_run_stopped(self) -> dict:
        """Append the run_stopped event that closes a stopped pass (5.6.5).

        5.6.5 has the runner start no new attempts, wait for the in-flight ones
        to be recorded, and only then write this event, so run() writes it after
        the workers have joined rather than the worker that triggered the stop
        writing it immediately. completed_seq_at_stop and the triggering attempt
        come from stop_info, captured when the decision was taken, while
        stopped_at is the time of this write; the two differ by the time the
        in-flight attempts needed to finish.
        """
        with self.lock:
            rec = {"event": "run_stopped", "run_id": self.run_id, "pass": self.pass_no,
                   "stopped_at": iso(self.now()), **self.stop_info}
            self._append(rec)
            return rec

    # ---- scheduling with the block boundary (5.6.1) ----
    def next_call(self) -> dict | None:
        """Take the next call, holding the block boundary of 5.6.1.

        The call list is already in the order 5.6.1 fixes, but with several
        workers a fast one would otherwise start the next repeat block while
        slow calls from the current block are still in flight. That would
        destroy the property the blocking exists for: each repeat is a complete
        unit executed within its own period of time, so that time-of-execution
        effects fall on all conditions alike rather than on one repeat. A worker
        therefore waits while any in-flight call has a lower repeat than the
        next one due.

        Returns None when the run is stopped or the list is exhausted, which is
        how workers learn to exit (5.6.5).
        """
        with self.cond:
            while True:
                if self.stopped or not self.remaining:
                    return None
                call = self.calls[self.remaining[0]]
                if any(self.calls[i]["repeat"] < call["repeat"] for i in self.in_flight):
                    self.cond.wait()
                    continue
                idx = self.remaining.pop(0)
                self.in_flight.add(idx)
                return call

    def finish_call(self, call: dict) -> None:
        with self.cond:
            self.in_flight.discard(call["order_index"])
            self.cond.notify_all()

    def worker(self) -> None:
        while True:
            call = self.next_call()
            if call is None:
                return
            try:
                self.process_call(call)
            finally:
                self.finish_call(call)

    # ---- one call: attempts, waits, retries (5.6.4) ----
    def backoff(self, attempt: int) -> float:
        """Wait before the next attempt, with the equal jitter fixed in 5.6.4.

        5.6.4 specifies both parts: the base is backoff_initial * 2^(attempt-1)
        capped at backoff_max, and the wait is half that base plus a uniform
        draw over the other half, so it lies in [base/2, base]. The random half
        separates workers that failed at the same moment and would otherwise
        retry together; the fixed half keeps a guaranteed minimum distance
        between attempts of the same call.
        """
        base = min(self.settings.backoff_max, self.settings.backoff_initial * 2 ** (attempt - 1))
        return base / 2 + self.rng.random() * base / 2

    def process_call(self, call: dict) -> None:
        """Carry one call to termination: attempts, waits, retries (5.6.4, 5.6.5).

        Implements together the per-call rules the decision log states in
        separate sections: at most MAX_ATTEMPTS attempts per repeat (5.4.7);
        a retry after retryable_error and after invalid_response, which 5.4.6
        treats alike as "no label obtained"; the wait taken from Retry-After
        when 5.6.4 gives a usable one and from backoff() otherwise; and no new
        attempt at all, plus a stop of the run, when Retry-After exceeds
        backoff_max, with the header value recorded unclipped as
        planned_wait_sec. A call ends on a success, on a fatal outcome (5.4.6),
        at the attempt cap, or because the run has stopped (5.6.5).

        planned_wait_sec is written on the attempt that precedes the wait rather
        than on the one that follows it, so that a resume can compute what is
        left of an interrupted wait from the record alone (5.6.6). That
        carried-over remainder is applied once, before this session's first
        attempt for the call.
        """
        idx = call["order_index"]
        st = self.states[idx]
        prompt, prompt_sha = self.prompts[(call["utterance_id"], call["condition"])]
        attempt = st.next_attempt
        prev_completed_at = st.prev_completed_at

        # Remaining wait carried over from the previous session (5.6.6).
        last = st.last_completed
        if last is not None and last.get("planned_wait_sec") is not None:
            remaining = (from_iso(last["completed_at"]).timestamp() + last["planned_wait_sec"]
                         - self.now().timestamp())
            if remaining > 0:
                self.sleep(remaining)

        while attempt <= MAX_ATTEMPTS:
            started_at = self.now()
            actual_wait = (None if prev_completed_at is None
                           else started_at.timestamp() - from_iso(prev_completed_at).timestamp())
            started = {"event": "attempt_started", "run_id": self.run_id, "pass": self.pass_no,
                       "order_index": idx, "utterance_id": call["utterance_id"],
                       "condition": call["condition"], "repeat": call["repeat"], "attempt": attempt,
                       "started_at": iso(started_at), "actual_wait_sec": actual_wait,
                       "prompt_sha256": prompt_sha, "request_params": self.params}
            if not self.begin_attempt(started):
                return                                  # stopped: no new attempts

            result = self.execute(prompt)
            completed_at = self.now()
            outcome = result["outcome"]
            retry_after = result.pop("retry_after")

            stop_reason = None
            planned_wait = wait_source = None
            if outcome == "fatal_error":
                stop_reason = "fatal_error"
            elif outcome in ("retryable_error", "invalid_response"):
                if retry_after is not None:
                    if retry_after > self.settings.backoff_max:
                        stop_reason = "retry_after_exceeds_max"
                        planned_wait, wait_source = retry_after, "retry_after"
                    elif attempt < MAX_ATTEMPTS:
                        planned_wait, wait_source = retry_after, "retry_after"
                elif attempt < MAX_ATTEMPTS:
                    planned_wait, wait_source = self.backoff(attempt), "backoff"

            rec = {"event": "attempt_completed", "run_id": self.run_id, "pass": self.pass_no,
                   "order_index": idx, "utterance_id": call["utterance_id"],
                   "condition": call["condition"], "repeat": call["repeat"], "attempt": attempt,
                   "completed_seq": None, "completed_at": iso(completed_at), **result,
                   "planned_wait_sec": planned_wait, "wait_source": wait_source}
            self.record_completed(rec, stop_reason)

            if outcome == "success":
                st.has_success = st.terminated = True
                return
            if stop_reason is not None or attempt >= MAX_ATTEMPTS:
                st.terminated = attempt >= MAX_ATTEMPTS
                return
            self.sleep(planned_wait)
            prev_completed_at = iso(completed_at)
            attempt += 1

    # ---- one SDK call via with_raw_response ----
    def execute(self, prompt: str) -> dict:
        """Make one API request and return its record fields (5.4.6, 5.6.7).

        The request goes through with_raw_response so that raw_response is the
        body exactly as the server sent it, for error responses as well as
        successful ones. 5.6.7 stores that text and 5.6.8 re-derives the label
        from it later, so keeping a parsed object instead would discard what the
        record exists to preserve. The client is built with max_retries = 0
        (5.6.4), which is what makes one call here exactly one attempt.

        Error outcomes are classified by classify_http_status from the body's
        error.code and error.type (5.4.6). The body is preferred over the SDK
        exception's attributes, which serve only as a fallback, so that the
        classification can be re-checked afterwards from the stored record
        rather than depending on SDK behaviour at the time of the call.
        Connection errors and timeouts have no body and no status, and are
        retryable under 5.4.6 for that reason.
        """
        import openai
        from test_api_request import build_request

        base = {"invalid_reason": None, "http_status": None, "openai_request_id": None,
                "openai_error_code": None, "openai_error_type": None,
                "response_model": None, "system_fingerprint": None,
                "finish_reason": None, "usage": None, "raw_response": None, "error": None,
                "retry_after": None}
        try:
            raw = self.client.chat.completions.with_raw_response.create(**build_request(prompt))
        except openai.APIStatusError as e:
            resp = e.response
            body_text = resp.text if resp is not None else None
            code = error_code_from_body(body_text) or getattr(e, "code", None)
            err_type = error_type_from_body(body_text) or getattr(e, "type", None)
            status = e.status_code
            ra_header = resp.headers.get("retry-after") if resp is not None else None
            return {**base, "outcome": classify_http_status(status, code, err_type),
                    "http_status": status,
                    "openai_request_id": resp.headers.get("x-request-id") if resp is not None else None,
                    "openai_error_code": code, "openai_error_type": err_type,
                    "raw_response": body_text,
                    "error": {"type": type(e).__name__, "message": str(e), "retry_after": ra_header},
                    "retry_after": parse_retry_after(ra_header, self.now()) if status == 429 else None}
        except openai.APIConnectionError as e:          # includes APITimeoutError
            return {**base, "outcome": "retryable_error",
                    "error": {"type": type(e).__name__, "message": str(e), "retry_after": None}}

        body_text = raw.text
        v = validate_body(body_text)
        return {**base, "outcome": v.outcome, "invalid_reason": v.invalid_reason,
                "http_status": raw.status_code, "openai_request_id": raw.headers.get("x-request-id"),
                "response_model": v.response_model, "system_fingerprint": v.system_fingerprint,
                "finish_reason": v.finish_reason, "usage": v.usage, "raw_response": body_text}

    # ---- run all workers; write run_stopped after in-flight attempts are recorded ----
    def run(self) -> dict:
        """Run the workers to exhaustion, then close the pass (5.6.5).

        5.6.5 requires every in-flight attempt to be recorded before a stopped
        run ends, so run_stopped is written here, once all workers have joined,
        instead of when the stop was decided. The attempts file is closed only
        after that event so it ends complete, which is the condition 5.6.6
        resume and the 5.6.7 truncation rule are stated against. The returned
        counts say how many calls are terminated, not how many succeeded.
        """
        threads = [threading.Thread(target=self.worker, name=f"worker-{i}", daemon=True)
                   for i in range(self.settings.concurrency)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        stopped_rec = self.write_run_stopped() if self.stopped else None
        self.fh.close()
        n_term = sum(1 for st in self.states.values() if st.terminated)
        return {"terminated": n_term, "total": len(self.states), "stopped": stopped_rec}


# --------------------------------------------------------------------------
# Verification (5.6.6), lock, repair (5.6.7)
# --------------------------------------------------------------------------

def verify_for_resume(run_dir: Path, pass_no: int, manifest: dict, cli_settings: dict) -> dict:
    """Run the 5.6.6 resume checks; return the prompts or refuse to start.

    5.6.6 requires all of these to pass before a pass may be resumed, so every
    check is evaluated and the failures are reported together rather than at the
    first one. A report that stopped early would be worked through one restart
    at a time, and each restart is another chance to begin a pass against a
    manifest that no longer describes it.

    The numbered comments below are the check numbers as 5.6.6 lists them. The
    closing comparison of command-line settings with the manifest is not one of
    those five; it enforces the 5.6.4 rule that these values have no defaults
    and stay fixed for the whole pass.
    """
    problems: list[str] = []
    # Check 1, first part: the request is the one the manifest describes.
    if manifest.get("model") != MODEL:
        problems.append(f"model {manifest.get('model')} != {MODEL}")
    if manifest.get("request_params") != request_params():
        problems.append("request_params differ from test_api_request.build_request")
    if manifest.get("seed") != PASS_SEEDS[pass_no]:
        problems.append(f"seed {manifest.get('seed')} != {PASS_SEEDS[pass_no]}")

    # Check 4: the input file is unchanged. Verified before the call list because
    # check 1 recomputes that list from this file, so a changed input would
    # otherwise be reported only as a mismatched call list.
    input_path = Path(manifest["input_file"]["path"])
    if not input_path.exists():
        problems.append(f"input file missing: {input_path}")
    elif sha256_file(input_path) != manifest["input_file"]["sha256"]:
        problems.append("input file sha256 differs from manifest")
    else:
        # Check 1, second part: the ordered call list is recomputed and compared.
        # The manifest list is the reference for reproduction (5.6.2); recomputing
        # it here shows that the seed and the inputs still generate that same list.
        if pass_no == 1:
            expected = plan_pass1(read_ids(input_path), PASS_SEEDS[1])
        else:
            # Tie-break passes: the selection source is the previous pass's attempts file;
            # the tie list is re-derived with parse_attempts functions (in memory, no write).
            prev = run_dir / f"attempts_pass{pass_no - 1}.jsonl"
            if not prev.exists() or sha256_file(prev) != manifest.get(f"attempts_pass{pass_no - 1}_sha256"):
                problems.append(f"{prev.name} sha256 differs from manifest_pass{pass_no}")
                expected = None
            else:
                records = []
                for n in range(1, pass_no):
                    records.extend(read_jsonl_strict(run_dir / f"attempts_pass{n}.jsonl"))
                finals = final_rows(labels_from_records(records), manifest["run_id"])
                pending = sorted((r["utterance_id"], r["condition"]) for r in finals if r["status"] == "tie_pending")
                expected = plan_tiebreak(pending, pass_no)
        if expected is not None and expected != manifest["calls"]:
            problems.append("ordered call list differs from the list recomputed from seed and input")

    # Check 2: load_prompts recomputes the sha256 of every prompt body, and the
    # file's own sha256 must match the manifest. The first catches an edited
    # prompt, the second an added or removed line.
    prompts_path = run_dir / "prompts.jsonl"
    prompts = {}
    try:
        prompts = load_prompts(prompts_path)
    except (Refused, TruncatedLastLine, CorruptedFile, OSError) as exc:
        problems.append(f"prompts.jsonl: {exc}")
    else:
        if sha256_file(prompts_path) != manifest.get("prompts_sha256"):
            problems.append("prompts.jsonl sha256 differs from manifest")
        # Check 3: equality of the pair sets for pass 1; for tie-break passes only
        # a subset, since those schedule the tied pairs alone (5.4.3).
        pairs = manifest_pairs(manifest)
        if pass_no == 1 and pairs != set(prompts):
            problems.append("(utterance_id, condition) set differs between manifest and prompts.jsonl")
        if pass_no >= 2 and not pairs <= set(prompts):
            problems.append(f"manifest_pass{pass_no} has pairs absent from prompts.jsonl")

    # Check 5: same commit as the manifest and a clean tree, so the records of a
    # pass can be attributed to one state of the code.
    commit = git_commit_hash()
    if commit.endswith("-dirty"):
        problems.append("working tree is dirty")
    if commit.split("-")[0] != str(manifest.get("git_commit", "")).split("-")[0]:
        problems.append(f"git commit {commit} != manifest {manifest.get('git_commit')}")

    # Not one of the five checks: 5.6.4 fixes the operational values for the whole
    # pass, so a value given on the command line may repeat the manifest but not
    # change it. None means the flag was not given and the manifest value stands.
    stored = Settings.from_manifest(manifest)
    for name, value in cli_settings.items():
        if value is not None and value != getattr(stored, name):
            problems.append(f"--{name.replace('_', '-')} {value} != manifest {getattr(stored, name)}")

    if problems:
        raise Refused("resume verification failed:\n  - " + "\n  - ".join(problems))
    return prompts


def acquire_lock(run_dir: Path) -> Path:
    """Create run.lock exclusively, or refuse to start (5.6.6).

    5.6.6 uses the lock to keep two processes off one run: both would append to
    the same attempts file and hand out overlapping completed_seq values, which
    would make the sequence 5.6.5 counts in meaningless. O_EXCL makes the test
    and the creation a single step, so two runners starting together cannot both
    succeed.

    A stale lock is removed manually after inspection, by decision, so this never
    deletes or takes over an existing one: nothing here can tell a dead process
    from a running one, and guessing wrong would corrupt a live run.
    """
    lock = run_dir / "run.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise Refused(f"{lock} exists: another process may be running; inspect and remove it manually")
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps({"pid": os.getpid(), "created_at": iso(utc_now())}) + "\n")
    return lock


def repair(run_dir: Path, pass_no: int, now=utc_now) -> int:
    """5.6.7 truncated-last-line repair; refuses if damage is not confined to the last line."""
    path = run_dir / f"attempts_pass{pass_no}.jsonl"
    try:
        read_jsonl_strict(path)
    except TruncatedLastLine as t:
        stamp = now().strftime("%Y%m%dT%H%M%SZ")
        backup = path.with_name(f"{path.name}.bak-{stamp}")
        shutil.copy2(path, backup)
        with path.open("r+b") as f:
            f.truncate(t.offset)
            f.flush()
            os.fsync(f.fileno())
        with (run_dir / "recovery_log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"repaired_at": iso(now()), "file": path.name, "backup": backup.name,
                                "bytes_removed": len(t.text),
                                "removed_text": t.text.decode("utf-8", "replace")},
                               ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        print(f"repaired {path.name}: removed {len(t.text)} bytes; backup {backup.name}")
        return 0
    except CorruptedFile as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"nothing to repair: {path.name} parses completely")
    return 0


# --------------------------------------------------------------------------
# Pass preparation
# --------------------------------------------------------------------------

def prepare_pass1(run_dir: Path, run_id: str, input_path: Path, settings: Settings,
                  builder=build_prompt) -> dict:
    """Write prompts.jsonl and manifest_pass1.json before any call (5.6.2, 5.6.3).

    Both files are written before the first request, so the plan a pass is later
    judged against exists independently of its results. Prompts are built once
    per (utterance, condition) pair, while the manifest call list repeats each
    pair once per repeat block (5.6.1); the manifest stores the prompts file's
    sha256, which 5.6.6 check 2 verifies on resume.
    """
    ids = read_ids(input_path)
    calls = plan_pass1(ids, PASS_SEEDS[1])
    prompts_path = run_dir / "prompts.jsonl"
    write_prompts(prompts_path, [(uid, cond) for uid in ids for cond in CONDITIONS], builder)
    manifest = build_manifest(run_id, 1, calls, settings, sha256_file(prompts_path),
                              input_path, sha256_file(input_path))
    write_json(run_dir / "manifest_pass1.json", manifest)
    return manifest


def require_pass_terminated(run_dir: Path, pass_no: int) -> dict:
    """Return manifest_pass{N} after checking that every call of pass N is terminated."""
    m_path = run_dir / f"manifest_pass{pass_no}.json"
    a_path = run_dir / f"attempts_pass{pass_no}.jsonl"
    if not m_path.exists() or not a_path.exists():
        raise Refused(f"pass {pass_no} has not run")
    manifest = json.loads(m_path.read_text(encoding="utf-8"))
    states, _ = scan_attempts(read_jsonl_strict(a_path), manifest["calls"])
    open_calls = [i for i, st in states.items() if not st.terminated]
    if open_calls:
        raise Refused(f"pass {pass_no} not fully terminated: {len(open_calls)} calls open "
                      f"(first {open_calls[:5]})")
    return manifest


def prepare_tiebreak_pass(run_dir: Path, run_id: str, pass_no: int, settings: Settings) -> dict | None:
    """Write manifest_pass{N} (N = 2 or 3) from the tie_pending rows of final_labels.csv.

    Requires every call of pass N-1 to be terminated. Re-runs the parser so that
    labels.csv / final_labels.csv reflect all attempts files present, then reads
    the tie list from final_labels.csv. Returns None, writing nothing, when no
    pair is tie_pending (the pass is not needed).
    """
    prev_manifest = require_pass_terminated(run_dir, pass_no - 1)
    parse_run(run_dir, run_id)
    pairs = tie_pending_pairs(run_dir / "final_labels.csv")
    if not pairs:
        return None
    calls = plan_tiebreak(pairs, pass_no)
    m1 = prev_manifest if pass_no == 2 else json.loads((run_dir / "manifest_pass1.json").read_text(encoding="utf-8"))
    input_path = Path(m1["input_file"]["path"])
    extra = {f"attempts_pass{pass_no - 1}_sha256": sha256_file(run_dir / f"attempts_pass{pass_no - 1}.jsonl"),
             "final_labels_sha256": sha256_file(run_dir / "final_labels.csv"),
             "parse_attempts_git_commit": git_commit_hash(), "n_tie_pairs": len(pairs)}
    manifest = build_manifest(run_id, pass_no, calls, settings, sha256_file(run_dir / "prompts.jsonl"),
                              input_path, sha256_file(input_path), extra)
    write_json(run_dir / f"manifest_pass{pass_no}.json", manifest)
    return manifest


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Experiment runner (Decision Log 5.6).")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--pass", dest="pass_no", type=int, choices=(1, 2, 3), required=True)
    ap.add_argument("--input", type=Path, help="CSV with a source_id column (pass 1, fresh start)")
    ap.add_argument("--concurrency", type=int)
    ap.add_argument("--timeout", type=float)
    ap.add_argument("--backoff-initial", type=float)
    ap.add_argument("--backoff-max", type=float)
    ap.add_argument("--failure-threshold", type=int)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--repair", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="write manifest and prompts.jsonl; send nothing")
    return ap.parse_args(argv)


def settings_from_args(args: argparse.Namespace) -> Settings:
    missing = [n for n in ("concurrency", "timeout", "backoff_initial", "backoff_max", "failure_threshold")
               if getattr(args, n) is None]
    if missing:
        raise Refused("fresh start requires " + ", ".join("--" + n.replace("_", "-") for n in missing)
                      + " (5.6.4: no defaults for pilot settings)")
    return Settings(args.concurrency, args.timeout, args.backoff_initial, args.backoff_max,
                    args.failure_threshold)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_dir = RUNS_DIR / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = acquire_lock(run_dir)
    try:
        return _main_locked(args, run_dir)
    finally:
        lock.unlink(missing_ok=True)


def _main_locked(args: argparse.Namespace, run_dir: Path) -> int:
    pass_no = args.pass_no
    manifest_path = run_dir / f"manifest_pass{pass_no}.json"
    attempts_path = run_dir / f"attempts_pass{pass_no}.jsonl"

    if args.repair:
        return repair(run_dir, pass_no)

    if args.resume:
        if not manifest_path.exists():
            raise Refused(f"{manifest_path.name} missing: nothing to resume")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cli = {"concurrency": args.concurrency, "timeout": args.timeout,
               "backoff_initial": args.backoff_initial, "backoff_max": args.backoff_max,
               "failure_threshold": args.failure_threshold}
        prompts = verify_for_resume(run_dir, pass_no, manifest, cli)
        settings = Settings.from_manifest(manifest)
    else:
        if manifest_path.exists():
            raise Refused(f"{manifest_path.name} exists: use --resume, or a new --run-id for a re-run")
        if attempts_path.exists():
            raise Refused(f"{attempts_path.name} exists without a manifest: inspect manually")
        settings = settings_from_args(args)
        if pass_no == 1:
            if args.input is None:
                raise Refused("--input is required for a fresh pass 1")
            manifest = prepare_pass1(run_dir, args.run_id, args.input, settings)
        else:
            manifest = prepare_tiebreak_pass(run_dir, args.run_id, pass_no, settings)
            if manifest is None:
                print(f"pass {pass_no} not needed: no tie_pending rows in final_labels.csv")
                return 0
        prompts = load_prompts(run_dir / "prompts.jsonl")
        print(f"wrote {manifest_path.name}: {manifest['n_calls']} calls, seed {manifest['seed']}")
        if args.dry_run:
            return 0

    if attempts_path.exists():
        try:
            records = read_jsonl_strict(attempts_path)
        except TruncatedLastLine as t:
            raise Refused(f"{t}; run with --repair after inspecting the file")
        except CorruptedFile as exc:
            raise Refused(str(exc))
    else:
        records = []
    states, seq = scan_attempts(records, manifest["calls"])
    open_calls = sum(1 for st in states.values() if not st.terminated)
    print(f"pass {pass_no}: {len(states)} calls, {len(states) - open_calls} terminated, {open_calls} open")
    if open_calls == 0:
        return 0

    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY_ABLATION"], max_retries=0,
                    timeout=settings.timeout)
    runner = Runner(run_id=args.run_id, pass_no=pass_no, calls=manifest["calls"], prompts=prompts,
                    client=client, settings=settings, attempts_path=attempts_path, states=states,
                    completed_seq_start=seq)
    summary = runner.run()
    print(f"terminated {summary['terminated']}/{summary['total']}")
    if summary["stopped"]:
        print(f"run_stopped: {summary['stopped']['reason']} "
              f"(completed_seq {summary['stopped']['completed_seq_at_stop']}); resume manually")
        return 3
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        sys.exit(2)
