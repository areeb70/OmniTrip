from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

class AgentRun(BaseModel):
    goal: str
    start_city: str # <--- THIS MUST BE HERE
    city: str
    people: int
    nights: int
    duration_days: int
    budget: dict[str, Any]
    transit: dict[str, Any]
    travel_risk: dict[str, Any]
    itinerary: list[dict[str, Any]]
    final_plan: str
    feedback_used: dict[str, Any] | None = None
    saved_path: str | None = Field(default=None)

OUTPUT_DIR = Path("outputs")
