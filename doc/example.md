# Example Output

Running `decompile.py` on a Nuitka onefile binary:

```bash
python decompile.py app.exe -o app_out
```

Console pipeline output:

```text
[INFO] Target: ...\app.exe
[INFO] Output: ...\app_out
[STEP 1] Checking for Nuitka onefile container...
[OK] Onefile unpacked -> primary payload: onefile_payload\onefile_payload\app.dll
[INFO] Detected Python runtime: 3.11
[STEP 2] Running static devirtualization (.bytecode -> .pyc)...
[OK] Extracting .pyc: Extracted 358/358 (.pyc + .marshal)
[OK] Frozen bytecode: 358 .pyc files in ...\app_out\pyc
[STEP 3] Running NDX native source recovery (native C -> .py -> .pyc)...
[OK] Dev modules (2): __main__, __parents_main__
[OK] Native modules compiled to .pyc: 2 ok, 0 failed -> ...\app_out\pyc\native_recovered
[DONE] All outputs saved in: ...\app_out
```

## Output Directory Layout

```text
app_out/
├── pyc/
│   ├── abc.pyc                 # Standard library & bundled frozen .pyc modules
│   ├── json/                   # Nested packages preserved
│   └── native_recovered/       # Recovered native modules compiled to .pyc
│       └── dev/
│           └── __main__.pyc
├── source/
│   ├── bytecode_decompiled/    # Decompiled bytecode (.py / .dis)
│   └── dev/
│       └── __main__.py         # Recovered native source
├── native_constants/
│   └── __main__.constants.json # Extracted strings, numbers, and constant pools
├── files/                      # Embedded data files (if present)
└── onefile_payload/            # Unpacked onefile container (if onefile)
```
