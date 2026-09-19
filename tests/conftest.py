"""Shared fixtures: no network, no real API key, synthetic prompts.

The runner is exercised with a fake client whose ``with_raw_response.create``
returns a fake raw response or raises a real ``openai`` exception built from an
``httpx.Response``. Time and sleep are injected so waits are observable.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import openai
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
os.environ.setdefault("TALKMOVES_DIR", str(REPO_ROOT))   # paths.py import guard only

import run_experiment as rx  # noqa: E402
from build_inputs import CONDITIONS  # noqa: E402
from test_api_request import MODEL  # noqa: E402


def ok_body(category="Not coded", finish="stop", refusal=None, content=None, extra_fields=None) -> str:
    """A Chat Completions body as the API returns it (as text)."""
    if content is None:
        obj = {"category": category}
        if extra_fields:
            obj.update(extra_fields)
        content = json.dumps(obj)
    return json.dumps({
        "id": "chatcmpl-x", "object": "chat.completion", "model": MODEL,
        "system_fingerprint": "fp_test",
        "choices": [{"index": 0, "finish_reason": finish,
                     "message": {"role": "assistant", "content": content, "refusal": refusal}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15,
                  "completion_tokens_details": {"reasoning_tokens": 0}},
    })


class FakeRaw:
    def __init__(self, text: str, status_code: int = 200, request_id: str = "req_ok"):
        self.text, self.status_code = text, status_code
        self.headers = {"x-request-id": request_id}


def status_error(status: int, code: str | None = None, retry_after: str | None = None,
                 request_id: str = "req_err") -> openai.APIStatusError:
    """A real openai exception of the class the SDK would raise for ``status``."""
    body = {"error": {"message": "synthetic", "type": "synthetic", "param": None, "code": code}}
    headers = {"x-request-id": request_id}
    if retry_after is not None:
        headers["retry-after"] = retry_after
    resp = httpx.Response(status, headers=headers, json=body,
                          request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"))
    cls = {429: openai.RateLimitError, 500: openai.InternalServerError, 503: openai.InternalServerError,
           401: openai.AuthenticationError, 400: openai.BadRequestError}.get(status, openai.APIStatusError)
    return cls("synthetic", response=resp, body=body["error"])


def connection_error() -> openai.APIConnectionError:
    return openai.APITimeoutError(request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"))


class FakeClient:
    """handler(prompt, n_calls_so_far_for_this_prompt) -> FakeRaw, or raises."""

    def __init__(self, handler):
        self.handler = handler
        self.seen: dict[str, int] = {}
        self.requests: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(
            with_raw_response=SimpleNamespace(create=self._create)))

    def _create(self, **request):
        self.requests.append(request)
        prompt = request["messages"][0]["content"]
        n = self.seen.get(prompt, 0)
        self.seen[prompt] = n + 1
        return self.handler(prompt, n)


class Clock:
    """Deterministic UTC clock: every call advances by ``step`` seconds."""

    def __init__(self, start="2026-09-18T00:00:00+00:00", step=1.0):
        self.t = datetime.fromisoformat(start).astimezone(timezone.utc)
        self.step = timedelta(seconds=step)

    def __call__(self) -> datetime:
        self.t += self.step
        return self.t


def fake_prompt(uid: int, cond: str) -> str:
    return f"PROMPT uid={uid} cond={cond}"


def calls_for(ids: list[int], pass_no: int = 1) -> list[dict]:
    if pass_no == 1:
        return rx.plan_pass1(ids, rx.PASS_SEEDS[1])
    return rx.plan_tiebreak([(u, c) for u in ids for c in CONDITIONS], pass_no)


def prompts_for(calls: list[dict]) -> dict:
    return {(c["utterance_id"], c["condition"]):
            (fake_prompt(c["utterance_id"], c["condition"]),
             rx.sha256_text(fake_prompt(c["utterance_id"], c["condition"])))
            for c in calls}


def settings(**over) -> rx.Settings:
    base = dict(concurrency=1, timeout=30.0, backoff_initial=2.0, backoff_max=60.0, failure_threshold=100)
    base.update(over)
    return rx.Settings(**base)


def make_runner(tmp_path: Path, handler, *, ids=(1,), pass_no=1, calls=None, records=None, sleeps=None,
                clock=None, run_id="t", **over) -> tuple[rx.Runner, Path, FakeClient]:
    calls = calls if calls is not None else calls_for(list(ids), pass_no)
    attempts = tmp_path / f"attempts_pass{pass_no}.jsonl"
    states, seq = rx.scan_attempts(records or [], calls)
    client = FakeClient(handler)
    sleeps = sleeps if sleeps is not None else []
    runner = rx.Runner(run_id=run_id, pass_no=pass_no, calls=calls, prompts=prompts_for(calls),
                       client=client, settings=settings(**over), attempts_path=attempts,
                       states=states, completed_seq_start=seq, rng=random.Random(0),
                       sleep=sleeps.append, now=clock or Clock())
    return runner, attempts, client


def read_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


@pytest.fixture
def helpers():
    return SimpleNamespace(ok_body=ok_body, FakeRaw=FakeRaw, status_error=status_error,
                           connection_error=connection_error, FakeClient=FakeClient, Clock=Clock,
                           fake_prompt=fake_prompt, calls_for=calls_for, prompts_for=prompts_for,
                           settings=settings, make_runner=make_runner, read_records=read_records)
