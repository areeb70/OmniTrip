import argparse
import json
import os
from pathlib import Path

from matchdayops.feedback import load_eval_feedback
from matchdayops.llm import generate_final_plan
from matchdayops.schemas import AgentRun
from matchdayops.tools import (
    assess_travel_risk,
    build_itinerary,
    estimate_budget,
    find_transit_options,
    save_agent_run,
    search_travel_costs,
)
from matchdayops.tracing import configure_tracing, flush_tracing, traced

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

@traced("omnitrip.agent.run")
def run_agent(goal: str, start_city: str, city: str, people: int, nights: int, duration_days: int) -> AgentRun:
    feedback = load_eval_feedback()
    
    # 1. Determine the travel style based on the user's goal
    style = "mid-range"
    goal_lower = goal.lower()
    if any(word in goal_lower for word in ["luxury", "premium", "fancy", "high-end", "expensive"]):
        style = "luxury"
    elif any(word in goal_lower for word in ["budget", "cheap", "affordable", "low cost", "student"]):
        style = "budget"

    # 2. CALL THE SEARCH TOOL for real-world, live data
    web_context = search_travel_costs(city=city, style=style)
    
    # 3. Get the baseline data (for safety/comparison)
    budget = estimate_budget(start_city=start_city, city=city, people=people, nights=nights, goal=goal)
    transit = find_transit_options(city=city)
    travel_risk = assess_travel_risk(city=city)
    itinerary = build_itinerary(city=city, days=duration_days)

    # 4. Pass the web_context to Gemini
    final_plan = generate_final_plan(
        goal=goal, 
        start_city=start_city, 
        city=city, 
        people=people, 
        nights=nights, 
        duration_days=duration_days,
        budget=budget, 
        transit=transit, 
        travel_risk=travel_risk, 
        itinerary=itinerary, 
        feedback=feedback,
        web_context=web_context # <--- Pass the search results here
    )

    run = AgentRun(
        goal=goal, start_city=start_city, city=city, people=people, nights=nights, duration_days=duration_days,
        budget=budget, transit=transit, travel_risk=travel_risk, itinerary=itinerary,
        final_plan=final_plan, feedback_used=feedback,
    )
    save_agent_run(run)
    return run

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OmniTrip Gemini agent.")
    parser.add_argument("goal", nargs="?", default="Plan a budget-friendly vacation.")
    parser.add_argument("--start_city", default="New York")
    parser.add_argument("--city", default="Tokyo")
    parser.add_argument("--people", type=int, default=2)
    parser.add_argument("--nights", type=int, default=3)
    parser.add_argument("--days", type=int, default=4)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    configure_tracing()
    run = run_agent(
        goal=args.goal, 
        start_city=args.start_city, 
        city=args.city, 
        people=args.people, 
        nights=args.nights, 
        duration_days=args.days
    )

    if args.json:
        print(run.model_dump_json(indent=2))
    else:
        print(run.final_plan)
    flush_tracing()

if __name__ == "__main__":
    main()
