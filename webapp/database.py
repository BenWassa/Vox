import random
import random
import json
import os
from dataclasses import dataclass
from typing import List, Optional


def _load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@dataclass
class Card:
    box: int = 1
    id: str
    hanzi: str
    pinyin: str
    english: List[str]

@dataclass
class GrammarPoint:
    id: str
    structure: str
    pattern: str
    explanation: str
    status: str = 'unseen'


class DatabaseManager:
    """Very lightweight data loader used by the web API."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.progress_path = os.path.join(data_dir, 'progress.json')
        self.cards = [_to_card(c) for c in _load_json(os.path.join(data_dir, 'vocab_a1.json'))]
        self.grammar = [_to_grammar(g) for g in _load_json(os.path.join(data_dir, 'grammar_a1.json'))]

        # Load progress if available
        progress = {
            'card_boxes': {},
            'grammar_status': {}
        }
        if os.path.exists(self.progress_path):
            try:
                with open(self.progress_path, 'r', encoding='utf-8') as f:
                    progress.update(json.load(f))
            except Exception:
                # Ignore corrupt progress files
                pass

        for c in self.cards:
            c.box = int(progress['card_boxes'].get(c.id, 1))
        for g in self.grammar:
            g.status = progress['grammar_status'].get(g.id, g.status)

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
    )

def _to_grammar(raw: dict) -> GrammarPoint:
    return GrammarPoint(
        id=str(raw['id']),
        structure=raw['structure'],
        pattern=raw['pattern'],
        explanation=raw['explanation'],
        status=raw.get('status', 'unseen'),
    )
