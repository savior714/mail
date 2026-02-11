# Gmail-AI-Archivist (Pencil Edition)

A high-performance personal email archivist that organizes years of Gmail data using a "Local-First AI Synthesis" approach. Now featuring a unique **Hand-Drawn / Sketch** web interface.

## 🚀 Key Features
- **Modern Web Interface**: Decoupled React (Vite) frontend with a beautiful, hand-drawn "Pencil" aesthetic.
- **FastAPI Backend**: Robust Python API exposing core email organization logic.
- **Tailwind v4 Powered**: Utilizing the latest CSS engine for high-performance rendering.
- **Local-First Architecture**: Syncs metadata to SQLite for ultra-fast local processing.
- **AI Rule Synthesis**: Uses Gemini 1.5 Flash to classify senders and create persistent rules.
- **Storage Optimizer**: Automatically flags large emails (>= 5MB) as `⚠️_Big_Trash`.

## 🛠️ Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud Project with **Gmail API** enabled.
- Google AI Studio API Key (Gemini).

### 2. Configuration
1.  Place your OAuth `credentials.json` in the project root.
2.  Set `GOOGLE_API_KEY` in your `.env` file.

### 3. Quick Start (Windows)
Double-click `start_app.bat` to launch both Backend and Frontend simultaneously.

### 4. Manual Installation
**Backend**:
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## 🛠️ Project Structure
- **`src/api/`**: FastAPI implementation.
- **`src/services/`**: Core business logic (Syncer, Rule Generator, Applier).
- **`frontend/`**: React + Vite + Tailwind v4 web application.
- **`docs/`**: Detailed documentation and architecture guides.
- **`legacy_ui/`**: Archived Flet TUI/GUI implementation.

## 📁 Documentation
- [Architecture Guide](docs/ARCHITECTURE.md): Web architecture and Synthesis pattern.
- [Dev History](docs/DEV_HISTORY.md): Evolution from TUI to Sketchy Web UI.
- [Next Steps](docs/NEXT_STEPS.md): Future roadmap.
