import json

from matchdayops.schemas import OUTPUT_DIR


def load_eval_feedback() -> dict | None:
    path = OUTPUT_DIR / "latest_eval_feedback.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_eval_feedback(evaluation: dict) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "latest_eval_feedback.json"
    path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
    return str(path)
