# PHM5004 Question Bank

A small Flask web app for practicing PHM5004 MCQs.

It serves questions from a JSON file generated from a Markdown question bank.

## Requirements

- Python 3.9+ recommended
- `pip install flask`

## Quick start

Run the included scripts (they will rebuild the JSON if the Markdown is newer):

```bash
bash scripts/run_bank1.sh   # http://127.0.0.1:5001
bash scripts/run_bank2.sh   # http://127.0.0.1:5002
```

If you prefer to run directly:

```bash
python3 -m pip install flask
export QUESTIONS_FILE=questions.json
export PORT=5001
python3 app.py
```

## Building question JSON

Generate a JSON file from a Markdown bank:

```bash
python3 build_questions.py --input 5004question_bank.md --output questions.json
```

The scripts default to:

- Bank 1: `other/question_bank1.md` → `questions_bank1.json`
- Bank 2: `other/question_bank2.md` → `questions_bank2.json`

## Configuration

Environment variables:

- `QUESTIONS_FILE`: path to the question JSON (default: `questions.json`)
- `PORT`: server port (default: `5001`)

## Notes

- This is a study tool; the Flask `secret_key` in `app.py` is hard-coded and should be changed if you deploy it.
