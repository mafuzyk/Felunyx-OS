#!/usr/bin/env python3
"""Set and verify a systemd-boot LoaderEntryOneShot in an OVMF varstore."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SYSTEMD_BOOT_GUID = "4a67b082-0a4c-41cf-b6c7-440b29bb8c4f"
VARIABLE_NAME = "LoaderEntryOneShot"
TOOL_PACKAGE = "python3-virt-firmware"
ALLOWED_ENTRIES = {
    "felunyx-linux-zen.conf",
    "felunyx-linux-lts.conf",
}


class OperationalError(RuntimeError):
    """A fail-closed executor or readback error."""


def write_json_atomic(path: Path, data: object) -> None:
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


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise OperationalError(
            f"command failed ({completed.returncode}): {' '.join(command)}"
            + (f": {detail}" if detail else "")
        )


def package_version(dpkg_query: str) -> str:
    completed = subprocess.run(
        [dpkg_query, "-W", "-f=${Version}\\n", TOOL_PACKAGE],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise OperationalError(
            f"cannot resolve installed {TOOL_PACKAGE} version"
        )
    return completed.stdout.strip().splitlines()[0]


def decode_entry(variable: dict[str, object]) -> str:
    if variable.get("name") != VARIABLE_NAME:
        raise OperationalError(f"{VARIABLE_NAME} readback is absent")
    if str(variable.get("guid", "")).casefold() != SYSTEMD_BOOT_GUID:
        raise OperationalError(f"{VARIABLE_NAME} readback GUID mismatch")
    if variable.get("attr") != 7:
        raise OperationalError(f"{VARIABLE_NAME} readback attributes mismatch")

    raw = variable.get("data")
    if not isinstance(raw, str):
        raise OperationalError(f"{VARIABLE_NAME} readback data is not hex")
    try:
        decoded = bytes.fromhex(raw).decode("utf-16-le")
    except (ValueError, UnicodeDecodeError) as exc:
        raise OperationalError(
            f"{VARIABLE_NAME} readback data is invalid"
        ) from exc
    return decoded.rstrip("\0")


def readback_entry(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperationalError("cannot parse virt-fw-vars readback") from exc

    if not isinstance(data, dict) or not isinstance(
        data.get("variables"), list
    ):
        raise OperationalError("virt-fw-vars readback schema is invalid")

    matches = [
        item
        for item in data["variables"]
        if isinstance(item, dict)
        and item.get("name") == VARIABLE_NAME
        and str(item.get("guid", "")).casefold() == SYSTEMD_BOOT_GUID
    ]
    if len(matches) != 1:
        raise OperationalError(
            f"expected one {VARIABLE_NAME} readback, found {len(matches)}"
        )
    return decode_entry(matches[0])


def set_loader_oneshot(vars_path: Path, entry: str, report: Path) -> None:
    if entry not in ALLOWED_ENTRIES:
        raise ValueError(f"unsupported loader entry: {entry}")
    if not vars_path.is_file():
        raise ValueError(f"OVMF varstore does not exist: {vars_path}")

    virt_fw_vars = shutil.which("virt-fw-vars")
    if not virt_fw_vars:
        raise OperationalError("virt-fw-vars is required")
    dpkg_query = shutil.which("dpkg-query")
    if not dpkg_query:
        raise OperationalError("dpkg-query is required")

    version = package_version(dpkg_query)
    payload = {
        "variables": [
            {
                "name": VARIABLE_NAME,
                "guid": SYSTEMD_BOOT_GUID,
                "attr": 7,
                "data": (entry + "\0").encode("utf-16-le").hex(),
            }
        ]
    }

    vars_path = vars_path.resolve()
    report = report.resolve()
    with tempfile.TemporaryDirectory(
        prefix=".felunyx-loader-oneshot-", dir=vars_path.parent
    ) as directory:
        temporary_dir = Path(directory)
        payload_path = temporary_dir / "set.json"
        modified_vars = temporary_dir / "OVMF_VARS.modified.fd"
        readback_path = temporary_dir / "readback.json"
        write_json_atomic(payload_path, payload)

        run_checked(
            [
                virt_fw_vars,
                "--input",
                str(vars_path),
                "--set-json",
                str(payload_path),
                "--output",
                str(modified_vars),
            ]
        )
        if not modified_vars.is_file():
            raise OperationalError("virt-fw-vars did not produce a varstore")

        run_checked(
            [
                virt_fw_vars,
                "--input",
                str(modified_vars),
                "--output-json",
                str(readback_path),
            ]
        )
        observed = readback_entry(readback_path)
        if observed != entry:
            raise OperationalError(
                "LoaderEntryOneShot readback mismatch: "
                f"requested {entry!r}, observed {observed!r}"
            )

        os.replace(modified_vars, vars_path)

    write_json_atomic(
        report,
        {
            "schema": 1,
            "tool_package": TOOL_PACKAGE,
            "tool_version": version,
            "guid": SYSTEMD_BOOT_GUID,
            "variable": VARIABLE_NAME,
            "entry": entry,
            "verified": True,
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vars", type=Path, required=True)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        set_loader_oneshot(args.vars, args.entry, args.report)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 64
    except OperationalError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
