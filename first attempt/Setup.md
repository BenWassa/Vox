# Language-Reservoir Pilot Setup Guide
Here is the complete initial build of the Language-Reservoir Pilot, dubbed Project Vox.

---

### **Project Structure**

This structure reflects the specified architecture, separating concerns into distinct modules.

```
/language-reservoir
│
├── main.py                 # Main application entry point, CLI handler
├── database.py             # Data Access Layer (DAL) for all SQLite operations
├── logic.py                # Core business logic (SRS intervals, etc.)
├── ui.py                   # All tkinter UI components
├── models.py               # Pydantic-like data classes for clarity
├── importer.py             # One-time data ingestion script
├── README.md               # Instructions for setup and usage
│
├── data/
│   ├── vocab_a1.json       # Source vocabulary data (sample provided)
│   └── grammar_a1.json     # Source grammar data (sample provided)
│
├── backups/                # Automatically created for DB backups
│
└── progress.db             # SQLite database, created on first run
```

---

### **1. Sample Data Files**

Create these two files inside the `data/` directory.

#### `data/vocab_a1.json`
```json
[
  {
    "id": "v001",
    "hanzi": "爱",
    "pinyin": "ài",
    "english": ["to love", "to be fond of"]
  },
  {
    "id": "v002",
    "hanzi": "八",
    "pinyin": "bā",
    "english": ["eight", "8"]
  },
  {
    "id": "v003",
    "hanzi": "爸爸",
    "pinyin": "bàba",
    "english": ["dad", "father"]
  },
  {
    "id": "v004",
    "hanzi": "杯子",
    "pinyin": "bēizi",
    "english": ["cup", "glass"]
  }
]
```

#### `data/grammar_a1.json`
```json
[
  {
    "id": "g001",
    "structure": "Subj. + 是 + Obj.",
    "pattern": "A 是 B",
    "explanation": "The basic structure for equating two nouns, similar to 'to be' in English."
  },
  {
    "id": "g002",
    "structure": "Subj. + 在 + Place",
    "pattern": "在",
    "explanation": "Indicates the location of someone or something."
  },
  {
    "id": "g003",
    "structure": "Subj. + 有 + Obj.",
    "pattern": "有",
    "explanation": "Expresses possession, similar to 'to have' or 'there is/are'."
  }
]
```

---

### **2. Python Source Code**

Here are the contents for each Python file.

#### `models.py`
This file defines simple data structures for type safety and clarity.
```python
# models.py
import datetime
from dataclasses import dataclass, field
from typing import List, Optional

# --- Data From Source Files ---

@dataclass
class VocabItem:
    id: str
    hanzi: str
    pinyin: str
    english: List[str]

@dataclass
class GrammarItem:
    id: str
    structure: str
    pattern: str
    explanation: str
    
# --- Data From Database (including progress) ---

@dataclass
class VocabCard:
    id: int
    hanzi: str
    pinyin: str
    english: str # Stored as a joined string in DB
    box: int = 1
    last_review: Optional[datetime.datetime] = None
    next_review: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class GrammarPoint:
    id: int
    structure: str
    pattern: str
    explanation: str
    status: str = "unseen" # unseen, seen, practiced, mastered
    practice_count: int = 0
```

#### `logic.py`
This module contains the core, state-free business logic, like the SRS intervals.
```python
# logic.py
import datetime

# Leitner system: intervals for boxes 1 through 5
# After getting a card right, it moves to the next box.
# If it's in the last box and correct, it's 'mastered' (moved to box 6).
SRS_INTERVALS_DAYS = {
    1: 1,
    2: 3,
    3: 7,
    4: 14,
    5: 30,
}

def get_next_review_date(current_box: int) -> datetime.datetime:
    """Calculates the next review date based on the current box."""
    now = datetime.datetime.utcnow()
    if current_box in SRS_INTERVALS_DAYS:
        delta = datetime.timedelta(days=SRS_INTERVALS_DAYS[current_box])
        return now + delta
    # If card is mastered (box 6) or new (box 0/1), set review far in the future
    # or handle as a special case. For mastered, we can set a very long delay.
    return now + datetime.timedelta(days=365 * 5)
```

