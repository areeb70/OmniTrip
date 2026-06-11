import os 
import requests
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
def estimate_budget(start_city: str, city: str, people: int, nights: int, goal: str) -> dict:
    # 1. Get the base costs for the city
    baseline = CITY_BASELINES.get(city.lower(), {"hotel": 130, "food_day": 40, "transit": "Public Transport", "risk": "Medium"})
    days = max(nights + 1, 1)
    
    # 2. DYNAMIC MULTIPLIER: This is the "Smart" part
    # We check the 'goal' to see if we should make the trip more expensive or cheaper
    multiplier = 1.0 # Default: Mid-range
    goal_lower = goal.lower()
    
    if any(word in goal_lower for word in ["luxury", "premium", "fancy", "high-end", "expensive", "romantic"]):
        multiplier = 1.8  # Increase prices by 80% for luxury
    elif any(word in goal_lower for word in ["budget", "cheap", "affordable", "low cost", "student"]):
        multiplier = 0.6  # Decrease prices by 40% for budget
    
    # 3. Calculate costs using the multiplier
    flights = get_flight_estimate(start_city, city, people)
    
    # We multiply the hotel and food by the multiplier
    lodging = (baseline["hotel"] * multiplier) * nights
    meals = people * days * (baseline["food_day"] * multiplier)
    transit = people * days * 30 * multiplier
    activities = people * days * 45 * multiplier
    
    subtotal = flights["total_flight_cost"] + lodging + meals + transit + activities
    buffer = round(subtotal * 0.10)
    
    return {
        "overall_total": subtotal + buffer,
        "style": "Luxury" if multiplier > 1 else ("Budget" if multiplier < 1 else "Mid-range"),
        "flight_details": flights,
        "breakdown": {
            "flights": flights["total_flight_cost"],
            "lodging": round(lodging, 2),
            "meals_and_dining": round(meals, 2),
            "local_transport": round(transit, 2),
            "activities_and_tours": round(activities, 2),
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

@traced("tool.search_travel_costs")
def search_travel_costs(city: str, style: str) -> str:
    """
    Performs a real-time web search for current travel expenses in a specific city.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Search tool unavailable: No TAVILY_API_KEY found in .env."

    # We create a very specific query to get numbers and current dates
    query = f"average daily cost for {style} travel in {city} 2024 2025 hotel food transport activities"
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 3
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if not results:
            return "No real-time data found for this destination. Relying on baseline estimates."

        # We combine the top 3 search results into one block of text for Gemini to analyze
        context = "\n\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in results])
        return context
    except Exception as e:
        return f"Real-time search failed: {str(e)}. Relying on baseline estimates."

