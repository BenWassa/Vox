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