#### `database.py`
The heart of the application, managing all `sqlite3` interaction and backups.
```python
# database.py
import sqlite3
import json
import os
import shutil
import datetime
from typing import List, Optional, Dict, Any

import logic
from models import VocabCard, GrammarPoint

DB_FILE = "progress.db"
BACKUP_DIR = "backups"

class DatabaseManager:
    """Manages all database operations and automated backups."""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Creates database tables if they don't exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS vocab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT UNIQUE NOT NULL,
                    hanzi TEXT NOT NULL,
                    pinyin TEXT NOT NULL,
                    english TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS grammar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT UNIQUE NOT NULL,
                    structure TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    explanation TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS vocab_progress (
                    vocab_id INTEGER UNIQUE NOT NULL,
                    box INTEGER NOT NULL DEFAULT 1,
                    last_review TIMESTAMP,
                    next_review TIMESTAMP NOT NULL,
                    FOREIGN KEY (vocab_id) REFERENCES vocab (id)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS grammar_progress (
                    grammar_id INTEGER UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'unseen',
                    practice_count INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (grammar_id) REFERENCES grammar (id)
                )
            """)

    def create_backup(self):
        """Creates a timestamped backup of the database file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{timestamp}_{os.path.basename(self.db_path)}")
        shutil.copy2(self.db_path, backup_path)
        print(f"Backup created at {backup_path}")

    def populate_from_json(self, vocab_path: str, grammar_path: str):
        """Populates vocab and grammar tables from JSON files if they are empty."""
        with self.conn:
            # Check if vocab table is empty
            cur = self.conn.execute("SELECT COUNT(id) FROM vocab")
            if cur.fetchone()[0] == 0:
                print("Populating vocab from JSON...")
                with open(vocab_path, 'r', encoding='utf-8') as f:
                    vocab_data = json.load(f)
                for item in vocab_data:
                    self.conn.execute(
                        "INSERT INTO vocab (source_id, hanzi, pinyin, english) VALUES (?, ?, ?, ?)",
                        (item['id'], item['hanzi'], item['pinyin'], ", ".join(item['english']))
                    )
                # Initialize progress for all new vocab
                self.conn.execute("""
                    INSERT INTO vocab_progress (vocab_id, next_review)
                    SELECT id, ? FROM vocab WHERE id NOT IN (SELECT vocab_id FROM vocab_progress)
                """, (datetime.datetime.utcnow(),))

            # Check if grammar table is empty
            cur = self.conn.execute("SELECT COUNT(id) FROM grammar")
            if cur.fetchone()[0] == 0:
                print("Populating grammar from JSON...")
                with open(grammar_path, 'r', encoding='utf-8') as f:
                    grammar_data = json.load(f)
                for item in grammar_data:
                    self.conn.execute(
                        "INSERT INTO grammar (source_id, structure, pattern, explanation) VALUES (?, ?, ?, ?)",
                        (item['id'], item['structure'], item['pattern'], item['explanation'])
                    )
                # Initialize progress for all new grammar
                self.conn.execute("""
                    INSERT INTO grammar_progress (grammar_id)
                    SELECT id FROM grammar WHERE id NOT IN (SELECT grammar_id FROM grammar_progress)
                """)

    def get_card_to_review(self) -> Optional[VocabCard]:
        """Fetches the next due vocab card for review."""
        query = """
            SELECT v.id, v.hanzi, v.pinyin, v.english, vp.box, vp.last_review, vp.next_review
            FROM vocab v
            JOIN vocab_progress vp ON v.id = vp.vocab_id
            WHERE vp.next_review <= ?
            ORDER BY vp.next_review
            LIMIT 1
        """
        now_utc = datetime.datetime.utcnow()
        cur = self.conn.execute(query, (now_utc,))
        row = cur.fetchone()
        if not row:
            return None
        return VocabCard(**dict(row))

    def update_card_progress(self, card_id: int, correct: bool):
        """Updates a card's Leitner box and next review date."""
        self.create_backup() # Backup before every state change
        with self.conn:
            cur = self.conn.execute("SELECT box FROM vocab_progress WHERE vocab_id = ?", (card_id,))
            row = cur.fetchone()
            if not row:
                return

            current_box = row[0]
            new_box = current_box + 1 if correct else 1
            if new_box > 6: new_box = 6 # Box 6 is "mastered"

            next_review_date = logic.get_next_review_date(new_box)

            self.conn.execute(
                """
                UPDATE vocab_progress
                SET box = ?, last_review = ?, next_review = ?
                WHERE vocab_id = ?
                """,
                (new_box, datetime.datetime.utcnow(), next_review_date, card_id)
            )

    def get_all_grammar_points(self) -> List[GrammarPoint]:
        """Retrieves all grammar points with their current status."""
        query = """
            SELECT g.id, g.structure, g.pattern, g.explanation, gp.status, gp.practice_count
            FROM grammar g
            JOIN grammar_progress gp ON g.id = gp.grammar_id
            ORDER BY g.id
        """
        cur = self.conn.execute(query)
        return [GrammarPoint(**dict(row)) for row in cur.fetchall()]

    def update_grammar_status(self, grammar_id: int, new_status: str):
        """Updates the status of a single grammar point."""
        self.create_backup()
        with self.conn:
            self.conn.execute(
                "UPDATE grammar_progress SET status = ? WHERE grammar_id = ?",
                (new_status, grammar_id)
            )

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Aggregates progress data for the dashboard."""
        with self.conn:
            # Vocab stats
            total_vocab = self.conn.execute("SELECT COUNT(*) FROM vocab").fetchone()[0]
            mastered_vocab = self.conn.execute("SELECT COUNT(*) FROM vocab_progress WHERE box = 6").fetchone()[0]
            
            # Grammar stats
            total_grammar = self.conn.execute("SELECT COUNT(*) FROM grammar").fetchone()[0]
            mastered_grammar = self.conn.execute("SELECT COUNT(*) FROM grammar_progress WHERE status = 'mastered'").fetchone()[0]

            return {
                "vocab_total": total_vocab,
                "vocab_mastered": mastered_vocab,
                "vocab_mastery_percent": (mastered_vocab / total_vocab * 100) if total_vocab > 0 else 0,
                "grammar_total": total_grammar,
                "grammar_mastered": mastered_grammar,
                "grammar_mastery_percent": (mastered_grammar / total_grammar * 100) if total_grammar > 0 else 0,
            }

    def export_progress_to_json(self) -> str:
        """Exports all progress tables to a JSON string."""
        with self.conn:
            vocab_progress = self.conn.execute("SELECT * FROM vocab_progress").fetchall()
            grammar_progress = self.conn.execute("SELECT * FROM grammar_progress").fetchall()
        
        data = {
            "version": 1,
            "export_date": datetime.datetime.now().isoformat(),
            "vocab_progress": [dict(row) for row in vocab_progress],
            "grammar_progress": [dict(row) for row in grammar_progress],
        }
        return json.dumps(data, indent=2)

    def import_progress_from_json(self, json_data: str):
        """Deletes existing progress and imports from a JSON string."""
        self.create_backup() # Backup before a destructive import
        data = json.loads(json_data)
        
        with self.conn:
            # Clear existing progress
            self.conn.execute("DELETE FROM vocab_progress")
            self.conn.execute("DELETE FROM grammar_progress")
            
            # Import vocab progress
            for row in data['vocab_progress']:
                self.conn.execute(
                    "INSERT INTO vocab_progress (vocab_id, box, last_review, next_review) VALUES (?, ?, ?, ?)",
                    (row['vocab_id'], row['box'], row['last_review'], row['next_review'])
                )
            
            # Import grammar progress
            for row in data['grammar_progress']:
                self.conn.execute(
                    "INSERT INTO grammar_progress (grammar_id, status, practice_count) VALUES (?, ?, ?)",
                    (row['grammar_id'], row['status'], row['practice_count'])
                )
        print("Progress imported successfully.")

    def close(self):
        """Closes the database connection."""
        self.conn.close()
```

