

# Project Vox

Project Vox is an offline-first language learning tool for Mandarin Chinese (A1 level), featuring spaced repetition vocabulary, grammar tracking, and progress visualization.

## Structure

All active code is now in the `webapp/` folder, which contains:

- Flask backend (`app.py`, `routes/`, `database.py`, `config.py`)
- HTML/CSS/JS frontend (`templates/`, `static/`)
- Data files (`data/`)
- Commissioning and documentation (`README.md`, `COMMISSIONING.md`)
- Automated tests (`tests/` at project root)

Legacy desktop code has been removed for clarity and maintainability.

## How to Use

See `webapp/README.md` for all setup, usage, and contribution details.

## License
- Python code: MIT License
- Data: Creative Commons (see data files for details)

---

**Note:** The repository has been reorganized for clarity. All development should occur in the `webapp/` folder. If you notice any files that should be moved or removed, please update the structure and this README accordingly.