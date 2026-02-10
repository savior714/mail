# Usage Guide

## First Time Setup

1.  **Credentials**:
    - Download `credentials.json` from Google Cloud Console (OAuth 2.0 Client ID - Desktop).
    - Save to project root.

2.  **Environment**:
    - Set `OPENAI_API_KEY` in `.env`.

3.  **Dependencies**:
    - `pip install -r requirements.txt`

## Running the Archivist

### Dry Run (Safe Mode)
Currently, the system only supports Dry Run. It fetches emails but **does not** modify them.

```bash
python -m src.main
```

### verification
After the run, check the generated `dry_run_report_*.json` file.
- `id`: Email ID.
- `category`: Assigned category.
- `method`: How it was classified (`Rule`, `AI`, `Fallback`).
- `reasoning`: Why it was classified that way.

## Rule Tuning
If you see misclassified emails in the report:
1.  Open `src/config.py`.
2.  Add the Sender or distinct Subject keywords to `AppConfig.HARD_RULES`.
3.  Rerun to verify.
