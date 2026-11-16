import subprocess
import sys
from pathlib import Path

ENGINE_SCRIPT = Path(__file__).resolve().parent / "nuitka_decompiler.py"


def engine_exists() -> bool:
    return ENGINE_SCRIPT.exists()


def run_engine(args: list[str]) -> int:
    cmd = [sys.executable, str(ENGINE_SCRIPT), *args]
    proc = subprocess.run(cmd)
    return proc.returncode
