# AGENTS.md - Gmail-AI-Archivist Context

## 1. Project Identity
- **Name**: Gmail-AI-Archivist
- **Goal**: Automate personal email organization using a cost-efficient, hybrid AI approach.
- **Role**: Python Backend Architect specializing in high-throughput data processing and API integration.

## 2. Tech Stack Setup
- **Language**: Python 3.10+
- **Core Libraries**:
    - `google-api-python-client` (Gmail API)
    - `google-generativeai` (Gemini 1.5 Flash)
    - `pydantic` (Data Validation & Schema)
    - `tqdm` (Progress Visualization)
    - `python-dotenv` (Configuration)

## 3. Architecture Principles
### A. 3-Layer Filtering (Cost Optimization)
1.  **Layer 1 (Hard Rules)**: Regex-based filtering for obvious spam/notifications (Zero Cost).
2.  **Layer 2 (AI Classification)**: LLM (Gemini 1.5 Flash) processing on `Snippet`.
    - **Optimization**: Uses Free Tier with Rate Limiting (15 RPM).
3.  **Layer 3 (Fallback)**: Mark as 'Unclassified' for manual review.

### B. Directory Structure (`src-structure-guardian`)
- **Root**: Config files (`requirements.txt`, `.env`), Documentation (`docs/`), Scripts (`scripts/`).
- **`src/`**: All source code.
    - `src/services/`: Core business logic (`gmail_client`, `classifier`, `reporter`).
    - `src/utils/`: Shared utilities (`logger`).
    - `src/config.py`: Configuration & Constants.
    - `src/main.py`: Entry point.

## 4. Coding Standards
- **Style**: PEP 8 compliant.
- **Type Hinting**: Strict typing (`typing.List`, `typing.Optional`, etc.).
- **Docstrings**: Google Style for all functions and classes.
- **Error Handling**: Graceful failure with logging (no silent crashes).

## 5. Operation Modes
- **Dry Run (Default)**: Read-only access (`gmail.readonly`). Generates JSON report.
- **Real Run**: (Future) Write access to modify labels/archive.

## 6. Key Files
- `src/config.py`: Central place for Categories and Regex Rules.
- `src/services/classifier.py`: The brain of the operation.
- `src/main.py`: The orchestrator.
