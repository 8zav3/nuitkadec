import py_compile
import shutil
import struct
from pathlib import Path

CPYTHON_MAGICS = {
    "3.8":  struct.pack("<H2s", 3413, b"\r\n"),
    "3.9":  struct.pack("<H2s", 3425, b"\r\n"),
    "3.10": struct.pack("<H2s", 3439, b"\r\n"),
    "3.11": struct.pack("<H2s", 3495, b"\r\n"),
    "3.12": struct.pack("<H2s", 3531, b"\r\n"),
    "3.13": struct.pack("<H2s", 3571, b"\r\n"),
    "3.14": struct.pack("<H2s", 3627, b"\r\n"),
}


def detect_marshal_python_version(marshal_bytes: bytes) -> str | None:
    if not marshal_bytes or marshal_bytes[0] not in (0x63, 0xE3):
        return None
    if b"\x97\x00" in marshal_bytes[:64]:
        return "3.11"
    return None


def repair_pyc_headers(pyc_dir: Path, detected_ver: str | None) -> int:
    repaired = 0
    if not pyc_dir.exists():
        return 0

    for pyc_path in pyc_dir.rglob("*.pyc"):
        try:
            raw = pyc_path.read_bytes()
            if len(raw) < 17:
                continue
            magic = raw[:4]
            body = raw[16:]
            target_ver = detect_marshal_python_version(body) or detected_ver
            if target_ver and target_ver in CPYTHON_MAGICS:
                expected_magic = CPYTHON_MAGICS[target_ver]
                if magic != expected_magic:
                    pyc_path.write_bytes(expected_magic + raw[4:16] + body)
                    repaired += 1
        except OSError:
            continue
    return repaired


def compile_recovered_sources_to_pyc(source_dir: Path, pyc_out_dir: Path) -> tuple[int, int]:
    ok = 0
    fail = 0
    if not source_dir.exists():
        return ok, fail

    target_root = pyc_out_dir / "native_recovered"
    for py_file in source_dir.rglob("*.py"):
        rel = py_file.relative_to(source_dir)
        out_pyc = target_root / rel.with_suffix(".pyc")
        out_pyc.parent.mkdir(parents=True, exist_ok=True)
        try:
            py_compile.compile(str(py_file), cfile=str(out_pyc), doraise=True)
            ok += 1
        except Exception:
            fail += 1
    return ok, fail


def copy_tree_pyc(src_pyc_dir: Path, dst_pyc_dir: Path) -> int:
    count = 0
    if not src_pyc_dir.exists():
        return count
    for pyc_file in src_pyc_dir.rglob("*.pyc"):
        rel = pyc_file.relative_to(src_pyc_dir)
        dest = dst_pyc_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pyc_file, dest)
        count += 1
    return count
