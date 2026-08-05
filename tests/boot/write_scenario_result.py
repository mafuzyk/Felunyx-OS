#!/usr/bin/env python3
"""Write one canonical, atomic virtual-scenario result."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

STATUSES = {"pass", "fail", "blocked", "not-run"}
EVIDENCE_KEY = re.compile(r"^[a-z][a-z0-9_-]*$")


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


def parse_evidence(values: list[str]) -> dict[str, str]:
    evidence: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid evidence mapping: {value}")
        key, path = value.split("=", 1)
        if not EVIDENCE_KEY.fullmatch(key):
            raise ValueError(f"invalid evidence key: {key}")
        if not path:
            raise ValueError(f"empty evidence path: {key}")
        if key in evidence:
            raise ValueError(f"duplicate evidence key: {key}")
        evidence[key] = path
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--finished-at", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.status not in STATUSES:
        print(f"unsupported scenario status: {args.status}", file=sys.stderr)
        return 64
    try:
        evidence = parse_evidence(args.evidence)
        write_atomic(
            args.output,
            {
                "schema": 1,
                "scenario": args.scenario,
                "status": args.status,
                "started_at": args.started_at,
                "finished_at": args.finished_at,
                "message": args.message,
                "evidence": evidence,
            },
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 64 if isinstance(exc, ValueError) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
