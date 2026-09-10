Written by Hermes–GPT-6 (AI assistant)

# Optional Torch q3 repair (Windows)

Version-specific workaround for `vr must not be None for symbol q3` in
**Torch 2.13.0+cu132**. Adapted from the context-propagation proposal in
[PyTorch PR #187350](https://github.com/pytorch/pytorch/pull/187350), reported in
[issue #187337](https://github.com/pytorch/pytorch/issues/187337) and
[nunif discussion #731](https://github.com/nagadomi/nunif/discussions/731).
The proposal was closed without merging when this tool was published; this is
not an official PyTorch fix or a general-purpose compiler repair.

`patch.json` holds only the small replacement fragments and LF-normalized SHA256
checksums of the exact original/patched files. The patch forwards existing local
range information through symbolic simplification. It does not suppress compiler
errors, disable compilation, or change model weights.

## Use

Close iw3/conversion processes first. Run with Python 3.10+; no extra dependencies
are needed for the repair tool itself. From this directory, replacing the example
path with the installation folder containing `python/`:

```bat
python repair.py "C:\iw3"
python repair.py "C:\iw3" --apply
python repair.py "C:\iw3" --restore
```

The first command is **read-only** and prints `original` or `patched`. Unknown
versions or source checksums are refused. Apply creates and verifies an adjacent
`symbolic_shapes.py.iw3-q3-original` backup before replacing the source. Reapplying
an already-patched file does nothing. Restore requires a matching backup and
preserves it. Do not delete that backup if you want to restore.

Nothing runs automatically at iw3 startup or on update. A future Torch upgrade can
overwrite the fix; this tool will refuse an unfamiliar build rather than adapt it
blindly. Restart iw3 after applying/restoring and test a short compiled conversion.
This tool does not touch Python developer headers, packages, CUDA, or drivers.

## Tests

```bat
python -B test_repair.py
C:\iw3\python\python.exe -B regression.py
```

The first uses **synthetic files in temporary directories** to test checks,
backup/restore, idempotence and refusals. The second runs the original CPU-only
reproduction plus finite-range and cache-context regression checks against the
Torch belonging to the selected interpreter. It is expected to fail on the
original affected source and pass after repair. It does not test full video
conversion or GPU output; those require separate real conversion testing.

Before publication, the tool was also exercised on a disposable copy of the real
original Torch source: patch output matched the previously tested candidate and
restore recovered the exact original bytes. Earlier local validation of that
candidate included compiled GPU/eager output comparisons and user host conversion
confirmation. These are limited checks, not universal correctness guarantees.

## Separate Python developer-file mismatch

The original installation also had Python 3.10 developer files alongside a 3.12.10
runtime. That was a separate repair, not the cause of the CPU reproduction above.
Use the version-aware upstream `windows_package/torch_compile/install_python_dev.bat`
only after checking it matches your runtime. The matching archive used was
[Python 3.12.10 developer files](https://github.com/nagadomi/nunif/releases/download/python_dev_release/python-3.12.10-dev.zip).
This tool deliberately does not download or install it.

Patch fragments derive from PyTorch and its proposed fix; see the
[PyTorch license](https://github.com/pytorch/pytorch/blob/main/LICENSE).
Keep this optional workaround separate from player bug-fix/feature PRs.
