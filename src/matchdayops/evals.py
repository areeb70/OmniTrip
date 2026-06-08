from matchdayops.tracing import traced


@traced("eval.plan_quality")
def evaluate_plan(text: str) -> dict:
    lower = text.lower()
    checks = {
        "budget": "budget" in lower or "$" in text,
        "safety": "safety" in lower or "safe" in lower or "crowd" in lower,
        "human_approval": "approval" in lower or "approve" in lower,
        "next_actions": "next actions" in lower or "5 next actions" in lower,
        "tool_evidence": "estimated" in lower and "transit" in lower,
        "risk_mitigation": "mitigation" in lower or "backup" in lower,
    }
    score = round(sum(checks.values()) / len(checks), 2)
    feedback = []
    if not checks["budget"]:
        feedback.append("Add explicit budget numbers and assumptions.")
    if not checks["safety"]:
        feedback.append("Include safety and crowd-management guidance.")
    if not checks["human_approval"]:
        feedback.append("Add human approval gates before spending money.")
    if not checks["next_actions"]:
        feedback.append("End with exactly 5 concrete next actions.")
    if not checks["tool_evidence"]:
        feedback.append("Reference tool evidence such as budget and transit outputs.")
    if not checks["risk_mitigation"]:
        feedback.append("Name risks and backup plans.")
    if not feedback:
        feedback.append("Plan passes all local quality checks.")
    return {"score": score, "checks": checks, "feedback": feedback}
