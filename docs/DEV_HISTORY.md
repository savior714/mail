# Development History

## 2026-02-10 (MVP Implementation)
- **Initialized**: Core logic for Gmail sync and AI classification.
- **Migrated**: Switched to Gemini 1.5 Flash for free-tier sustainability.

## 2026-02-11 (GUI Evolution)
- **Phase 1 (Flet)**: Built a TUI/GUI using Flet. Faced significant layout and compatibility issues with Flet 0.80+.
- **Phase 2 (The Great Web Pivot)**:
    - Abandoned Flet; migrated to **FastAPI + React (Vite)**.
    - Implemented **"Hand-Drawn / Sketch"** aesthetic (Pencil borders, paper textures).
    - Established **Tailwind CSS v4** as the primary styling engine.
    - Integrated **React Router** for robust navigation.
    - Created `start_app.bat` for unified local development.
- **Intelligence & UX**:
    - Implemented **Adaptive Rule Learning**: Feed-back loop that extracts regex from manual fixes.
    - Added **AI Batching/Robustness**: Fixed JSON parsing errors by chunking large classification batches.
    - **UX Polish**: Added detailed logging and startup signals for the rule generation pipeline.
- **Rule Migration**: Executed batch migration for `rules.json` to handle emoji standardization and category renaming.
- **Optimization**: Standardized emojis across UI and rules to prevent duplicate label generation.
