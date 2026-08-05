#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PREFIX = "FELUNYX_EVIDENCE="
REQUIRED_KEYS = (
    "schema",
    "id",
    "build_metadata",
    "kernel",
    "kernel_variant",
    "live",
    "uefi",
    "graphical_target",
    "sddm",
    "networkmanager",
    "plasma_wayland_available",
    "sessions",
    "sshd_service_active",
    "sshd_socket_active",
)


def wait_for_payload(path: Path, timeout: int) -> dict:
    deadline = time.monotonic() + timeout
    seen = ""
    while time.monotonic() < deadline:
        if path.exists():
            seen = path.read_text(encoding="utf-8", errors="replace")
            matches = [
                line[len(PREFIX) :]
                for line in seen.splitlines()
                if line.startswith(PREFIX)
            ]
            if len(matches) > 1:
                raise ValueError("duplicate live evidence payloads")
            if matches:
                try:
                    payload = json.loads(matches[0])
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"malformed live evidence JSON: {exc.msg}"
                    ) from exc
                if not isinstance(payload, dict):
                    raise ValueError("live evidence must be a JSON object")
                return payload
        time.sleep(0.1)
    raise TimeoutError(f"{PREFIX!r} not found in {path}; tail={seen[-2000:]}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_keys(data: dict) -> None:
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"missing required key: {key}")


def has_active_plasma_session(sessions: object) -> bool:
    if not isinstance(sessions, list):
        return False
    for session in sessions:
        if not isinstance(session, dict):
            continue
        desktop = str(session.get("desktop", "")).casefold()
        if (
            session.get("class") == "user"
            and session.get("type") == "wayland"
            and session.get("active") is True
            and session.get("remote") is False
            and ("kde" in desktop or "plasma" in desktop)
        ):
            return True
    return False


def validate_live(data: dict, kernel: str, firmware: str) -> None:
    require_keys(data)
    require(data.get("schema") == 2, "live evidence schema must be 2")
    require(data.get("id") == "felunyx", "guest identity is not Felunyx")
    require(data.get("kernel_variant") == kernel, "wrong live kernel")
    require(
        isinstance(data.get("kernel"), str) and bool(data["kernel"]),
        "running kernel is absent",
    )
    require(data.get("live") is True, "live marker is absent")
    if firmware == "uefi":
        require(data.get("uefi") is True, "required UEFI boot was not observed")
    else:
        require(data.get("uefi") is False, "BIOS boot was not observed")
    require(data.get("build_metadata") is True, "build metadata is absent")
    require(data.get("graphical_target") is True, "graphical target is inactive")
    require(data.get("sddm") is True, "SDDM is inactive")
    require(data.get("networkmanager") is True, "NetworkManager is inactive")
    require(
        data.get("plasma_wayland_available") is True,
        "Plasma Wayland definition is absent",
    )
    require(
        has_active_plasma_session(data.get("sessions")),
        "active Plasma Wayland session is absent",
    )
    require(data.get("sshd_service_active") is False, "SSH service is active")
    require(data.get("sshd_socket_active") is False, "SSH socket is active")


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
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
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--kernel", choices=("zen", "lts"), required=True)
    parser.add_argument(
        "--firmware", choices=("uefi", "bios"), default="uefi"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        payload = wait_for_payload(args.log, args.timeout)
        validate_live(payload, args.kernel, args.firmware)
        write_atomic(args.output, payload)
    except (OSError, TimeoutError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
