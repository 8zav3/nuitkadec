import os
import re
from pathlib import Path


def detect_python_version_from_dir(directory: Path) -> str | None:
    if not directory.is_dir():
        return None
    for entry in directory.iterdir():
        name = entry.name.lower()
        m = re.match(r"^python3(\d{1,2})\.dll$", name)
        if m:
            return f"3.{m.group(1)}"
        m = re.match(r"^libpython3\.(\d{1,2})", name)
        if m:
            return f"3.{m.group(1)}"
    return None


def detect_python_version_from_binary(binary: Path) -> str | None:
    ver = detect_python_version_from_dir(binary.parent)
    if ver:
        return ver
    try:
        data = binary.read_bytes()
    except OSError:
        return None
    for pat in (rb"python3(\d{1,2})\.dll", rb"libpython3\.(\d{1,2})"):
        m = re.search(pat, data, re.IGNORECASE)
        if m:
            return f"3.{m.group(1).decode('ascii')}"
    return None


def find_primary_payload(payload_dir: Path, original_name: str) -> Path | None:
    candidates: list[tuple[int, Path]] = []
    skip_prefixes = ("python3", "vcruntime", "msvcp", "ucrtbase", "api-ms-", "libcrypto", "libssl")

    for root, _, files in os.walk(payload_dir):
        for fname in files:
            p = Path(root) / fname
            low = fname.lower()
            if low.startswith(skip_prefixes):
                continue
            if low.endswith((".pyd", ".so.1", ".txt", ".json", ".yaml", ".yml", ".dat")):
                continue
            if not (low.endswith((".exe", ".dll", ".so", ".dylib")) or os.access(p, os.X_OK)):
                continue

            score = 0
            if p.stem.lower() == Path(original_name).stem.lower():
                score += 50
            if low.endswith(".exe"):
                score += 20
            elif low.endswith((".dll", ".so", ".dylib")):
                score += 15
            try:
                head = p.read_bytes()
                if b"NUITKA_" in head or b"constant_bin" in head or b"__parents_main__" in head:
                    score += 100
                score += min(len(head) // (1024 * 1024), 30)
            except OSError:
                continue
            candidates.append((score, p))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]
