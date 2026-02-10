# Next Steps

## Immediate (MVP Verification - User)
- [ ] **Config**: User to provide `credentials.json` and `.env`.
- [ ] **Dry Run**: Run `python -m src.main` and review report.
- [ ] **Rule Tuning**: Update `src/config.py` based on report results.

## Phase 2 (Real Run)
- [ ] Implement `LabelManager` to create/apply Gmail labels.
- [ ] Add `Analysis` mode to run on full inbox (batch processing).
- [ ] Implement Archive/Trash logic.

## Phase 3 (Optimization)
- [ ] Implement Batch API for Gmail (reduce HTTP calls).
- [ ] Add AsyncIO support for concurrent processing.
