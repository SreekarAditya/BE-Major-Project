# Rerun the benchmark

The source PDF, reference snapshots and Carlito fonts are included. All writes
stay in this folder. The existing review deck, workbook and references are inputs.

From this folder:

```sh
./.venv/bin/python3 -I run_all.py
```

On a fresh machine with Python and Poppler (`pdftotext`, `pdftoppm`):

```sh
python3 -m venv .venv
./.venv/bin/python3 -I -m pip install --no-cache-dir -r requirements.txt
./.venv/bin/python3 -I run_all.py
```

Individual scripts use paths relative to their own saved location. Run them in
the order listed in `run_all.py`. The isolated Python flag is mandatory for
source processing. No network, optimizer, strength calibration or randomness
other than the seeded beam-cluster bootstrap is needed during analysis.

The pipeline verifies source hashes and protected-file hashes, records timings,
and fails if an unexpected numeric or integrity condition is found. Its success
means the scripts and bookkeeping passed. Scientific limitations remain in
`HUMAN_NEEDED.md` and `REPORT.md`; a successful run does not make them disappear.

`initial_extraction_audit_FAIL.json` keeps the first strict text-token failure.
The text layer joins some adjacent decimal values without spaces. The final
extractor allows exact decimal substrings only in addition to the independent
visual transcription. Source numbers were unchanged.

`digitisation_initial_REJECTED.json` retains an early pixel-read attempt before
overlay review corrected the branch selection. It contained two missed
endpoints and a wrong bare-cycle branch. Only `digitised_static.json` is used
by the benchmark. Unaccepted reloading-branch reads stay in that file with an
explicit excluded status.
