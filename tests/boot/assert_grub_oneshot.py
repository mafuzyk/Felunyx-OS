#!/usr/bin/env python3
"""Validate a verified installed GRUB one-shot preparation marker."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

PREFIX = "FELUNYX_GRUB_NEXT="
ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(data: dict[str, object]) -> None:
    for key in ("schema", "requested", "selector", "verified"):
        require(key in data, f"missing required key: {key}")

    require(data.get("schema") == 1, "GRUB one-shot schema must be 1")
    require(
        data.get("requested") == "linux-lts",
        "unexpected GRUB one-shot request",
    )
    require(
        data.get("verified") is True,
        "GRUB one-shot was not verified",
    )

    selector = data.get("selector")
    require(isinstance(selector, str), "GRUB selector is absent")
    parts = selector.split(">")
    require(
        len(parts) == 2,
        "GRUB selector must include submenu and entry IDs",
    )
    require(
        all(part and not part.isdigit() and ID.fullmatch(part) for part in parts),
        "GRUB selector must use stable IDs",
    )


def read_payload(path: Path, timeout: int) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    seen = ""
    while True:
        if path.exists():
            seen = path.read_text(encoding="utf-8", errors="replace")
            matches = [
                line[len(PREFIX):]
                for line in seen.splitlines()
                if line.startswith(PREFIX)
            ]
            if len(matches) > 1:
                raise ValueError("duplicate GRUB one-shot evidence")
            if len(matches) == 1:
                try:
                    payload = json.loads(matches[0])
                except json.JSONDecodeError as exc:
                    raise ValueError("malformed GRUB one-shot evidence") from exc
                require(
                    isinstance(payload, dict),
                    "GRUB one-shot evidence is not an object",
                )
                return payload
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"{PREFIX!r} not found in {path}; tail={seen[-2000:]}"
            )
        time.sleep(0.1)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = read_payload(args.log, args.timeout)
        validate(data)
        write_atomic(args.output, data)
    except (ValueError, TimeoutError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
