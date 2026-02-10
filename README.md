# Gmail-AI-Archivist

A smart, cost-efficient personal email archivist that uses a hybrid approach (Regex + AI) to classify and organize your Gmail inbox.

## Features
- **3-Layer Classification**:
    1.  **Hard Rules (Regex)**: Instant classification for known patterns (Notifications, Auth codes).
    2.  **AI (GPT-4o-mini)**: Semantic analysis for unclassified emails (using only snippets to save tokens).
    3.  **Fallback**: Catches ambiguous emails.
- **Dry Run Mode**: Safe simulation that generates a JSON report without modifying your inbox.
- **Cost Efficient**: Optimized to minimize OpenAI API usage.

## Setup

### 1. Prerequisites
- Python 3.10+
- Google Cloud Project with **Gmail API** enabled.
- OpenAI API Key.

### 2. Configuration
1.  Place your `credentials.json` (from Google Cloud) in the project root.
2.  Create `.env` based on `.env.example`:
    ```ini
    OPENAI_API_KEY=sk-...
    ```

### 3. Installation
```bash
pip install -r requirements.txt
```

## Usage (Dry Run)

Run the archivist in simulation mode:

```bash
python -m src.main
```

- **Output**: A JSON file (e.g., `dry_run_report_YYYYMMDD_HHMMSS.json`) containing classification results.
- **View Progress**: A `tqdm` progress bar usually indicates status.

## Project Structure
- `src/`: Source code.
- `conf/` (or root): Configuration files.
- `docs/`: Documentation.
