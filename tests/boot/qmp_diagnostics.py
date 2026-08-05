#!/usr/bin/env python3
"""Capture small, read-only QMP diagnostics without changing VM state."""
from __future__ import annotations

import argparse
import json
import os
import socket
import tempfile
import time
from pathlib import Path


def receive(stream) -> dict:
    line = stream.readline()
    if not line:
        raise RuntimeError("QMP connection closed")
    value = json.loads(line)
    if not isinstance(value, dict):
        raise RuntimeError("QMP response is not an object")
    return value


def execute(stream, command: str) -> dict:
    stream.write(json.dumps({"execute": command}).encode("utf-8") + b"\n")
    while True:
        value = receive(stream)
        if "event" in value:
            continue
        return value


def write_atomic(path: Path, data: dict) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout
    while not args.socket.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    if not args.socket.exists():
        return 1

    connection = socket.socket(socket.AF_UNIX)
    connection.settimeout(args.timeout)
    try:
        connection.connect(str(args.socket))
        stream = connection.makefile("rwb", buffering=0)
        greeting = receive(stream)
        capabilities = execute(stream, "qmp_capabilities")
        status = execute(stream, "query-status")
        version = execute(stream, "query-version")
        write_atomic(
            args.output,
            {
                "schema": 1,
                "greeting": greeting,
                "capabilities": capabilities,
                "status": status,
                "version": version,
            },
        )
    except (OSError, RuntimeError, json.JSONDecodeError):
        return 1
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
