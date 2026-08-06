import io
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_fake_iso(root: Path, entry_files: dict, payload: list[str]) -> Path:
    """Build a plain TAR readable by bsdtar, shaped like the EFI ISO layout."""
    archive = root / "fake.iso"
    with tarfile.open(archive, "w") as tar:
        for name, content in entry_files.items():
            info = tarfile.TarInfo(f"loader/entries/{name}")
            data = content.encode()
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for path in payload:
            info = tarfile.TarInfo(path)
            info.size = 1
            tar.addfile(info, io.BytesIO(b"\0"))
    return archive


def run_validator(
    profile: Path, iso: Path, report: Path
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "tools/felunyx-validate",
            "--profile",
            str(profile),
            "--iso",
            str(iso),
            "--report",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_validator_rejects_efi_entries_referencing_missing_payload(tmp_path):
    iso = build_fake_iso(
        tmp_path,
        {
            "felunyx-linux-zen.conf": (
                "linux    /felunyx/boot/x86_64/vmlinuz-linux-zen\n"
                "initrd   /felunyx/boot/x86_64/amd-ucode.img\n"
                "initrd   /felunyx/boot/x86_64/intel-ucode.img\n"
                "initrd   /felunyx/boot/x86_64/initramfs-linux-zen.img\n"
            ),
            "felunyx-linux-lts.conf": (
                "linux    /felunyx/boot/x86_64/vmlinuz-linux-lts\n"
                "initrd   /felunyx/boot/x86_64/amd-ucode.img\n"
                "initrd   /felunyx/boot/x86_64/intel-ucode.img\n"
                "initrd   /felunyx/boot/x86_64/initramfs-linux-lts.img\n"
            ),
        },
        # amd-ucode.img and intel-ucode.img intentionally absent
        payload=[
            "felunyx/boot/x86_64/vmlinuz-linux-zen",
            "felunyx/boot/x86_64/vmlinuz-linux-lts",
            "felunyx/boot/x86_64/initramfs-linux-zen.img",
            "felunyx/boot/x86_64/initramfs-linux-lts.img",
        ],
    )
    report = tmp_path / "report.json"
    result = run_validator(ROOT / "iso" / "profile", iso, report)

    data = json.loads(report.read_text())
    assert result.returncode == 1
    assert data["status"] == "fail"
    names = {c["name"] for c in data["checks"]}
    assert "efi-payload-complete" in names
    efi = next(c for c in data["checks"] if c["name"] == "efi-payload-complete")
    assert efi["status"] == "fail"
    assert "amd-ucode.img" in efi["detail"]
    assert "intel-ucode.img" in efi["detail"]


def test_validator_accepts_efi_entries_with_embedded_microcode(tmp_path):
    iso = build_fake_iso(
        tmp_path,
        {
            "felunyx-linux-zen.conf": (
                "linux    /felunyx/boot/x86_64/vmlinuz-linux-zen\n"
                "initrd   /felunyx/boot/x86_64/initramfs-linux-zen.img\n"
            ),
            "felunyx-linux-lts.conf": (
                "linux    /felunyx/boot/x86_64/vmlinuz-linux-lts\n"
                "initrd   /felunyx/boot/x86_64/initramfs-linux-lts.img\n"
            ),
        },
        payload=[
            "felunyx/boot/x86_64/vmlinuz-linux-zen",
            "felunyx/boot/x86_64/vmlinuz-linux-lts",
            "felunyx/boot/x86_64/initramfs-linux-zen.img",
            "felunyx/boot/x86_64/initramfs-linux-lts.img",
        ],
    )
    report = tmp_path / "report.json"
    result = run_validator(ROOT / "iso" / "profile", iso, report)

    data = json.loads(report.read_text())
    assert result.returncode == 0
    assert data["status"] == "pass"
    efi = next(
        c for c in data["checks"] if c["name"] == "efi-payload-complete"
    )
    assert efi["status"] == "pass"