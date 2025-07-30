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
    english: str  # Stored as a joined string in DB
    box: int = 1
    last_review: Optional[datetime.datetime] = None
    next_review: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class GrammarPoint:
    id: int
    structure: str
    pattern: str
    explanation: str
    status: str = "unseen"  # unseen, seen, practiced, mastered
    practice_count: int = 0
