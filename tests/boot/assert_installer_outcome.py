#!/usr/bin/env python3
"""Validate installer outcome events and safely extract transported guest logs."""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

EVENT_PREFIX = "FELUNYX_INSTALL="
LOG_PREFIX = "FELUNYX_INSTALL_LOG="
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MAX_LOG_SIZE = 8 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_prefixed(path: Path, prefix: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    result: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if not line.startswith(prefix):
            continue
        try:
            value = json.loads(line[len(prefix):])
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed {prefix.rstrip('=')} JSON") from exc
        require(isinstance(value, dict), f"{prefix.rstrip('=')} payload is not an object")
        result.append(value)
    return result


def validate_events(events: list[dict[str, object]], mode: str) -> dict[str, object]:
    starts = [event for event in events if event.get("event") == "start"]
    successes = [event for event in events if event.get("event") == "success"]
    failures = [event for event in events if event.get("event") == "failure"]
    blocked = [event for event in events if event.get("event") == "blocked"]

    require(len(starts) == 1, f"expected one installer start event, found {len(starts)}")
    require(starts[0].get("mode") == mode, "installer start mode mismatch")
    if blocked:
        raise ValueError("installer was blocked instead of reaching expected failure" if mode == "failure" else "installer was blocked")

    if mode == "success":
        require(not failures, "unexpected installer failure in success mode")
        require(len(successes) == 1, f"expected one installer success event, found {len(successes)}")
        require(successes[0].get("mode") == "success", "installer success mode mismatch")
        return {"outcome": "success"}

    require(not successes, "unexpected installer success in failure mode")
    require(len(failures) == 1, f"expected one injected failure event, found {len(failures)}")
    failure = failures[0]
    require(
        failure.get("stage") == "felunyx-fail"
        and failure.get("error_class") == "FelunyxInjectedFailure",
        "unexpected installer failure classification",
    )
    return {
        "outcome": "expected-failure",
        "error_class": "FelunyxInjectedFailure",
    }


def decode_logs(records: list[dict[str, object]]) -> dict[str, bytes]:
    decoded: dict[str, bytes] = {}
    for record in records:
        require(record.get("schema") == 1, "installer log schema must be 1")
        name = record.get("name")
        require(
            isinstance(name, str)
            and SAFE_NAME.fullmatch(name) is not None
            and Path(name).name == name,
            "unsafe installer log name",
        )
        require(name not in decoded, f"duplicate installer log: {name}")
        encoded = record.get("content_base64")
        require(isinstance(encoded, str), f"installer log content is absent: {name}")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"installer log base64 is invalid: {name}") from exc
        require(len(content) <= MAX_LOG_SIZE, f"installer log is too large: {name}")
        require(record.get("size") == len(content), f"installer log size mismatch: {name}")
        require(
            record.get("sha256") == hashlib.sha256(content).hexdigest(),
            f"installer log digest mismatch: {name}",
        )
        decoded[name] = content
    return decoded


def write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def write_json_atomic(path: Path, data: dict[str, object]) -> None:
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_bytes_atomic(path, payload)


def wait_for_outcome(
    serial: Path,
    evidence_stream: Path,
    mode: str,
    timeout: int,
) -> tuple[dict[str, object], dict[str, bytes]]:
    deadline = time.monotonic() + timeout
    last_error: ValueError | None = None
    while True:
        try:
            events = parse_prefixed(serial, EVENT_PREFIX)
            outcome = validate_events(events, mode)
            logs = decode_logs(parse_prefixed(evidence_stream, LOG_PREFIX))
            require("installer-harness.log" in logs, "required installer log is absent: installer-harness.log")
            if mode == "failure":
                require("calamares-debug.log" in logs, "required failure log is absent: calamares-debug.log")
            return outcome, logs
        except ValueError as exc:
            last_error = exc
        if time.monotonic() >= deadline:
            raise last_error or TimeoutError("installer outcome was not observed")
        time.sleep(0.1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", type=Path, required=True)
    parser.add_argument("--evidence-stream", type=Path, required=True)
    parser.add_argument("--mode", choices=("success", "failure"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=2400)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        outcome, logs = wait_for_outcome(
            args.serial, args.evidence_stream, args.mode, args.timeout
        )
        for name, content in logs.items():
            write_bytes_atomic(args.logs_dir / name, content)
        summary: dict[str, object] = {
            "schema": 1,
            "mode": args.mode,
            **outcome,
            "logs": sorted(logs),
        }
        write_json_atomic(args.output, summary)
    except (OSError, TimeoutError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
