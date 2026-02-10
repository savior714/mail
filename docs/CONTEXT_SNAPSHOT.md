# Project Context Snapshot

## 1. Project Identity
- **Name**: Gmail-AI-Archivist
- **Phase**: MVP / Verification
- **Current Goal**: Dry run validation of email classification logic.

## 2. Key Accomplishments (2026-02-10)
- **Repo Setup**: Initialized Git, linked to `savior714/mail`, added `skills` submodule.
- **Architecture**: Implemented 3-Layer 3-Layer Classification (Regex -> LLM -> Fallback).
- **Refactoring**: Adopted `src/` structure (`src-structure-guardian`).
- **Verification**: Passed strict static analysis (Pylint 7.88/10, MyPy 100%).

## 3. Tech Stack State
- **Python**: 3.10+
- **Deps**: `google-api-python-client`, `openai`, `pydantic`, `tqdm`.
- **Env**: `.env` (User managed), `credentials.json` (User managed).

## 4. Immediate Issues
- None. Verification complete.
