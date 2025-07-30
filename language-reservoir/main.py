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