#### `ui.py`
A functional `tkinter` UI that wires all the components together.
```python
# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from database import DatabaseManager
from models import VocabCard, GrammarPoint

class App(tk.Tk):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.title("Language Reservoir Pilot")
        self.geometry("800x600")

        self.current_card: VocabCard | None = None

        # --- Main Layout ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Tabs ---
        self.vocab_frame = ttk.Frame(self.notebook)
        self.grammar_frame = ttk.Frame(self.notebook)
        self.dashboard_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.vocab_frame, text="Vocab Study")
        self.notebook.add(self.grammar_frame, text="Grammar")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # --- Build UI for each tab ---
        self.setup_vocab_ui()
        self.setup_grammar_ui()
        self.setup_dashboard_ui()
        
        # --- Initial Load ---
        self.load_next_card()

    def on_tab_change(self, event):
        """Refresh data when a tab is selected."""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        
        if tab_text == "Dashboard":
            self.refresh_dashboard()
        elif tab_text == "Grammar":
            self.refresh_grammar_list()

    def setup_vocab_ui(self):
        """Create the UI for the vocabulary study tab."""
        # --- Card Display ---
        card_area = ttk.LabelFrame(self.vocab_frame, text="Current Card", padding=20)
        card_area.pack(pady=20, padx=20, fill="x")
        
        self.pinyin_label = ttk.Label(card_area, text="Pinyin", font=("Arial", 24))
        self.pinyin_label.pack(pady=5)
        
        self.english_label = ttk.Label(card_area, text="English", font=("Arial", 16))
        self.english_label.pack(pady=5)
        
        self.hanzi_label = ttk.Label(card_area, text="?", font=("Microsoft YaHei", 48, "bold"), foreground="blue")
        self.hanzi_label.pack(pady=20)
        
        self.reveal_button = ttk.Button(card_area, text="Reveal Character", command=self.reveal_card)
        self.reveal_button.pack(pady=10)

        # --- Action Buttons ---
        action_frame = ttk.Frame(self.vocab_frame)
        action_frame.pack(pady=20)

        self.incorrect_button = ttk.Button(action_frame, text="❌ Incorrect", command=lambda: self.mark_card(False))
        self.incorrect_button.grid(row=0, column=0, padx=10)
        
        self.correct_button = ttk.Button(action_frame, text="✅ Correct", command=lambda: self.mark_card(True))
        self.correct_button.grid(row=0, column=1, padx=10)
        
        self.incorrect_button.config(state=tk.DISABLED)
        self.correct_button.config(state=tk.DISABLED)

    def setup_grammar_ui(self):
        """Create the UI for the grammar tracking tab."""
        # --- Grammar List ---
        cols = ("ID", "Pattern", "Status")
        self.grammar_tree = ttk.Treeview(self.grammar_frame, columns=cols, show='headings')
        for col in cols:
            self.grammar_tree.heading(col, text=col)
        self.grammar_tree.pack(expand=True, fill="both", pady=10)

        # --- Action Buttons ---
        grammar_action_frame = ttk.Frame(self.grammar_frame)
        grammar_action_frame.pack(pady=10)
        
        ttk.Button(grammar_action_frame, text="Mark as Seen", command=lambda: self.update_selected_grammar("seen")).pack(side=tk.LEFT, padx=5)
        ttk.Button(grammar_action_frame, text="Mark as Practiced", command=lambda: self.update_selected_grammar("practiced")).pack(side=tk.LEFT, padx=5)
        ttk.Button(grammar_action_frame, text="Mark as Mastered", command=lambda: self.update_selected_grammar("mastered")).pack(side=tk.LEFT, padx=5)
        
        self.refresh_grammar_list()

    def setup_dashboard_ui(self):
        """Create the UI for the dashboard tab."""
        dash_content = ttk.Frame(self.dashboard_frame, padding=20)
        dash_content.pack(expand=True, fill="both")

        # --- Vocab Progress ---
        ttk.Label(dash_content, text="Vocabulary Mastery", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0,10))
        self.vocab_progress = ttk.Progressbar(dash_content, orient="horizontal", length=300, mode="determinate")
        self.vocab_progress.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.vocab_stats_label = ttk.Label(dash_content, text="0/0 (0.0%)")
        self.vocab_stats_label.grid(row=2, column=0, sticky="w", pady=(0, 20))

        # --- Grammar Progress ---
        ttk.Label(dash_content, text="Grammar Mastery", font=("Arial", 16, "bold")).grid(row=3, column=0, sticky="w", pady=(0,10))
        self.grammar_progress = ttk.Progressbar(dash_content, orient="horizontal", length=300, mode="determinate")
        self.grammar_progress.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.grammar_stats_label = ttk.Label(dash_content, text="0/0 (0.0%)")
        self.grammar_stats_label.grid(row=5, column=0, sticky="w", pady=(0, 20))
        
        ttk.Button(dash_content, text="Refresh Stats", command=self.refresh_dashboard).grid(row=6, column=0, pady=20)

    def load_next_card(self):
        """Fetch and display the next card for review."""
        self.current_card = self.db.get_card_to_review()
        self.reveal_button.config(state=tk.NORMAL)
        self.incorrect_button.config(state=tk.DISABLED)
        self.correct_button.config(state=tk.DISABLED)

        if self.current_card:
            self.pinyin_label.config(text=self.current_card.pinyin)
            self.english_label.config(text=self.current_card.english)
            self.hanzi_label.config(text="?", foreground="blue")
        else:
            self.pinyin_label.config(text="No cards due for review.")
            self.english_label.config(text="Great job! Come back later.")
            self.hanzi_label.config(text="🎉")
            self.reveal_button.config(state=tk.DISABLED)

    def reveal_card(self):
        """Show the answer (Hanzi) on the current card."""
        if self.current_card:
            self.hanzi_label.config(text=self.current_card.hanzi, foreground="black")
            self.reveal_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.NORMAL)
            self.correct_button.config(state=tk.NORMAL)

    def mark_card(self, correct: bool):
        """Process the user's answer and load the next card."""
        if self.current_card:
            self.db.update_card_progress(self.current_card.id, correct)
            self.load_next_card()

    def refresh_grammar_list(self):
        """Clear and reload the grammar list from the database."""
        for i in self.grammar_tree.get_children():
            self.grammar_tree.delete(i)
        
        points = self.db.get_all_grammar_points()
        for point in points:
            self.grammar_tree.insert("", "end", iid=str(point.id), values=(point.id, point.pattern, point.status))

    def update_selected_grammar(self, new_status: str):
        """Update the status for the selected grammar item(s)."""
        selected_items = self.grammar_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a grammar point from the list.")
            return

        for item_iid in selected_items:
            grammar_id = int(item_iid)
            self.db.update_grammar_status(grammar_id, new_status)

        self.refresh_grammar_list()

    def refresh_dashboard(self):
        """Fetch latest stats and update the dashboard widgets."""
        stats = self.db.get_dashboard_stats()
        
        # Vocab
        self.vocab_progress['value'] = stats['vocab_mastery_percent']
        self.vocab_stats_label.config(
            text=f"{stats['vocab_mastered']}/{stats['vocab_total']} ({stats['vocab_mastery_percent']:.1f}%)"
        )
        
        # Grammar
        self.grammar_progress['value'] = stats['grammar_mastery_percent']
        self.grammar_stats_label.config(
            text=f"{stats['grammar_mastered']}/{stats['grammar_total']} ({stats['grammar_mastery_percent']:.1f}%)"
        )
```

