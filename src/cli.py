import argparse
import json
import shutil
import sys
from pathlib import Path

from src.detect import detect_python_version_from_binary, find_primary_payload
from src.engine import ENGINE_SCRIPT, engine_exists, run_engine
from src.pyc_decompiler import decompile_pyc_tree
from src.pyc_repair import (
    compile_recovered_sources_to_pyc,
    copy_tree_pyc,
    repair_pyc_headers,
)


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Universal Nuitka Decompiler — extracts .pyc and recovers .py source from any Nuitka binary."
    )
    parser.add_argument("target", help="Path to Nuitka-compiled binary (.exe, .dll, ELF, Mach-O)")
    parser.add_argument("-o", "--output", default=None, help="Output directory (default: <target_stem>_decompiled)")
    parser.add_argument("--all", action="store_true", help="Recover all modules including bundled third-party libraries")
    parser.add_argument("--only", default=None, help="Comma-separated module glob filter for native recovery")
    parser.add_argument("--target-python", default=None, help="Force Python version X.Y (auto-detected if omitted)")
    parser.add_argument("--trigger", action="store_true", help="Use GDB/LD_PRELOAD runtime blob capture (for Nuitka Commercial)")
    parser.add_argument("--gdb", default=None, help="Path to gdb executable for --trigger")
    parser.add_argument("--skip-native", action="store_true", help="Only extract frozen .pyc bytecode (skip NDX native recovery)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not engine_exists():
        log("ERR", f"Core engine not found: {ENGINE_SCRIPT}")
        return 1

    target = Path(args.target).resolve()
    if not target.exists():
        log("ERR", f"Target not found: {target}")
        return 1

    out_dir = Path(args.output).resolve() if args.output else Path.cwd() / f"{target.stem}_decompiled"
    out_dir.mkdir(parents=True, exist_ok=True)

    devirt_dir = out_dir / "_devirt_work"
    source_dir = out_dir / "source"
    pyc_dir = out_dir / "pyc"
    pyc_dir.mkdir(parents=True, exist_ok=True)

    log("INFO", f"Target: {target}")
    log("INFO", f"Output: {out_dir}")

    work_target = target
    onefile_dir = out_dir / "onefile_payload"
    log("STEP 1", "Checking for Nuitka onefile container...")
    run_engine([str(target), "--onefile-unpack", "-o", str(onefile_dir), "--no-banner"])
    if onefile_dir.exists() and any(onefile_dir.iterdir()):
        primary = find_primary_payload(onefile_dir, target.name)
        if primary:
            work_target = primary
            log("OK", f"Onefile unpacked -> primary payload: {work_target.relative_to(out_dir)}")
        else:
            log("WARN", "Onefile extracted files, but no primary Nuitka binary identified; using original target.")
    else:
        if onefile_dir.exists() and not any(onefile_dir.iterdir()):
            onefile_dir.rmdir()
        log("OK", "Standalone binary (not onefile).")

    py_ver = args.target_python or detect_python_version_from_binary(work_target)
    if py_ver:
        log("INFO", f"Detected Python runtime: {py_ver}")
    else:
        log("WARN", "Could not auto-detect Python version; engine will infer from binary.")

    log("STEP 2", "Running static devirtualization (.bytecode -> .pyc)...")
    devirt_args = [str(work_target), "--devirt", "--devirt-decompile", "-o", str(devirt_dir), "--no-banner"]
    if py_ver:
        devirt_args += ["--target-python", py_ver]
    if args.trigger:
        devirt_args.append("--trigger")
        if args.gdb:
            devirt_args += ["--trigger-gdb", args.gdb]

    run_engine(devirt_args)

    extracted_pyc = copy_tree_pyc(devirt_dir / "bytecode_pyc", pyc_dir)
    repaired = repair_pyc_headers(pyc_dir, py_ver)
    log("OK", f"Frozen bytecode: {extracted_pyc} .pyc files in {pyc_dir}" + (f" ({repaired} headers repaired)" if repaired else ""))

    pyc_py_ok, pyc_py_fail = decompile_pyc_tree(pyc_dir, source_dir / "pyc_decompiled")
    log("OK", f"Decompiled .pyc -> .py: {pyc_py_ok} ok, {pyc_py_fail} failed -> {source_dir / 'pyc_decompiled'}")

    if (devirt_dir / "devirt_files").exists():
        shutil.copytree(devirt_dir / "devirt_files", out_dir / "files", dirs_exist_ok=True)
    if (devirt_dir / "devirt_modules").exists():
        shutil.copytree(devirt_dir / "devirt_modules", out_dir / "native_constants", dirs_exist_ok=True)
    if (devirt_dir / "devirt_source").exists():
        shutil.copytree(devirt_dir / "devirt_source", source_dir / "bytecode_disasm", dirs_exist_ok=True)

    manifest_path = devirt_dir / "DEVIRT_MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("bytecode_modules", 0) == 0 and not manifest.get("native_modules"):
                log("WARN", "No static modules recovered (possible Nuitka Commercial / encrypted blob). Re-run with --trigger.")
        except Exception:
            pass

    if not args.skip_native:
        log("STEP 3", "Running NDX native source recovery (native C -> .py -> .pyc)...")
        ndx_args = ["--ndx", str(work_target), "-o", str(source_dir)]
        if not args.all and not args.only:
            ndx_args.append("--dev-only")
        if args.only:
            ndx_args += ["--only", args.only]
        if py_ver:
            ndx_args += ["--target-python", py_ver]
        if args.verbose:
            ndx_args.append("-v")

        run_engine(ndx_args)
        native_pyc_ok, native_pyc_fail = compile_recovered_sources_to_pyc(source_dir, pyc_dir)
        log("OK", f"Native modules compiled to .pyc: {native_pyc_ok} ok, {native_pyc_fail} failed -> {pyc_dir / 'native_recovered'}")

    log("DONE", f"All outputs saved in: {out_dir}")
    log("DONE", f"  .pyc files : {pyc_dir}")
    log("DONE", f"  .py source : {source_dir}")
    return 0
