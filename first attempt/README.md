# Vox Desktop App (Tkinter)

This is the original desktop version of Project Vox, built entirely with the Python standard library (Python 3.9+). It features a Tkinter GUI for vocabulary study, grammar tracking, and progress visualization.

## Features
- Spaced repetition (Leitner 6-box system)
- Grammar tracker
- Dashboard for progress
- Automatic local backups
- Import/export progress as JSON

## Setup
1. Ensure you have Python 3.9 or newer.
2. Place `vocab_a1.json` and `grammar_a1.json` in the `data/` directory.
3. Run the app:
   ```bash
   python main.py
   ```

## Data
- All progress is stored locally in `progress.db` (created on first run).
- Backups are saved in the `backups/` folder.

## License
- Code: MIT License
- Data: Creative Commons (see data files)
