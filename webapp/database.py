import json
import os
from dataclasses import dataclass
from typing import List, Optional


def _load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@dataclass
class Card:
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
        self.cards = [_to_card(c) for c in _load_json(os.path.join(data_dir, 'vocab_a1.json'))]
        self.grammar = [_to_grammar(g) for g in _load_json(os.path.join(data_dir, 'grammar_a1.json'))]

    def get_card_to_review(self) -> Optional[Card]:
        return self.cards[0] if self.cards else None

    def update_card_progress(self, card_id: str, correct: bool):
        # Placeholder for state update
        pass

    def get_all_grammar_points(self) -> List[GrammarPoint]:
        return self.grammar

    def update_grammar_status(self, grammar_id: str, status: str):
        for g in self.grammar:
            if g.id == grammar_id:
                g.status = status

    def get_dashboard_stats(self) -> dict:
        return {
            'total_cards': len(self.cards),
            'total_grammar': len(self.grammar)
        }

    def export_progress_to_json(self) -> str:
        data = {
            'cards': [c.__dict__ for c in self.cards],
            'grammar': [g.__dict__ for g in self.grammar],
        }
        return json.dumps(data)

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
    )

def _to_grammar(raw: dict) -> GrammarPoint:
    return GrammarPoint(
        id=str(raw['id']),
        structure=raw['structure'],
        pattern=raw['pattern'],
        explanation=raw['explanation'],
        status=raw.get('status', 'unseen'),
    )
