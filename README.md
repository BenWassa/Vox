# Project Vox: Language-Reservoir Pilot

**Project Vox** is a self-contained, offline-first desktop application for language learning, built entirely with the Python standard library. This pilot version focuses on Mandarin Chinese (A1 level) and provides tools for vocabulary drilling, grammar tracking, and progress visualization.

The core mission is to provide a powerful, private, and portable learning tool that runs on any machine with Python, without requiring external dependencies, web servers, or cloud accounts. Your data stays with you.


*(Conceptual mockup of the running application)*

## Key Features

-   **Spaced Repetition System (SRS):** Uses a five-box Leitner system to efficiently drill vocabulary. Cards you know less appear more frequently.
-   **Grammar Tracker:** Log and track your progress through a list of essential grammar points, marking them as "seen," "practiced," or "mastered."
-   **Dashboard:** A simple dashboard visualizes your mastery percentage for both vocabulary and grammar, keeping you motivated.
-   **100% Offline & Private:** The entire application runs locally. Your progress data never leaves your machine.
-   **Zero Dependencies:** Runs on any standard Python 3.9+ installation. No `pip install` required.
-   **Automatic Backups:** Every time you update a card or grammar point, the application automatically saves a timestamped backup of your progress.
-   **Portable Progress:** Easily export your entire learning history to a single JSON file and import it on another machine.

## Requirements

-   Python 3.9 or newer.

That's it!

## Setup and Installation

No installation is needed. Just clone this repository or download the source code.

1.  **Get the code:**
    ```bash
    git clone https://github.com/BenWassa/Vox.git
    cd Vox
    ```
2.  **Ensure you have the data files:** The repository should include `vocab_a1.json` and `grammar_a1.json` inside the `data/` directory. If not, create the directory and place them there.

## How to Run the Application

To start the graphical user interface (GUI), run `main.py` from your terminal:

```bash
python main.py
```

On the very first run, the application will automatically:
1.  Create the `progress.db` SQLite database file.
2.  Create the `backups/` directory.
3.  Populate the database with the initial vocabulary and grammar from the `data/` directory.

## Using the Application

The application is organized into three tabs:

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
/language-reservoir
│
├── main.py             # Main app entry point, handles CLI args
├── database.py         # All SQLite database logic (DAL)
├── logic.py            # Pure business logic (e.g., SRS intervals)
├── ui.py               # All tkinter GUI components
├── models.py           # Data classes for vocab/grammar objects
│
├── data/
│   ├── vocab_a1.json   # Source HSK A1 vocabulary
│   └── grammar_a1.json # Source A1 grammar points
│
├── backups/            # Timestamped database backups are stored here
│
└── progress.db         # The SQLite database file
```

## License

-   **Source Code:** The Python source code in this repository is licensed under the [MIT License](LICENSE).
-   **Data:** The included language data (`vocab_a1.json`, `grammar_a1.json`) is curated from sources licensed under Creative Commons (CC-BY-SA, CC BY-NC-SA), including the [HSK Academy](https://www.hsk.academy/en/hsk_1) and the [Chinese Grammar Wiki](https://resources.allsetlearning.com/chinese/grammar/).