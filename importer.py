"""One-time data ingestion script."""

from database import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    db.populate_from_json(
        vocab_path="data/vocab_a1.json",
        grammar_path="data/grammar_a1.json"
    )
    db.close()
    print("Initial data imported.")

