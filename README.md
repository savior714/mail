# Gmail-AI-Archivist (Production Readiness)

A high-performance personal email archivist that organizes years of Gmail data using a "Local-First AI Synthesis" approach. 

## 🚀 Key Features
- **Local-First Architecture**: Syncs metadata to SQLite for ultra-fast local processing without API bottleneck.
- **AI Rule Synthesis**: Uses Gemini 1.5 Flash to classify *Senders* once, creating a persistent `rules.json` that organizes millions of emails.
- **Production Scale-up**: Process data in yearly batches (e.g., `--year 2024`) to handle massive mailboxes safely.
- **Safety Rollback Tags**: Every cloud operation is tagged with `History/Batch_YYYYMMDD` for easy identification and revert.
- **Storage Optimizer**: Automatically flags large emails (>= 5MB) in Shopping/Promo categories as `⚠️_Big_Trash`.
- **Manual Audit Mode**: Edit `rules.json` to override AI decisions; your manual edits are **preserved** forever.

## 🛠️ Setup

### 1. Prerequisites
- Python 3.10+
- Google Cloud Project with **Gmail API** enabled.
- Google AI Studio API Key (Gemini).

### 2. Configuration
1.  Place your OAuth `credentials.json` in the project root.
2.  Set `GOOGLE_API_KEY` in your `.env` file.

### 3. Installation
```bash
pip install -r requirements.txt
```

## 📖 Usage Flow

### Step 1: Sync (Local First)
Sync a specific year to your local database:
```bash
python src/main_local.py --year 2024
```

### Step 2: AI Audit
Generate classification rules for all senders:
- Run **[2] Generate Rules** in the TUI.
- Open `rules.json` and manually audit/edit categories.

### Step 3: Cloud Apply
Push your audited classifications back to Gmail:
- Run **[4] Cloud Sync** in the TUI.
- Watch as labels like `Archived/💰_Finance` are applied via high-speed batch requests.

## 🛠️ Project Structure
- **`src/main.py`**: Primary Production TUI entry point.
- **`scripts/`**: Utility scripts (model listing, etc.).
- **`tests/`**: Unit and integration tests.
- **`archive/`**: Legacy code and dry-run versions.
- **`antigravity-awesome-skills/`**: Curated AI skills library (Replacing legacy `skills/`).

## 📁 Documentation
- [Architecture Guide](docs/ARCHITECTURE.md): Deep dive into the Synthesis pattern.
- [Usage Guide](docs/USAGE.md): Detailed CLI instructions.
