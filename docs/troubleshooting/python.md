# Python Troubleshooting

## 2026-02-10: Pylint Import Errors
- **Issue**: `E0401: Unable to import ...` in `src/config.py` and others.
- **Cause**: `src` directory was not a package, and PYTHONPATH was not set correctly during linting.
- **Fix**: 
    1. Added `__init__.py` to `src`, `src/services`, `src/utils`.
    2. Ran pylint with `$env:PYTHONPATH = "."`.

## 2026-02-10: Indentation Errors & Logging
- **Issue**: `W0311: Bad indentation` in `classifier.py`.
- **Issue**: `W1203: Use lazy % formatting`.
- **Fix**: Re-indented code block and replaced f-strings in logger calls with `%s` formatting.
