# Vox Web App

This is the web-based version of Project Vox. It uses a Flask backend and a modern HTML/CSS/JS frontend for a more flexible and visually appealing interface.

## Features
- Spaced repetition (Leitner 6-box system)
- Grammar tracker
- Dashboard for progress
- Import/export progress as JSON

## Setup
1. Install Python 3.9+ and Flask:
   ```bash
   pip install -r requirements.txt
   ```
2. Place `vocab_a1.json` and `grammar_a1.json` in the `data/` directory at the project root.
3. Start the server:
   ```bash
   python app.py
   ```
4. Open your browser to [http://localhost:5000](http://localhost:5000)

## License
- Code: MIT License
- Data: Creative Commons (see data files)
