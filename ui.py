# ui.py - Complete modern UI implementation
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

from database import DatabaseManager
from models import VocabCard, GrammarPoint

class App(tk.Tk):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.title("Language Reservoir Pilot")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Set application icon and configure window
        self.configure(bg='#f8f9fa')
        
        # Session tracking variables
        self.session_stats = {
            'correct': 0,
            'incorrect': 0,
            'total_today': 0
        }

        self.current_card: VocabCard | None = None

        # Create custom styles first
        self.create_modern_styles()

        # --- Main Layout ---
        self.notebook = ttk.Notebook(self, style='Modern.TNotebook')
        self.notebook.pack(expand=True, fill="both", padx=15, pady=15)

        # --- Tabs ---
        self.vocab_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.grammar_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.dashboard_frame = ttk.Frame(self.notebook, style='Tab.TFrame')

        self.notebook.add(self.vocab_frame, text="📚 Vocab Study")
        self.notebook.add(self.grammar_frame, text="📝 Grammar")
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # --- Build UI for each tab ---
        self.setup_vocab_ui()
        self.setup_grammar_ui()
        self.setup_dashboard_ui()

        # --- Initial Load ---
        self.load_next_card()

    def create_modern_styles(self):
        """Create modern, appealing styles for the entire application."""
        style = ttk.Style()
        style.theme_use('clam')

        # Color palette
        self.colors = {
            'bg_primary': '#f8f9fa',
            'bg_secondary': '#ffffff',
            'bg_card': '#ffffff',
            'bg_shadow': '#e9ecef',
            'accent_blue': '#0066cc',
            'accent_green': '#28a745',
            'accent_red': '#dc3545',
            'accent_orange': '#fd7e14',
            'text_primary': '#212529',
            'text_secondary': '#6c757d',
            'text_light': '#ffffff',
            'hanzi_bg': '#f8f9ff',
            'hover_green': '#218838',
            'hover_red': '#c82333',
            'border_light': '#dee2e6'
        }

        # Configure notebook
        style.configure('Modern.TNotebook', background=self.colors['bg_primary'])
        style.configure('Modern.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Segoe UI', 11, 'bold'))

        # Frame styles
        style.configure('Tab.TFrame', background=self.colors['bg_primary'])
        style.configure('Container.TFrame', background=self.colors['bg_primary'])
        style.configure('Header.TFrame', background=self.colors['bg_primary'])
        style.configure('Card.TFrame', 
                       background=self.colors['bg_card'], 
                       relief='solid', 
                       borderwidth=1,
                       lightcolor=self.colors['border_light'],
                       darkcolor=self.colors['border_light'])
        style.configure('CardContent.TFrame', background=self.colors['bg_card'])
        style.configure('Shadow.TFrame', background=self.colors['bg_shadow'])
        style.configure('Action.TFrame', background=self.colors['bg_primary'])
        style.configure('Stats.TFrame', background=self.colors['bg_primary'])
        style.configure('HanziContainer.TFrame', 
                       background=self.colors['hanzi_bg'], 
                       relief='solid', 
                       borderwidth=1,
                       lightcolor=self.colors['border_light'])

        # Label styles
        style.configure('Header.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['text_primary'])
        style.configure('Streak.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['accent_blue'])
        style.configure('Pinyin.TLabel', 
                       background=self.colors['bg_card'], 
                       foreground=self.colors['accent_blue'])
        style.configure('English.TLabel', 
                       background=self.colors['bg_card'], 
                       foreground=self.colors['text_secondary'])
        style.configure('Hanzi.TLabel', 
                       background=self.colors['hanzi_bg'], 
                       foreground=self.colors['text_primary'])
        style.configure('Stats.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['text_secondary'])

        # Button styles
        style.configure('Reveal.TButton', 
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.colors['text_light'],
                       background=self.colors['accent_blue'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 12])
        style.map('Reveal.TButton',
                 background=[('active', '#0056b3'), ('pressed', '#004494')])

        style.configure('Correct.TButton', 
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['text_light'],
                       background=self.colors['accent_green'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 15])
        style.map('Correct.TButton',
                 background=[('active', self.colors['hover_green']), ('pressed', '#1e7e34')])

        style.configure('Incorrect.TButton', 
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['text_light'],
                       background=self.colors['accent_red'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 15])
        style.map('Incorrect.TButton',
                 background=[('active', self.colors['hover_red']), ('pressed', '#bd2130')])

    def on_tab_change(self, event):
        """Refresh data when a tab is selected."""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")

        if "Dashboard" in tab_text:
            self.refresh_dashboard()
        elif "Grammar" in tab_text:
            self.refresh_grammar_list()

    def setup_vocab_ui(self):
        """Create a modern, visually appealing UI for the vocabulary study tab."""
        
        # Main container with padding
        main_container = ttk.Frame(self.vocab_frame, style='Container.TFrame', padding=30)
        main_container.pack(expand=True, fill='both')
        
        # Configure grid weights for responsive design
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # === HEADER SECTION ===
        header_frame = ttk.Frame(main_container, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 30))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Session title
        self.session_label = ttk.Label(header_frame, text="📚 Vocabulary Study", 
                                     font=('Segoe UI', 18, 'bold'), 
                                     style='Header.TLabel')
        self.session_label.grid(row=0, column=0, sticky='w')
        
        # Session stats
        self.session_stats_label = ttk.Label(header_frame, text="🎯 Session: 0 correct, 0 incorrect", 
                                    font=('Segoe UI', 11), 
                                    style='Streak.TLabel')
        self.session_stats_label.grid(row=0, column=2, sticky='e')
        
        # === FLASHCARD SECTION ===
        # Card container with shadow effect simulation
        card_shadow = ttk.Frame(main_container, style='Shadow.TFrame')
        card_shadow.grid(row=1, column=0, sticky='nsew', pady=(0, 30))
        card_shadow.grid_columnconfigure(0, weight=1)
        card_shadow.grid_rowconfigure(0, weight=1)
        
        # Main card frame
        self.card_frame = ttk.Frame(card_shadow, style='Card.TFrame', padding=40)
        self.card_frame.grid(row=0, column=0, sticky='nsew', padx=3, pady=3)
        self.card_frame.grid_columnconfigure(0, weight=1)
        
        # Card content area
        content_frame = ttk.Frame(self.card_frame, style='CardContent.TFrame')
        content_frame.grid(row=0, column=0, sticky='ew', pady=(0, 30))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Pinyin (larger, prominent)
        self.pinyin_label = ttk.Label(content_frame, text="Pinyin", 
                                    font=('Segoe UI', 28, 'bold'),
                                    style='Pinyin.TLabel')
        self.pinyin_label.grid(row=0, column=0, pady=(0, 15))
        
        # English meaning
        self.english_label = ttk.Label(content_frame, text="English", 
                                     font=('Segoe UI', 18),
                                     style='English.TLabel')
        self.english_label.grid(row=1, column=0, pady=(0, 30))
        
        # Hanzi display area with background
        hanzi_container = ttk.Frame(content_frame, style='HanziContainer.TFrame', padding=30)
        hanzi_container.grid(row=2, column=0, sticky='ew', pady=(0, 30))
        
        self.hanzi_label = ttk.Label(hanzi_container, text="?", 
                                   font=('Microsoft YaHei', 72, 'bold'),
                                   style='Hanzi.TLabel')
        self.hanzi_label.pack()
        
        # Reveal button (styled prominently)
        self.reveal_button = ttk.Button(self.card_frame, text="👁 Reveal Character", 
                                      command=self.reveal_card,
                                      style='Reveal.TButton')
        self.reveal_button.grid(row=1, column=0, pady=(0, 30))
        
        # === ACTION BUTTONS SECTION ===
        action_container = ttk.Frame(main_container, style='Action.TFrame')
        action_container.grid(row=2, column=0, sticky='ew')
        action_container.grid_columnconfigure((0, 1), weight=1)
        
        # Incorrect button (red theme)
        self.incorrect_button = ttk.Button(action_container, 
                                         text="❌ Incorrect\nNeed more practice", 
                                         command=lambda: self.mark_card_with_animation(False),
                                         style='Incorrect.TButton')
        self.incorrect_button.grid(row=0, column=0, sticky='ew', padx=(0, 15))
        
        # Correct button (green theme)
        self.correct_button = ttk.Button(action_container, 
                                       text="✅ Correct\nI knew it!", 
                                       command=lambda: self.mark_card_with_animation(True),
                                       style='Correct.TButton')
        self.correct_button.grid(row=0, column=1, sticky='ew', padx=(15, 0))
        
        # Initially disable action buttons
        self.incorrect_button.config(state=tk.DISABLED)
        self.correct_button.config(state=tk.DISABLED)
        
        # === PROGRESS FOOTER ===
        progress_frame = ttk.Frame(main_container, style='Stats.TFrame')
        progress_frame.grid(row=3, column=0, sticky='ew', pady=(20, 0))
        
        # Simple progress info
        self.progress_info_label = ttk.Label(progress_frame, 
                                           text="💡 Tip: Focus on understanding the context and meaning", 
                                           font=('Segoe UI', 10, 'italic'),
                                           style='Stats.TLabel')
        self.progress_info_label.pack()

    def setup_grammar_ui(self):
        """Create the UI for the grammar tracking tab (enhanced)."""
        # Main container
        grammar_container = ttk.Frame(self.grammar_frame, style='Container.TFrame', padding=20)
        grammar_container.pack(expand=True, fill='both')
        
        # Header
        header = ttk.Label(grammar_container, text="📝 Grammar Points Progress", 
                          font=('Segoe UI', 18, 'bold'), 
                          style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Grammar list with better styling
        cols = ("ID", "Pattern", "Structure", "Status")
        self.grammar_tree = ttk.Treeview(grammar_container, columns=cols, show='headings', height=15)
        
        # Configure column headings and widths
        self.grammar_tree.heading("ID", text="ID")
        self.grammar_tree.heading("Pattern", text="Pattern")
        self.grammar_tree.heading("Structure", text="Structure")
        self.grammar_tree.heading("Status", text="Status")
        
        self.grammar_tree.column("ID", width=80, minwidth=50)
        self.grammar_tree.column("Pattern", width=150, minwidth=100)
        self.grammar_tree.column("Structure", width=300, minwidth=200)
        self.grammar_tree.column("Status", width=120, minwidth=80)
        
        self.grammar_tree.pack(expand=True, fill="both", pady=(0, 20))
        
        # Action buttons with better styling
        grammar_action_frame = ttk.Frame(grammar_container, style='Action.TFrame')
        grammar_action_frame.pack(pady=10)
        
        ttk.Button(grammar_action_frame, text="👀 Mark as Seen", 
                  command=lambda: self.update_selected_grammar("seen")).pack(side=tk.LEFT, padx=5)
        ttk.Button(grammar_action_frame, text="📝 Mark as Practiced", 
                  command=lambda: self.update_selected_grammar("practiced")).pack(side=tk.LEFT, padx=5)
        ttk.Button(grammar_action_frame, text="✅ Mark as Mastered", 
                  command=lambda: self.update_selected_grammar("mastered")).pack(side=tk.LEFT, padx=5)
        
        self.refresh_grammar_list()

    def setup_dashboard_ui(self):
        """Create an enhanced UI for the dashboard tab."""
        # Main container
        dash_container = ttk.Frame(self.dashboard_frame, style='Container.TFrame', padding=30)
        dash_container.pack(expand=True, fill='both')
        
        # Header
        header = ttk.Label(dash_container, text="📊 Learning Dashboard", 
                          font=('Segoe UI', 20, 'bold'), 
                          style='Header.TLabel')
        header.pack(pady=(0, 30))
        
        # Stats grid
        stats_grid = ttk.Frame(dash_container, style='Container.TFrame')
        stats_grid.pack(expand=True, fill='both')
        stats_grid.grid_columnconfigure((0, 1), weight=1)
        
        # === Vocabulary Progress Card ===
        vocab_card = ttk.Frame(stats_grid, style='Card.TFrame', padding=25)
        vocab_card.grid(row=0, column=0, sticky='nsew', padx=(0, 15), pady=(0, 20))
        
        ttk.Label(vocab_card, text="📚 Vocabulary Mastery", 
                 font=('Segoe UI', 16, 'bold'), 
                 style='Header.TLabel').pack(pady=(0, 15))
        
        self.vocab_progress = ttk.Progressbar(vocab_card, orient="horizontal", 
                                            length=300, mode="determinate")
        self.vocab_progress.pack(pady=(0, 10))
        
        self.vocab_stats_label = ttk.Label(vocab_card, text="0/0 (0.0%)", 
                                          font=('Segoe UI', 14),
                                          style='Stats.TLabel')
        self.vocab_stats_label.pack()
        
        # === Grammar Progress Card ===
        grammar_card = ttk.Frame(stats_grid, style='Card.TFrame', padding=25)
        grammar_card.grid(row=0, column=1, sticky='nsew', padx=(15, 0), pady=(0, 20))
        
        ttk.Label(grammar_card, text="📝 Grammar Mastery", 
                 font=('Segoe UI', 16, 'bold'), 
                 style='Header.TLabel').pack(pady=(0, 15))
        
        self.grammar_progress = ttk.Progressbar(grammar_card, orient="horizontal", 
                                              length=300, mode="determinate")
        self.grammar_progress.pack(pady=(0, 10))
        
        self.grammar_stats_label = ttk.Label(grammar_card, text="0/0 (0.0%)", 
                                           font=('Segoe UI', 14),
                                           style='Stats.TLabel')
        self.grammar_stats_label.pack()
        
        # === Today's Activity Card ===
        activity_card = ttk.Frame(stats_grid, style='Card.TFrame', padding=25)
        activity_card.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        ttk.Label(activity_card, text="🎯 Today's Activity", 
                 font=('Segoe UI', 16, 'bold'), 
                 style='Header.TLabel').pack(pady=(0, 15))
        
        activity_stats_frame = ttk.Frame(activity_card, style='CardContent.TFrame')
        activity_stats_frame.pack(fill='x')
        activity_stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.today_cards_label = ttk.Label(activity_stats_frame, text="📊 Cards: 0", 
                                         font=('Segoe UI', 12),
                                         style='Stats.TLabel')
        self.today_cards_label.grid(row=0, column=0)
        
        self.today_accuracy_label = ttk.Label(activity_stats_frame, text="🎯 Accuracy: 0%", 
                                            font=('Segoe UI', 12),
                                            style='Stats.TLabel')
        self.today_accuracy_label.grid(row=0, column=1)
        
        self.streak_label = ttk.Label(activity_stats_frame, text="🔥 Streak: 0 days", 
                                    font=('Segoe UI', 12),
                                    style='Stats.TLabel')
        self.streak_label.grid(row=0, column=2)
        
        # Refresh button
        ttk.Button(stats_grid, text="🔄 Refresh Stats", 
                  command=self.refresh_dashboard,
                  style='Reveal.TButton').grid(row=2, column=0, columnspan=2, pady=20)

    def load_next_card(self):
        """Enhanced card loading with better state management."""
        self.current_card = self.db.get_card_to_review()
        
        # Reset button states
        self.reveal_button.config(state=tk.NORMAL)
        self.incorrect_button.config(state=tk.DISABLED)
        self.correct_button.config(state=tk.DISABLED)
        
        if self.current_card:
            # Display card content
            self.pinyin_label.config(text=self.current_card.pinyin)
            
            # Handle multiple English meanings
            english_text = self.current_card.english
            if len(english_text) > 60:  # Truncate if too long
                english_text = english_text[:57] + "..."
            self.english_label.config(text=english_text)
            
            # Reset hanzi display
            self.hanzi_label.config(text="❓", foreground='#6c757d')
            
            # Update tip
            tips = [
                "💡 Try to visualize the character before revealing",
                "💡 Think about the character's components and radicals",
                "💡 Connect the sound with the meaning",
                "💡 Remember similar characters you've learned",
                "💡 Practice writing the character mentally"
            ]
            import random
            self.progress_info_label.config(text=random.choice(tips))
            
        else:
            # No cards available
            self.pinyin_label.config(text="🎉 All caught up!")
            self.english_label.config(text="Excellent work! No cards due for review right now.")
            self.hanzi_label.config(text="🌟", foreground='#28a745')
            self.reveal_button.config(state=tk.DISABLED)
            self.progress_info_label.config(text="🎯 Come back later for more practice!")

    def reveal_card(self):
        """Enhanced card reveal with better visual feedback."""
        if self.current_card:
            # Show the hanzi with emphasis
            self.hanzi_label.config(text=self.current_card.hanzi, foreground='#212529')
            
            # Update button states
            self.reveal_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.NORMAL)
            self.correct_button.config(state=tk.NORMAL)
            
            # Add a subtle "revealed" animation
            self.animate_reveal()

    def animate_reveal(self):
        """Simple animation for card reveal."""
        # Simple scale effect simulation by temporarily changing font size
        original_font = ('Microsoft YaHei', 72, 'bold')
        larger_font = ('Microsoft YaHei', 76, 'bold')
        
        # Temporarily make it slightly larger
        self.hanzi_label.config(font=larger_font)
        self.after(150, lambda: self.hanzi_label.config(font=original_font))

    def mark_card_with_animation(self, correct: bool):
        """Enhanced card marking with visual feedback."""
        if not self.current_card:
            return
        
        # Update session stats
        if correct:
            self.session_stats['correct'] += 1
        else:
            self.session_stats['incorrect'] += 1
        
        # Update session display
        self.update_session_display()
        
        # Provide visual feedback
        if correct:
            self.show_feedback("✅ Excellent!", "#28a745")
        else:
            self.show_feedback("❌ Keep practicing!", "#dc3545")
        
        # Update the card in database
        self.db.update_card_progress(self.current_card.id, correct)
        
        # Load next card after brief delay
        self.after(1200, self.load_next_card)

    def show_feedback(self, message: str, color: str):
        """Show temporary feedback message with fade effect."""
        # Create temporary feedback label
        feedback = ttk.Label(self.card_frame, text=message, 
                            font=('Segoe UI', 18, 'bold'),
                            background='#ffffff', foreground=color)
        feedback.grid(row=2, column=0, pady=15)
        
        # Remove feedback after delay
        self.after(1000, feedback.destroy)

    def update_session_display(self):
        """Update the session statistics display."""
        total = self.session_stats['correct'] + self.session_stats['incorrect']
        if total > 0:
            accuracy = (self.session_stats['correct'] / total) * 100
            self.session_stats_label.config(
                text=f"🎯 Session: {self.session_stats['correct']} correct, "
                     f"{self.session_stats['incorrect']} incorrect ({accuracy:.0f}%)"
            )
        else:
            self.session_stats_label.config(text="🎯 Session: Ready to start!")

    def mark_card(self, correct: bool):
        """Legacy method - redirects to new animated version."""
        self.mark_card_with_animation(correct)

    def refresh_grammar_list(self):
        """Clear and reload the grammar list from the database with enhanced display."""
        for i in self.grammar_tree.get_children():
            self.grammar_tree.delete(i)

        points = self.db.get_all_grammar_points()
        for point in points:
            # Add status emoji for better visual feedback
            status_display = {
                'unseen': '⚪ unseen',
                'seen': '🔵 seen', 
                'practiced': '🟡 practiced',
                'mastered': '🟢 mastered'
            }.get(point.status, point.status)
            
            self.grammar_tree.insert("", "end", iid=str(point.id), 
                                   values=(point.id, point.pattern, point.structure, status_display))

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
        """Fetch latest stats and update the dashboard widgets with enhanced display."""
        stats = self.db.get_dashboard_stats()

        # Vocab progress
        self.vocab_progress['value'] = stats['vocab_mastery_percent']
        self.vocab_stats_label.config(
            text=f"{stats['vocab_mastered']}/{stats['vocab_total']} mastered\n"
                 f"({stats['vocab_mastery_percent']:.1f}%)"
        )

        # Grammar progress  
        self.grammar_progress['value'] = stats['grammar_mastery_percent']
        self.grammar_stats_label.config(
            text=f"{stats['grammar_mastered']}/{stats['grammar_total']} mastered\n"
                 f"({stats['grammar_mastery_percent']:.1f}%)"
        )
        
        # Today's activity (simplified for now)
        total_session = self.session_stats['correct'] + self.session_stats['incorrect']
        session_accuracy = 0
        if total_session > 0:
            session_accuracy = (self.session_stats['correct'] / total_session) * 100
            
        self.today_cards_label.config(text=f"📊 Cards: {total_session}")
        self.today_accuracy_label.config(text=f"🎯 Accuracy: {session_accuracy:.0f}%")
        # Note: Streak calculation would require additional database tracking