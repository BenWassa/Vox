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
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vocab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT UNIQUE NOT NULL,
                    hanzi TEXT NOT NULL,
                    pinyin TEXT NOT NULL,
                    english TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS grammar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT UNIQUE NOT NULL,
                    structure TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    explanation TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vocab_progress (
                    vocab_id INTEGER UNIQUE NOT NULL,
                    box INTEGER NOT NULL DEFAULT 1,
                    last_review TIMESTAMP,
                    next_review TIMESTAMP NOT NULL,
                    FOREIGN KEY (vocab_id) REFERENCES vocab (id)
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS grammar_progress (
                    grammar_id INTEGER UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'unseen',
                    practice_count INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (grammar_id) REFERENCES grammar (id)
                )
                """
            )

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
                self.conn.execute(
                    """
                    INSERT INTO vocab_progress (vocab_id, next_review)
                    SELECT id, ? FROM vocab WHERE id NOT IN (SELECT vocab_id FROM vocab_progress)
                """,
                    (datetime.datetime.utcnow(),)
                )

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
                self.conn.execute(
                    """
                    INSERT INTO grammar_progress (grammar_id)
                    SELECT id FROM grammar WHERE id NOT IN (SELECT grammar_id FROM grammar_progress)
                """
                )

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
        self.create_backup()  # Backup before every state change
        with self.conn:
            cur = self.conn.execute("SELECT box FROM vocab_progress WHERE vocab_id = ?", (card_id,))
            row = cur.fetchone()
            if not row:
                return

            current_box = row[0]
            new_box = current_box + 1 if correct else 1
            if new_box > 6:
                new_box = 6  # Box 6 is "mastered"

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
        self.create_backup()  # Backup before a destructive import
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
