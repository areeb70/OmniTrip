from datetime import datetime
import json
import os
from typing import Any
from matchdayops.tracing import traced

SYSTEM_PROMPT = """
You are OmniTrip, a premier global travel consultant. 
Your goal is to provide high-end, professional travel dossiers.

CRITICAL REQUIREMENTS:
1. BUDGET TABLE: You MUST present the expenses in a Markdown Table. 
   Columns: [Category, Cost, Description].
   Include a "GRAND TOTAL" row at the bottom.
2. LOGIC: Mention how the flights were estimated based on the departure city.
3. STRUCTURE: Use professional headings, bold text for key locations, and a clean list for the itinerary.
4. ACTIONABLE: End with exactly 5 professional "Next Steps" (e.g., Visa requirements for [City], Flight booking windows).
"""

@traced("gemini.generate_final_plan")
def generate_final_plan(
    goal: str, start_city: str, city: str, people: int, nights: int, duration_days: int,
    budget: dict[str, Any], transit: dict[str, Any], travel_risk: dict[str, Any],
    itinerary: list[dict[str, Any]], feedback: dict[str, Any] | None, web_context: str,
) -> str:
    # Get current date to stop the AI from mentioning 2023
    current_date = datetime.now().strftime("%B %d, %Y")

    prompt = f"""
{SYSTEM_PROMPT}

CURRENT DATE: {current_date}

REAL-TIME WEB SEARCH RESULTS (PRIORITY):
{web_context}

User Goal: {goal}
Route: {start_city} ✈️ {city}
Travelers: {people} | Duration: {nights} Nights ({duration_days} Days)

BASELINE ESTIMATES (Use only as a fallback if web results are vague):
Budget: {json.dumps(budget, indent=2)}
Transit: {json.dumps(transit, indent=2)}
Risk: {json.dumps(travel_risk, indent=2)}
Itinerary: {json.dumps(itinerary, indent=2)}

Prior Feedback: {json.dumps(feedback or {}, indent=2)}

INSTRUCTIONS:
1. Analyze the REAL-TIME WEB SEARCH RESULTS first.
2. Use the most current pricing found in the search results for the Budget Table.
3. If the web results are missing a specific cost, use the BASELINE ESTIMATES.
4. Ensure the final plan is realistic and current for {current_date}.
"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # DEBUG PRINT: Let's see if the key is actually loading
    if api_key:
        print(f"DEBUG: API Key found. Starts with: {api_key[:5]}... and ends with ...{api_key[-5:]}")
    else:
        print("DEBUG: GOOGLE_API_KEY NOT FOUND in environment!")

    if not api_key:
        return offline_plan(city, people, nights, duration_days, budget, transit, travel_risk, itinerary, feedback)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            contents=prompt,
        )
        return response.text or offline_plan(city, people, nights, duration_days, budget, transit, travel_risk, itinerary, feedback)
    except Exception as e:
        # DEBUG PRINT: Print the actual error causing the offline mode
        print(f"!!! GEMINI API ERROR: {str(e)}") 
        return offline_plan(city, people, nights, duration_days, budget, transit, travel_risk, itinerary, feedback)

def offline_plan(city, people, nights, duration_days, budget, transit, travel_risk, itinerary, feedback) -> str:
    # We use .get() so that if the key is missing, it doesn't crash the whole app
    total_cost = budget.get('overall_total', budget.get('estimated_total_usd', 'N/A'))
    
    # Handle transit safely
    recommended_transit = transit.get('recommended', 'General Public Transport')

    return f"""# OmniTrip Plan for {city}
(⚠️ Offline Mode - Gemini Servers are currently overloaded)

## 💰 Estimated Budget
**Total Estimated Cost: ${total_cost}**
*Note: This is a simulated estimate because the AI is currently unavailable.*

## 🚌 Transit Strategy
**Recommended:** {recommended_transit}

## 🛡️ Travel Risk
**Safety Level:** {travel_risk.get('safety_level', 'Medium')}

## 📅 Basic Itinerary
- Day 1: Arrival and hotel check-in.
- Day 2-{duration_days-1}: Local exploration and city sights.
- Day {duration_days}: Final shopping and departure.

## 🚀 Next Actions
1. Check flight availability.
2. Research hotels in {city}.
3. Verify visa requirements.
4. Pack appropriate clothing for the region.
5. Try running the generator again in a few minutes.
"""

