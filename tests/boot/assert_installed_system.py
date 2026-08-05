#!/usr/bin/env python3
"""Validate read-only evidence emitted by an installed Felunyx system."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PREFIX = "FELUNYX_INSTALLED="
EXPECTED_SUBVOLUMES = {
    "/": "/@",
    "/home": "/@home",
    "/.snapshots": "/@snapshots",
    "/var/cache": "/@cache",
    "/var/log": "/@log",
}
REQUIRED_PACKAGES = ("grub", "linux-zen", "linux-lts")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def required_mapping(data: dict, key: str) -> dict:
    require(key in data, f"missing required key: {key}")
    value = data[key]
    require(isinstance(value, dict), f"required mapping is invalid: {key}")
    return value


def required_list(data: dict, key: str) -> list:
    require(key in data, f"missing required key: {key}")
    value = data[key]
    require(isinstance(value, list), f"required list is invalid: {key}")
    return value


def options(value: object) -> set[str]:
    require(isinstance(value, list), "mount options must be a list")
    require(all(isinstance(item, str) for item in value), "mount options contain a non-string value")
    return {item.strip() for item in value if item.strip()}


def normalize_subvolume(value: object) -> str:
    require(isinstance(value, str) and value.strip(), "Btrfs subvolume is absent")
    return "/" + value.strip().lstrip("/")


def has_efi_mask(option_set: set[str]) -> bool:
    if "umask=0077" in option_set:
        return True
    return {"fmask=0077", "dmask=0077"}.issubset(option_set)


def validate_mounts(data: dict) -> None:
    mounts = required_mapping(data, "mounts")
    for target, expected_subvolume in EXPECTED_SUBVOLUMES.items():
        require(target in mounts, f"required mount is absent: {target}")
        mount = mounts[target]
        require(isinstance(mount, dict), f"mount observation is invalid: {target}")
        require(mount.get("fstype") == "btrfs", f"wrong filesystem for {target}")
        observed_subvolume = normalize_subvolume(mount.get("subvolume"))
        require(
            observed_subvolume == expected_subvolume,
            f"wrong Btrfs subvolume for {target}: expected {expected_subvolume}, observed {observed_subvolume}",
        )
        require(
            "compress=zstd:1" in options(mount.get("options")),
            f"missing compress=zstd:1 on {target}",
        )
        require(
            isinstance(mount.get("source"), str) and bool(mount["source"]),
            f"mount source is absent: {target}",
        )

    require("/boot/efi" in mounts, "required mount is absent: /boot/efi")
    efi = mounts["/boot/efi"]
    require(isinstance(efi, dict), "EFI mount observation is invalid")
    require(efi.get("fstype") == "vfat", "EFI filesystem is not vfat")
    require(has_efi_mask(options(efi.get("options"))), "EFI mount mask is not 0077")


def validate_subvolume_inventory(data: dict) -> None:
    observed = {
        normalize_subvolume(item)
        for item in required_list(data, "subvolumes")
    }
    expected = set(EXPECTED_SUBVOLUMES.values())
    missing = sorted(expected - observed)
    require(not missing, f"required Btrfs subvolumes are absent: {', '.join(missing)}")
    unexpected = observed - expected - {"/@swap"}
    require(
        not unexpected,
        f"unexpected Btrfs subvolumes observed: {', '.join(sorted(unexpected))}",
    )


def fstab_entries(data: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for entry in required_list(data, "fstab"):
        require(isinstance(entry, dict), "fstab entry is invalid")
        target = entry.get("target")
        require(isinstance(target, str) and target, "fstab target is absent")
        require(target not in result, f"duplicate fstab target: {target}")
        result[target] = entry
    return result


def validate_fstab(data: dict) -> None:
    entries = fstab_entries(data)
    for target, expected_subvolume in EXPECTED_SUBVOLUMES.items():
        require(target in entries, f"required fstab target is absent: {target}")
        entry = entries[target]
        require(entry.get("fstype") == "btrfs", f"wrong fstab filesystem for {target}")
        option_set = options(entry.get("options"))
        require("compress=zstd:1" in option_set, f"fstab compression is absent: {target}")
        subvolumes = [item.split("=", 1)[1] for item in option_set if item.startswith("subvol=")]
        require(len(subvolumes) == 1, f"fstab subvolume is ambiguous: {target}")
        observed = normalize_subvolume(subvolumes[0])
        require(
            observed == expected_subvolume,
            f"wrong fstab subvolume for {target}: expected {expected_subvolume}, observed {observed}",
        )

    require("/boot/efi" in entries, "required fstab target is absent: /boot/efi")
    efi = entries["/boot/efi"]
    require(efi.get("fstype") == "vfat", "EFI fstab filesystem is not vfat")
    require(has_efi_mask(options(efi.get("options"))), "EFI fstab mask is not 0077")


def validate_boot_payload(data: dict) -> None:
    packages = required_mapping(data, "packages")
    for package in REQUIRED_PACKAGES:
        require(packages.get(package) is True, f"required package absent: {package}")
    require(packages.get("felunyx-iso-hooks") is False, "live-only package remains installed")

    files = required_mapping(data, "files")
    checks = (
        ("grub_cfg", "GRUB configuration is absent"),
        ("linux_zen_kernel", "Linux Zen kernel image is absent"),
        ("linux_lts_kernel", "Linux LTS kernel image is absent"),
    )
    for key, message in checks:
        observation = files.get(key)
        require(isinstance(observation, dict), message)
        require(observation.get("exists") is True, message)
        require(isinstance(observation.get("size"), int) and observation["size"] > 0, message)

    require(files.get("live_marker") is False, "live marker remains installed")
    require(files.get("live_sudo") is False, "live sudo policy remains installed")
    require(files.get("live_autologin") is False, "live autologin policy remains installed")


def validate_installed(data: dict, kernel: str) -> None:
    required = {
        "schema",
        "id",
        "build_metadata",
        "build_info",
        "kernel",
        "kernel_variant",
        "live",
        "uefi",
        "packages",
        "files",
        "services",
        "mounts",
        "subvolumes",
        "fstab",
    }
    for key in sorted(required):
        require(key in data, f"missing required key: {key}")

    require(data.get("schema") == 1, "installed evidence schema must be 1")
    require(data.get("id") == "felunyx", "guest identity is not Felunyx")
    require(data.get("kernel_variant") == kernel, "wrong installed kernel")
    require(isinstance(data.get("kernel"), str) and bool(data["kernel"]), "running kernel is absent")
    require(data.get("live") is False, "installed evidence reports live state")
    require(data.get("uefi") is True, "required UEFI boot was not observed")
    require(data.get("build_metadata") is True, "build metadata is absent")
    build_info = required_mapping(data, "build_info")
    require(build_info.get("phase") == 2, "build metadata phase is not 2")
    require(isinstance(build_info.get("source_commit"), str) and bool(build_info["source_commit"]), "build source commit is absent")

    services = required_mapping(data, "services")
    require(services.get("sshd_service_active") is False, "SSH service is active")
    require(services.get("sshd_socket_active") is False, "SSH socket is active")

    validate_boot_payload(data)
    validate_mounts(data)
    validate_subvolume_inventory(data)
    validate_fstab(data)


def read_payload(path: Path, timeout: int) -> dict:
    deadline = time.monotonic() + timeout
    seen = ""
    while True:
        if path.exists():
            seen = path.read_text(encoding="utf-8", errors="replace")
            matches = [line[len(PREFIX):] for line in seen.splitlines() if line.startswith(PREFIX)]
            if len(matches) > 1:
                raise ValueError("duplicate installed evidence")
            if len(matches) == 1:
                try:
                    data = json.loads(matches[0])
                except json.JSONDecodeError as exc:
                    raise ValueError("malformed installed evidence JSON") from exc
                require(isinstance(data, dict), "installed evidence payload is not an object")
                return data
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{PREFIX!r} not found in {path}; tail={seen[-2000:]}")
        time.sleep(0.1)


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
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
    parser.add_argument("--kernel", choices=("zen", "lts"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = read_payload(args.log, args.timeout)
        validate_installed(data, args.kernel)
        write_atomic(args.output, data)
    except (ValueError, TimeoutError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
