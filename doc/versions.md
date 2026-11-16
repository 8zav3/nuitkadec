# Supported Versions & Targets

## Python Runtimes (`.pyc` Magic & Marshal)

| Python | Magic Int | Magic Bytes (LE) | Frozen `.pyc` | Native NDX |
|---|---|---|---|---|
| 3.8 | 3413 | `55 0d 0d 0a` | Supported | Supported |
| 3.9 | 3425 | `61 0d 0d 0a` | Supported | Supported |
| 3.10 | 3439 | `6f 0d 0d 0a` | Supported | Supported |
| 3.11 | 3495 | `a7 0d 0d 0a` | Supported | Supported |
| 3.12 | 3531 | `cb 0d 0d 0a` | Supported | Supported |
| 3.13 | 3571 | `f3 0d 0d 0a` | Supported | Supported |
| 3.14 | 3627 | `2b 0e 0d 0a` | Supported | Supported |

## Binary Formats & Packaging Modes

| Format | Standalone | Onefile (zstd / uncompressed) | Commercial / Encrypted Blob |
|---|---|---|---|
| **Windows PE** (`.exe` / `.dll`) | Static | Static auto-unpack | `--trigger` (GDB) |
| **Linux ELF** | Static | Static auto-unpack | `--trigger` (`LD_PRELOAD` / GDB) |
| **macOS Mach-O** | Static | Static auto-unpack | `--trigger` (GDB) |

## Nuitka Compiler Compatibility

- **Nuitka 1.x – 3.x**: Full static `.bytecode` extraction + native function/code-object recovery.
- **Nuitka 4.x (stripped MinGW/MSVC)**: Full static `.bytecode` extraction (`.pyc`), full constant pool extraction (`native_constants/*.constants.json`), and loader-entry resolution for `__main__` / `__parents_main__`.
