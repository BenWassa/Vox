# Project Vox

Project Vox is an offline-first language learning tool for Mandarin Chinese (A1 level), featuring spaced repetition vocabulary, grammar tracking, and progress visualization.

## Structure

All active code is in the `webapp/` folder:
- Flask backend (`app.py`, `routes/`, `database.py`, `config.py`)
- HTML/CSS/JS frontend (`templates/`, `static/`)
- Data files (`data/`)
- Documentation (`README.md`, `COMMISSIONING.md`)
- Automated tests (`tests/` at project root)

Legacy desktop code has been removed for clarity and maintainability.

## Features
- Spaced repetition (Leitner 6-box system)
- Grammar tracker
- Dashboard for progress
- Import/export progress as JSON

## Setup
1. Install Python 3.9+ and Flask:
   ```bash
   pip install -r webapp/requirements.txt
   ```
2. Place `vocab_a1.json` and `grammar_a1.json` in the `webapp/data/` directory.
3. Start the server:
   ```bash
   flask --app webapp run
   ```

## Running Tests
1. Install all requirements (including pytest):
   ```bash
   pip install -r webapp/requirements.txt
   ```
2. Run all tests using pytest from the project root:
   ```bash
   pytest
   ```
   This will automatically discover and run all tests in the `tests/` folder.

3. (Recommended) To check test coverage, install coverage and run:
   ```bash
   pip install coverage
   coverage run -m pytest
   coverage report -m
   ```
   This will show you which lines of code are covered by tests.

All tests should pass. If you add new features, please add or update tests in `tests/`.

4. Open your browser to [http://localhost:5000](http://localhost:5000)

## License
- Code: MIT License
- Data: Creative Commons (see data files for details)

---

**Note:** All development should occur in the `webapp/` folder. If you notice any files that should be moved or removed, please update the structure and this README accordingly.