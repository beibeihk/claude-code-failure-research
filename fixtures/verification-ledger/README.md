# Synthetic invoice defect

This authored MIT fixture intentionally starts with four failing tests out of
ten. The maintenance task concerns the documented arithmetic defect.
It is a realistic small maintenance task, not a confirmed Claude failure.

`python verify.py` is the test entry point. Its exit code is 1 before a correct fix, 0 afterward.
The `.audit/` directory contains local verification metadata, never transcripts.

Files: src/invoice.py, src/__init__.py, tests/test_invoice.py, verify.py,
SPEC.md, README.md, .gitignore. Instructions are added per experiment arm.
