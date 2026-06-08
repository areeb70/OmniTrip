import sys
from pathlib import Path

# Ensure the src directory is in the python path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import our custom agent and logic
from agent import run_agent
from matchdayops.evals import evaluate_plan
from matchdayops.feedback import save_eval_feedback
from matchdayops.tracing import configure_tracing, flush_tracing

# Initialize tracing
configure_tracing()

app = FastAPI(title="OmniTrip AI Agent")

# Allow the browser to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanRequest(BaseModel):
    goal: str = "Plan a budget-friendly vacation."
    start_city: str = "New York"
    city: str = "Tokyo"
    people: int = 2
    nights: int = 3
    duration_days: int = 4

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return r"""
<!doctype html>
<html lang="en">
  <head>
    <title>OmniTrip AI | Enterprise Travel Planner</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
      body { font-family: 'Plus Jakarta Sans', sans-serif; background: #f8fafc; }
      /* FIXED: Corrected the hex code here */
      .gradient-header { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); }
      .glass { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: 1px solid #e2e8f0; }
      .step-content { display: none; }
      .step-content.active { display: block; animation: fadeIn 0.4s ease-out; }
      @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      #result-container table { width: 100%; border-collapse: collapse; margin: 20px 0; border: 1px solid #e2e8f0; }
      #result-container th, #result-container td { padding: 12px; border: 1px solid #e2e8f0; text-align: left; }
      #result-container th { background-color: #f1f5f9; font-weight: 600; }
      .loader { border: 3px solid #f3f3f3; border-top: 3px solid #3b82f6; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; display: inline-block; }
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
      .tab-btn.active { background-color: #3b82f6; color: white; }
      @media print { .no-print { display: none !important; } body { background: white !important; } .glass { border: none !important; box-shadow: none !important; } }
    </style>
  </head>
  <body class="text-slate-900">
    <header class="gradient-header py-12 px-4 text-center text-white mb-10 no-print">
      <h1 class="text-4xl font-extrabold tracking-tight mb-2">OmniTrip AI ✈️</h1>
      <p class="text-slate-300 font-light">Architecting Bespoke Global Experiences</p>
    </header>

    <main class="max-w-5xl mx-auto px-4 pb-20">
      <!-- Wizard -->
      <div id="wizard-container" class="glass rounded-3xl p-8 shadow-xl mb-10 no-print">
        <div class="flex items-center justify-center mb-10 gap-4">
          <div id="dot-1" class="w-3 h-3 rounded-full bg-blue-600 transition-all"></div>
          <div class="h-1 w-12 bg-slate-200 rounded"></div>
          <div id="dot-2" class="w-3 h-3 rounded-full bg-slate-200 transition-all"></div>
          <div class="h-1 w-12 bg-slate-200 rounded"></div>
          <div id="dot-3" class="w-3 h-3 rounded-full bg-slate-200 transition-all"></div>
        </div>

        <div id="step-1" class="step-content active">
          <h2 class="text-2xl font-bold text-center mb-6">Where are we going?</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div><label class="block text-sm font-semibold text-slate-600 mb-2">Origin City</label>
            <input id="start_city" type="text" value="New York" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" /></div>
            <div><label class="block text-sm font-semibold text-slate-600 mb-2">Destination City</label>
            <input id="city" type="text" value="Paris" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" /></div>
          </div>
          <button onclick="nextStep(2)" class="w-full mt-8 bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition">Continue to Logistics →</button>
        </div>

        <div id="step-2" class="step-content">
          <h2 class="text-2xl font-bold text-center mb-6">The Logistics</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div><label class="block text-sm font-semibold text-slate-600 mb-2">Travelers</label>
            <input id="people" type="number" value="2" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" /></div>
            <div><label class="block text-sm font-semibold text-slate-600 mb-2">Nights</label>
            <input id="nights" type="number" value="3" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" /></div>
            <div><label class="block text-sm font-semibold text-slate-600 mb-2">Total Days</label>
            <input id="duration_days" type="number" value="4" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" /></div>
          </div>
          <div class="flex gap-4 mt-8">
            <button onclick="nextStep(1)" class="w-1/3 bg-slate-100 text-slate-600 font-bold py-3 rounded-xl hover:bg-slate-200 transition">← Back</button>
            <button onclick="nextStep(3)" class="w-2/3 bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition">Finalize Details →</button>
          </div>
        </div>

        <div id="step-3" class="step-content">
          <h2 class="text-2xl font-bold text-center mb-6">Travel Goal</h2>
          <label class="block text-sm font-semibold text-slate-600 mb-2">Tell us about your dream trip:</label>
          <textarea id="goal" class="w-full p-3 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 transition" rows="4">Plan a romantic 4-day trip to Paris for a couple.</textarea>
          <div class="flex gap-4 mt-8">
            <button onclick="nextStep(2)" class="w-1/3 bg-slate-100 text-slate-600 font-bold py-3 rounded-xl hover:bg-slate-200 transition">← Back</button>
            <button onclick="run()" class="w-2/3 bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition shadow-lg">Generate Experience ✨</button>
          </div>
        </div>
      </div>

      <div id="loading" class="hidden text-center py-10">
        <div class="loader mb-4"></div>
        <p class="text-slate-600 font-semibold text-xl">Consulting travel experts and calculating budgets...</p>
      </div>

      <div id="result-card" class="hidden glass rounded-3xl p-8 shadow-2xl animate-fade-in">
        <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <h2 class="text-2xl font-bold text-slate-800">Your Bespoke Dossier</h2>
          <div class="flex gap-2">
            <button onclick="showTab('plan')" class="tab-btn active px-4 py-2 rounded-lg text-sm font-bold transition">📅 Plan</button>
            <button onclick="showTab('budget')" class="tab-btn px-4 py-2 rounded-lg text-sm font-bold bg-slate-100 transition">💰 Budget</button>
            <button onclick="showTab('map')" class="tab-btn px-4 py-2 rounded-lg text-sm font-bold bg-slate-100 transition">🗺️ Map</button>
            <button onclick="window.print()" class="px-4 py-2 rounded-lg text-sm font-bold bg-slate-800 text-white transition">📄 PDF</button>
          </div>
        </div>

        <div id="tab-plan" class="tab-content active">
          <div id="result-container" class="prose prose-slate max-w-none text-gray-800"></div>
          <div class="mt-6 flex justify-between items-center border-t border-slate-200 pt-6">
            <span id="quality-score" class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full"></span>
            <button onclick="resetWizard()" class="text-blue-600 hover:text-blue-800 text-sm font-bold transition flex items-center gap-2">
                <span>🔄</span> Plan Another Trip
            </button>
          </div>
        </div>

        <div id="tab-budget" class="tab-content hidden">
          <div class="flex flex-col items-center">
            <div class="w-full max-w-md"><canvas id="budgetChart"></canvas></div>
            <p class="mt-4 text-sm text-slate-500 italic">Visual breakdown of estimated trip costs</p>
          </div>
        </div>

        <div id="tab-map" class="tab-content hidden">
          <div class="w-full h-[500px] rounded-2xl overflow-hidden border border-slate-200">
            <iframe id="trip-map" width="100%" height="100%" frameborder="0" src=""></iframe>
          </div>
        </div>
      </div>
    </main>

    <script>
      let currentChart = null;

      function nextStep(step) {
        document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
        document.getElementById('step-' + step).classList.add('active');
        document.querySelectorAll('[id^="dot-"]').forEach((dot, i) => {
            dot.className = (i + 1 <= step) ? 'w-3 h-3 rounded-full bg-blue-600 transition-all' : 'w-3 h-3 rounded-full bg-slate-200 transition-all';
        });
      }

      function resetWizard() {
        document.getElementById("result-card").classList.add("hidden");
        document.getElementById("wizard-container").classList.remove("hidden");
        nextStep(1);
      }

      function showTab(tab) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
        document.getElementById('tab-' + tab).classList.remove('hidden');
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active', 'bg-blue-600', 'text-white');
            btn.classList.add('bg-slate-100');
        });
        event.currentTarget.classList.add('active', 'bg-blue-600', 'text-white');
        event.currentTarget.classList.remove('bg-slate-100');
      }

      async function run() {
        const loading = document.getElementById("loading");
        const resultCard = document.getElementById("result-card");
        const wizard = document.getElementById("wizard-container");
        const resultContainer = document.getElementById("result-container");
        const scoreBadge = document.getElementById("quality-score");
        const tripMap = document.getElementById("trip-map");

        loading.classList.remove("hidden");
        resultCard.classList.add("hidden");
        wizard.classList.add("hidden");

        const startCity = document.getElementById("start_city").value;
        const destCity = document.getElementById("city").value;
        const payload = {
          goal: document.getElementById("goal").value,
          start_city: startCity,
          city: destCity,
          people: Number(document.getElementById("people").value),
          nights: Number(document.getElementById("nights").value),
          duration_days: Number(document.getElementById("duration_days").value)
        };

        try {
            tripMap.src = `https://www.google.com/maps?saddr=${encodeURIComponent(startCity)}&daddr=${encodeURIComponent(destCity)}&output=embed`;
            const response = await fetch("/plan", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload) });
            const data = await response.json();
            
            resultContainer.innerHTML = marked.parse(data.final_plan);
            scoreBadge.textContent = "Quality Score: " + data.evaluation.score;

            const budgetData = data.run.budget.breakdown;
            const ctx = document.getElementById('budgetChart').getContext('2d');
            if(currentChart) currentChart.destroy();
            currentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(budgetData),
                    datasets: [{
                        data: Object.values(budgetData),
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b'],
                        borderWidth: 0
                    }]
                },
                options: { plugins: { legend: { position: 'bottom' } }, cutout: '70%' }
            });

            loading.classList.add("hidden");
            resultCard.classList.remove("hidden");
        } catch (e) {
            loading.classList.add("hidden");
            wizard.classList.remove("hidden");
            alert("Error: Could not connect to the agent.");
        }
      }
    </script>
  </body>
</html>
"""

@app.post("/plan")
def plan(request: PlanRequest) -> dict:
    # Run the agent logic
    run = run_agent(
        goal=request.goal,
        start_city=request.start_city,
        city=request.city,
        people=request.people,
        nights=request.nights,
        duration_days=request.duration_days,
    )
    
    # Evaluate the resulting plan
    evaluation = evaluate_plan(run.final_plan)
    
    # Save evaluation for the next run's self-improvement
    save_eval_feedback(evaluation)
    
    # Push traces to Phoenix
    flush_tracing()
    
    return {
        "final_plan": run.final_plan,
        "run": run.model_dump(),
        "evaluation": evaluation,
    }
