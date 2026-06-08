import json
from pathlib import Path

from matchdayops.evals import evaluate_plan
from matchdayops.feedback import save_eval_feedback


def main() -> None:
    output_dir = Path("outputs")
    plans = sorted(output_dir.glob("plan_*.md"))
    if not plans:
        print("No plans found. Run: python src/agent.py")
        return

    latest = plans[-1]
    evaluation = evaluate_plan(latest.read_text(encoding="utf-8"))
    save_eval_feedback(evaluation)
    print(json.dumps({"evaluated": str(latest), **evaluation}, indent=2))


if __name__ == "__main__":
    main()
