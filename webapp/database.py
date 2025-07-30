import random
import random
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict


def _load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@dataclass
class Card:
    id: str
    hanzi: str
    pinyin: str
    english: List[str]
    box: int = 1
    status: str = 'new'  # new, learning, review, mastered
    streak: int = 0

@dataclass
class GrammarPoint:
    id: str
    structure: str
    pattern: str
    explanation: str
    status: str = 'unseen'


class DatabaseManager:
    """Data loader and vocab progress manager for Project Vox."""

    ACTIVE_POOL_SIZE = 3  # Number of active vocab items at a time
    STREAK_TO_REVIEW = 3  # Correct answers to move from learning to review
    STREAK_TO_MASTERED = 2  # Correct answers to move from review to mastered

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.progress_path = os.path.join(data_dir, 'progress.json')
        self.cards = [_to_card(c) for c in _load_json(os.path.join(data_dir, 'vocab_a1.json'))]
        self.grammar = [_to_grammar(g) for g in _load_json(os.path.join(data_dir, 'grammar_a1.json'))]

        # Load progress if available
        progress = {
            'card_status': {},  # id: {status, streak}
            'grammar_status': {}
        }
        if os.path.exists(self.progress_path):
            try:
                with open(self.progress_path, 'r', encoding='utf-8') as f:
                    progress.update(json.load(f))
            except Exception:
                pass

        for c in self.cards:
            state = progress['card_status'].get(c.id, {})
            c.status = state.get('status', 'new')
            c.streak = int(state.get('streak', 0))
        for g in self.grammar:
            g.status = progress['grammar_status'].get(g.id, g.status)

    def _save_progress(self):
        data = {
            'card_status': {c.id: {'status': c.status, 'streak': c.streak} for c in self.cards},
            'grammar_status': {g.id: g.status for g in self.grammar},
        }
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def get_active_vocab(self) -> List[Card]:
        """Return the current active pool of vocab items (learning or review, in ID order)."""
        # Always keep pool at ACTIVE_POOL_SIZE, prioritizing 'learning', then 'review', then unlock new
        pool = [c for c in self.cards if c.status in ('learning', 'review')]
        # If pool is too small, unlock new items by ID order
        if len(pool) < self.ACTIVE_POOL_SIZE:
            needed = self.ACTIVE_POOL_SIZE - len(pool)
            new_items = [c for c in self.cards if c.status == 'new']
            new_items = sorted(new_items, key=lambda c: c.id)[:needed]
            for c in new_items:
                c.status = 'learning'
                c.streak = 0
            pool += new_items
            self._save_progress()
        # Always return in ID order
        return sorted(pool, key=lambda c: c.id)

    def get_card_to_review(self) -> Optional[Card]:
        """Return a card from the active pool, prioritizing learning, then review, in ID order."""
        pool = self.get_active_vocab()
        learning = [c for c in pool if c.status == 'learning']
        review = [c for c in pool if c.status == 'review']
        if learning:
            return learning[0]
        elif review:
            return review[0]
        return None

    def update_card_progress(self, card_id: str, correct: bool):
        for c in self.cards:
            if c.id == card_id:
                if c.status == 'learning':
                    if correct:
                        c.streak += 1
                        if c.streak >= self.STREAK_TO_REVIEW:
                            c.status = 'review'
                            c.streak = 0
                    else:
                        c.streak = 0
                elif c.status == 'review':
                    if correct:
                        c.streak += 1
                        if c.streak >= self.STREAK_TO_MASTERED:
                            c.status = 'mastered'
                            c.streak = 0
                    else:
                        c.status = 'learning'
                        c.streak = 0
                # mastered: do nothing for now
                break
        self._save_progress()

    def _save_progress(self):
        data = {
            'card_boxes': {c.id: c.box for c in self.cards},
            'grammar_status': {g.id: g.status for g in self.grammar},
        }
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def get_card_to_review(self) -> Optional[Card]:
        if not self.cards:
            return None
        # Select randomly among cards in the lowest box (simple Leitner system)
        min_box = min(c.box for c in self.cards)
        candidates = [c for c in self.cards if c.box == min_box]
        return random.choice(candidates)

    def update_card_progress(self, card_id: str, correct: bool):
        for c in self.cards:
            if c.id == card_id:
                if correct:
                    c.box = min(c.box + 1, 6)
                else:
                    c.box = 1
                break
        self._save_progress()

    def get_all_grammar_points(self) -> List[GrammarPoint]:
        return self.grammar

    def update_grammar_status(self, grammar_id: str, status: str):
        for g in self.grammar:
            if g.id == grammar_id:
                g.status = status
                self._save_progress()

    def get_dashboard_stats(self) -> dict:
        return {
            'total_cards': len(self.cards),
            'total_grammar': len(self.grammar),
            'box_counts': {
                str(i): sum(1 for c in self.cards if c.box == i)
                for i in range(1, 7)
            },
            'grammar_status_counts': {
                status: sum(1 for g in self.grammar if g.status == status)
                for status in ['unseen', 'seen', 'practiced', 'mastered']
            }
        }

    def export_progress_to_json(self) -> str:
        data = {
            'cards': [c.__dict__ for c in self.cards],
            'grammar': [g.__dict__ for g in self.grammar],
        }
        return json.dumps(data, ensure_ascii=False)

    def import_progress_from_json(self, json_data: str):
        data = json.loads(json_data)
        # Overwrite local state for simplicity
        self.cards = [_to_card(c) for c in data.get('cards', [])]
        self.grammar = [_to_grammar(g) for g in data.get('grammar', [])]


def _to_card(raw: dict) -> Card:
    return Card(
        id=str(raw['id']),
        hanzi=raw['hanzi'],
        pinyin=raw['pinyin'],
        english=raw['english'],
        box=int(raw.get('box', 1)),
        status=raw.get('status', 'new'),
        streak=int(raw.get('streak', 0)),
    )

def _to_grammar(raw: dict) -> GrammarPoint:
    return GrammarPoint(
        id=str(raw['id']),
        structure=raw['structure'],
        pattern=raw['pattern'],
        explanation=raw['explanation'],
        status=raw.get('status', 'unseen'),
    )
