Run from any directory using the existing Job B1 Python environment (read-only):

```sh
/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08_benchmark_ozturkoglu2024/.venv/bin/python -B -I /Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08b_benchmark_pesic2015/run_all.py
```

The vector-path QA uses bundled isolated Python with pdfplumber at `/Users/sreekaraditya/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

Requires NumPy, Pillow, Matplotlib and Poppler (`pdftotext`, `pdftoppm`) on PATH. Carlito fonts are copied locally. Each named script can also run separately with `-B -I` after its predecessors. Fixed manual pixel picks are source inputs in `digitise.py`; regenerating an overlay does not establish correctness automatically. `QA.json` checks runtime and unchanged files outside this directory. Reading intervals are bounded sensitivity estimates, not population confidence intervals. Missing inputs remain missing on every rerun.
