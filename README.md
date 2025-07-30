
# Project Vox

Project Vox is an offline-first language learning tool for Mandarin Chinese (A1 level), featuring spaced repetition vocabulary, grammar tracking, and progress visualization. The project is split into two main versions:

- **Desktop App:** 100% Python, using Tkinter for the GUI. No external dependencies required.
- **Web App:** Modern HTML/CSS/JS frontend with a Python (Flask) backend.

Each version has its own folder and README with setup and usage instructions.

## Features
- Spaced Repetition System (Leitner, 6-box)
- Grammar progress tracker
- Dashboard for mastery stats
- Automatic local backups
- Data import/export

See the README in each subfolder for details on running the desktop or web version.

## Project Structure

```
Vox/
│
├── main.py             # Main app entry point, handles CLI args
├── database.py         # All SQLite database logic (DAL)
├── logic.py            # Pure business logic (e.g., SRS intervals)
├── ui.py               # All tkinter GUI components
├── models.py           # Data classes for vocab/grammar objects
│
├── webapp/             # HTML frontend powered by Flask
│   ├── app.py          # Web server entry point
│   ├── templates/      # HTML templates
│   └── static/         # CSS/JS assets
│
├── data/
│   ├── vocab_a1.json   # Source HSK A1 vocabulary
│   └── grammar_a1.json # Source A1 grammar points
│
├── backups/            # Timestamped database backups are stored here (created on first run)
│
└── progress.db         # The SQLite database file (created on first run)
```

## License
- Python code: MIT License
- Data: Creative Commons (see data files for details)

### 1. Vocab Study

This is your flashcard station.

-   The app shows you the Pinyin and English meaning of a word.
-   Guess the character (`hanzi`).
-   Click **"Reveal Character"** to see the answer.
-   Mark yourself **"✅ Correct"** or **"❌ Incorrect"**.
    -   A correct answer moves the card to the next Leitner box, increasing the time until you see it again.
    -   An incorrect answer moves the card back to the first box, so you review it more frequently.
-   When no cards are due for review, a "finished" message will appear.

### 2. Grammar

This tab lists all the grammar points for your current level.

-   Select one or more grammar points from the list.
-   Use the buttons to update their status to **"Mark as Seen"**, **"Mark as Practiced"**, or **"Mark as Mastered"**.
-   This helps you keep track of what you've learned and what you need to focus on.

### 3. Dashboard

The dashboard gives you a high-level overview of your learning journey.

-   It features progress bars for both **Vocabulary Mastery** and **Grammar Mastery**.
-   Mastery is defined as:
    -   **Vocab:** Cards that have reached the final Leitner box (Box 6).
    -   **Grammar:** Points explicitly marked as "mastered."
-   Click **"Refresh Stats"** to get the latest numbers.

## Command-Line Tools (Export/Import)

You can manage your progress data directly from the command line. This is useful for manual backups or migrating your progress to a new computer.

### Exporting Progress

To save all your learning progress into a single, human-readable file:

```bash
python main.py --export my_progress.json
```

This command creates a file named `my_progress.json` containing the status of all your vocab and grammar items.

### Importing Progress

To load progress from a previously exported JSON file:

**Warning:** This will overwrite your current progress in `progress.db`. The application will automatically create a backup before the import begins.

```bash
python main.py --import my_progress.json
```

## Project Structure

The project is organized into several modules to separate concerns:

```
Vox/
│
├── main.py             # Main app entry point, handles CLI args
├── database.py         # All SQLite database logic (DAL)
├── logic.py            # Pure business logic (e.g., SRS intervals)
├── ui.py               # All tkinter GUI components
├── models.py           # Data classes for vocab/grammar objects
│
├── webapp/             # HTML frontend powered by Flask
│   ├── app.py          # Web server entry point
│   ├── templates/      # HTML templates
│   └── static/         # CSS/JS assets
│
├── data/
│   ├── vocab_a1.json   # Source HSK A1 vocabulary
│   └── grammar_a1.json # Source A1 grammar points
│
├── backups/            # Timestamped database backups are stored here (created on first run)
│
└── progress.db         # The SQLite database file (created on first run)
```

## License

-   **Source Code:** The Python source code in this repository is intended to be licensed under the MIT License. (If the LICENSE file is missing, please add it to clarify the terms.)
-   **Data:** The included language data (`vocab_a1.json`, `grammar_a1.json`) is curated from sources licensed under Creative Commons (CC-BY-SA, CC BY-NC-SA), including the [HSK Academy](https://www.hsk.academy/en/hsk_1) and the [Chinese Grammar Wiki](https://resources.allsetlearning.com/chinese/grammar/).