#### `main.py`
The entry point that handles CLI arguments and launches the application.
```python
# main.py
import argparse
import os

from database import DatabaseManager
from ui import App

def main():
    """Main function to handle CLI and start the application."""
    parser = argparse.ArgumentParser(description="Language-Reservoir: An offline language learning tool.")
    parser.add_argument('--export', metavar='FILE', help='Export user progress to a JSON file.')
    parser.add_argument('--import', dest='import_file', metavar='FILE', help='Import user progress from a JSON file.')

    args = parser.parse_args()

    # --- Initialize Database ---
    # Ensure data directory exists for initial population
    os.makedirs("data", exist_ok=True)
    db_manager = DatabaseManager()
    
    # On first run, populate the static data from JSON
    db_manager.populate_from_json(
        vocab_path="data/vocab_a1.json",
        grammar_path="data/grammar_a1.json"
    )

    # --- Handle CLI Arguments ---
    if args.export:
        print(f"Exporting progress to {args.export}...")
        json_data = db_manager.export_progress_to_json()
        with open(args.export, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print("Export complete.")
        db_manager.close()
        return

    if args.import_file:
        if not os.path.exists(args.import_file):
            print(f"Error: Import file not found at {args.import_file}")
            db_manager.close()
            return
        
        print(f"Importing progress from {args.import_file}...")
        with open(args.import_file, 'r', encoding='utf-8') as f:
            json_data = f.read()
        try:
            db_manager.import_progress_from_json(json_data)
        except Exception as e:
            print(f"An error occurred during import: {e}")
        db_manager.close()
        return

    # --- Run GUI Application ---
    app = App(db_manager)
    app.mainloop()

    # --- Cleanup ---
    db_manager.close()


if __name__ == "__main__":
    main()
```

---

### **3. How to Run the Application**

1.  **Save all files:** Make sure all the files (`main.py`, `database.py`, `logic.py`, `ui.py`, `models.py`, and the JSON files in the `data/` directory) are saved with the correct names in the specified structure.
2.  **Open a terminal or command prompt.**
3.  **Navigate** to the `language-reservoir` directory.
4.  **Run the main script:**
    ```bash
    python main.py
    ```
5.  The application window will appear. On the very first run, it will automatically create `progress.db` and populate it from the JSON files. The `backups/` directory will also be created.

### **How to Use CLI Features**

*   **To Export Progress:**
    ```bash
    python main.py --export my_progress.json
    ```
    This will create a file named `my_progress.json` in your project directory.

*   **To Import Progress:**
    ```bash
    python main.py --import my_progress.json
    ```
    This will wipe the current progress in `progress.db` (after creating a backup) and load the state from `my_progress.json`.

---

This initial build successfully delivers on the core requirements of the pilot: a `sqlite3`-backed, `tkinter`-driven, offline-first application with a functional SRS engine, grammar tracker, backup system, and JSON export/import capabilities, all using only the Python standard library. The next steps would be to implement the writing journal and smoke tests.