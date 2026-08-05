#!/usr/bin/env python3
"""Aggregate independent Phase 2 VM scenario results fail closed."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

REQUIRED = {
    "live_zen": "live-zen",
    "live_lts": "live-lts",
    "install": "install",
    "installed_zen": "installed-zen",
    "installed_lts": "installed-lts",
    "failure_injection": "failure-injection",
}
BEST_EFFORT = {"bios": "bios"}
VALID_STATUSES = {"pass", "fail", "blocked", "not-run"}


def write_atomic(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def read_result(path: Path, expected_scenario: str) -> tuple[str, bool]:
    if not path.is_file():
        return "not-run", True

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "fail", False

    if not isinstance(data, dict):
        return "fail", False
    if data.get("schema") != 1:
        return "fail", False
    if data.get("scenario") != expected_scenario:
        return "fail", False

    status = data.get("status")
    if not isinstance(status, str) or status not in VALID_STATUSES:
        return "fail", False
    return status, True


def summarize(root: Path) -> tuple[dict[str, object], bool]:
    required: dict[str, str] = {}
    best_effort: dict[str, str] = {}
    integrity_ok = True

    for key, expected in REQUIRED.items():
        status, valid = read_result(
            root / key / "scenario-result.json", expected
        )
        required[key] = status
        integrity_ok = integrity_ok and valid

    for key, expected in BEST_EFFORT.items():
        status, valid = read_result(
            root / key / "scenario-result.json", expected
        )
        best_effort[key] = status
        integrity_ok = integrity_ok and valid

    passed = integrity_ok and all(
        status == "pass" for status in required.values()
    )
    summary: dict[str, object] = {
        "schema": 1,
        "required": required,
        "best_effort": best_effort,
        "virtual_gate": "pass" if passed else "fail",
    }
    return summary, passed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary, passed = summarize(args.root)
        write_atomic(args.output, summary)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
