# Vox

Project Vox is a self-directed language learning tool focused on grammar mastery, vocabulary retention, and output-based practice. The application runs entirely offline and stores progress in an SQLite database.

## Getting Started

1. Ensure you have Python installed (version 3.10 or later).
2. Navigate to the `language-reservoir` directory.
3. Run the application:
   ```bash
   python main.py
   ```
   On first launch the program creates `progress.db` and loads vocabulary and grammar from the JSON files in `data/`. A `backups/` directory is also created automatically.

### Export Progress
```
python main.py --export my_progress.json
```
This writes your current progress to `my_progress.json`.

### Import Progress
```
python main.py --import my_progress.json
```
This replaces existing progress with the contents of `my_progress.json` (a backup is created beforehand).

