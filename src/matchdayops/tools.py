import json
from datetime import datetime
from matchdayops.schemas import AgentRun, OUTPUT_DIR
from matchdayops.tracing import traced

# Mapping cities to regions for flight estimation
REGION_MAP = {
    "new york": "north_america", "los angeles": "north_america", "toronto": "north_america", "mexico city": "north_america",
    "london": "europe", "paris": "europe", "berlin": "europe", "rome": "europe", "madrid": "europe",
    "tokyo": "asia", "seoul": "asia", "bangkok": "asia", "singapore": "asia", "delhi": "asia", "mumbai": "asia",
    "sydney": "oceania", "melbourne": "oceania",
    "cairo": "africa", "nairobi": "africa", "joburg": "africa",
}

CITY_BASELINES = {
    "new york": {"hotel": 250, "food_day": 60, "transit": "Subway & Rideshare", "risk": "Low"},
    "tokyo": {"hotel": 150, "food_day": 40, "transit": "Trains & Walking", "risk": "Very Low"},
    "paris": {"hotel": 200, "food_day": 70, "transit": "Metro & Walking", "risk": "Low"},
    "bangkok": {"hotel": 60, "food_day": 20, "transit": "TukTuks & Grab", "risk": "Medium"},
    "london": {"hotel": 180, "food_day": 50, "transit": "Tube & Bus", "risk": "Low"},
}

def get_flight_estimate(start: str, end: str, people: int) -> dict:
    start_reg = REGION_MAP.get(start.lower(), "unknown")
    end_reg = REGION_MAP.get(end.lower(), "unknown")
    
    if start_reg == "unknown" or end_reg == "unknown":
        cost_per_person = 1200 
    elif start_reg == end_reg:
        cost_per_person = 300 
    elif (start_reg == "north_america" and end_reg == "europe") or (start_reg == "europe" and end_reg == "north_america"):
        cost_per_person = 800 
    else:
        cost_per_person = 1500 
        
    return {
        "category": "Flight Estimate",
        "cost_per_person": cost_per_person,
        "total_flight_cost": cost_per_person * people
    }

@traced("tool.estimate_budget")
def estimate_budget(start_city: str, city: str, people: int, nights: int) -> dict:
    baseline = CITY_BASELINES.get(city.lower(), {"hotel": 120, "food_day": 40, "transit": "Public Transport", "risk": "Medium"})
    days = max(nights + 1, 1)
    
    flights = get_flight_estimate(start_city, city, people)
    lodging = baseline["hotel"] * nights
    meals = people * days * baseline["food_day"]
    transit = people * days * 25
    activities = people * days * 40
    
    subtotal = flights["total_flight_cost"] + lodging + meals + transit + activities
    buffer = round(subtotal * 0.10)
    
    return {
        "overall_total": subtotal + buffer,
        "flight_details": flights,
        "breakdown": {
            "flights": flights["total_flight_cost"],
            "lodging": lodging,
            "meals_and_dining": meals,
            "local_transport": transit,
            "activities_and_tours": activities,
            "emergency_buffer": buffer
        }
    }

@traced("tool.find_transit_options")
def find_transit_options(city: str) -> dict:
    baseline = CITY_BASELINES.get(city.lower(), {"transit": "General Public Transport"})
    return {
        "recommended": baseline["transit"],
        "backup": "Rideshare apps (Uber/Grab/Bolt)",
        "tip": "Get a local city-pass for unlimited travel."
    }

@traced("tool.assess_travel_risk")
def assess_travel_risk(city: str) -> dict:
    baseline = CITY_BASELINES.get(city.lower(), {"risk": "Medium"})
    return {
        "safety_level": baseline["risk"],
        "considerations": [
            "Check current travel advisories",
            "Keep a digital copy of your passport",
            "Use a secure VPN for public Wi-Fi",
            "Research local emergency numbers"
        ],
    }

@traced("tool.build_itinerary")
def build_itinerary(city: str, days: int) -> list[dict[str, str]]:
    itinerary = []
    for day in range(1, days + 1):
        itinerary.append({
            "day": day, 
            "morning": "Local landmark exploration", 
            "afternoon": "Cultural activity or museum", 
            "evening": "Dinner and local leisure"
        })
    return itinerary

@traced("tool.save_agent_run")
def save_agent_run(run: AgentRun) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = OUTPUT_DIR / f"trip_run_{timestamp}.json"
    run.saved_path = str(filename)
    filename.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    markdown = OUTPUT_DIR / f"plan_{timestamp}.md"
    markdown.write_text(run.final_plan, encoding="utf-8")
    return str(filename)
