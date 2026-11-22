<div align="center">
  <img src="banner.svg" alt="Nuitka Decompiler — Universal Static Nuitka Decompiler & .pyc Extractor" width="100%">
  <br>

  <p>
    <a href="doc/versions.md"><strong>Supported Versions</strong></a>
    ·
    <a href="doc/example.md"><strong>Example Output</strong></a>
    ·
    <a href="https://github.com/DimaReverse/hexpyrion"><strong>HEXPYRION Engine</strong></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white" alt="Python >=3.10">
    <img src="https://img.shields.io/badge/Targets-PE%20%7C%20ELF%20%7C%20Mach--O-blue" alt="PE | ELF | Mach-O">
  </p>
</div>

---

## Overview

- **Automatic Onefile Unpacking**: Detects Nuitka onefile executables, unpacks embedded payloads statically without executing the binary, and locates the primary compiled target automatically.
- **Universal `.pyc` Extraction & Header Repair**: Extracts all frozen `.bytecode` chunks 1:1 into `.pyc`, auto-detects the embedded CPython version (`3.8–3.14`), and repairs 16-byte CPython magic headers when mismatched.
- **Native Module Recovery (NDX v2)**: Recovers native-compiled first-party modules (such as `__main__` and `__parents_main__`, including stripped Nuitka 4.x builds via loader-entry call resolution) into `.py` and compiles them to `.pyc`.
- **Constant Pool Extraction**: Dumps per-module constant pools (strings, numbers, URLs, imports) into `native_constants/*.constants.json`.
- **Protected / Commercial Fallback (`--trigger`)**: Optional GDB / `LD_PRELOAD` runtime blob capture before any application code executes.

## Documentation

- **[Supported Versions (`doc/versions.md`)](doc/versions.md)** — CPython `.pyc` magic matrix, PE/ELF/Mach-O support, and Nuitka 1.x–4.x notes.
- **[Example Output (`doc/example.md`)](doc/example.md)** — Sample CLI run and output directory structure.

## Installation & Usage

```bash
pip install -r requirements.txt
```

### Decompile any Nuitka binary

```bash
python decompile.py path/to/target.exe
```

### Custom output directory

```bash
python decompile.py path/to/target.exe -o out_dir
```

### CLI Options

| Flag | Description |
|---|---|
| `-o`, `--output` | Output directory (default: `<target>_decompiled`) |
| `--all` | Include bundled third-party libraries in native recovery |
| `--only MODS` | Comma-separated glob filter for native recovery (e.g. `"pkg.*,__main__"`) |
| `--target-python X.Y` | Override auto-detected Python version (`3.8`–`3.14`) |
| `--skip-native` | Extract frozen `.pyc` bytecode only |
| `--trigger` | Runtime blob capture via GDB / `LD_PRELOAD` (for Nuitka Commercial) |
| `--gdb PATH` | Custom `gdb` executable path for `--trigger` |
| `-v`, `--verbose` | Verbose diagnostic output |

## Credits & Origin

- Core Nuitka unpacking & native recovery engine (`src/nuitka_decompiler.py`) taken from [**HEXPYRION**](https://github.com/DimaReverse/hexpyrion) by [**DimaReverse**](https://github.com/DimaReverse), extended with loader-entry call resolution (`_ndx_resolve_loader_entry_call`) for stripped Nuitka 4.x binaries.
- `.pyc` → `.py` decompilation (`src/pyc_decompiler.py`) inspired by [**PyLingual**](https://github.com/syssec-utd/pylingual) (`syssec-utd/pylingual`), modified and optimized into a fast, multi-threaded deterministic bytecode-to-source lifter (zero ML model downloads, Python 3.8–3.14 support).
- Modular CLI pipeline (`src/`) built for universal one-command `.pyc` and `.py` extraction.

## Support & Contributing

Need help with a Nuitka binary, found a bug, or want to contribute?

- **Open an Issue**: [github.com/8zav3/nuitkadec/issues](https://github.com/8zav3/nuitkadec/issues)
- **Open a Pull Request**: [github.com/8zav3/nuitkadec/pulls](https://github.com/8zav3/nuitkadec/pulls)
- **Contact**: [![GitHub](https://img.shields.io/badge/GitHub-8zav3-181717?style=flat&logo=github&logoColor=white)](https://github.com/8zav3) [![Discord](https://img.shields.io/badge/Discord-Contact-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.com/users/1516402914267234382)

> **Authorized use only.** Use this tool only on software you own or are authorized to inspect.

<div align="center">
  <p><strong>nuitkadec</strong> · Universal static Nuitka decompiler &amp; .pyc extractor</p>
  <p><a href="doc/versions.md">Supported Versions</a> · <a href="doc/example.md">Example Output</a> · <a href="https://github.com/8zav3">GitHub</a> · <a href="https://discord.com/users/1516402914267234382">Discord</a></p>
</div>
