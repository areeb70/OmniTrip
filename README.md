# MatchDayOps

MatchDayOps is a Gemini-powered agent that helps travelers plan a safer, cheaper, and more organized 2026 World Cup match day.

It is built for the Arize hackathon track. The project shows a code-owned agent runtime, tool use, Phoenix-ready tracing, evaluations, and a simple self-improvement loop.

## Simple Explanation

This project has five main parts:

1. Gemini is the brain.
2. Python tools are the hands.
3. OpenInference records what happened.
4. Phoenix shows the traces and evaluation results.
5. Phoenix MCP lets the agent inspect observability data so it can improve.

The agent does not only chat. It performs a multi-step task:

1. Reads the travel goal.
2. Estimates budget.
3. Plans transit.
4. Checks crowd and safety risk.
5. Builds an itinerary.
6. Generates a final plan with Gemini.
7. Evaluates the answer.
8. Uses evaluation feedback in the next run.

## Why This Qualifies For Arize

- Code-owned agent runtime: Python CLI and FastAPI app.
- Gemini-powered: uses the Google GenAI SDK when `GOOGLE_API_KEY` is set.
- Tool use: budget, transit, crowd-risk, itinerary, save-run tools.
- OpenInference/Phoenix tracing: tracing hooks are included in `src/matchdayops/tracing.py`.
- Phoenix MCP ready: Gemini CLI config is included below.
- Evaluation loop: `src/evaluate.py` scores plans and saves feedback for future runs.
- Real-world challenge: World Cup travel logistics for families and fans.

## Project Structure

```text
src/
  agent.py                 CLI agent entrypoint
  app.py                   FastAPI web app
  evaluate.py              Local quality evaluation
  matchdayops/
    llm.py                 Gemini call and offline fallback
    tools.py               Agent tools
    evals.py               Scoring logic
    feedback.py            Self-improvement feedback storage
    tracing.py             Phoenix/OpenInference tracing setup
    schemas.py             Data models
```

## Setup

Create and activate a Python environment.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then fill in keys.

```bash
copy .env.example .env
```

Required for Gemini:

```bash
GOOGLE_API_KEY=your_google_api_key
```

Required for Phoenix Cloud tracing:

```bash
PHOENIX_API_KEY=your_phoenix_cloud_api_key
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-space-name
PHOENIX_PROJECT_NAME=worldcup
```

If you do not have keys yet, the project still runs in offline demo mode. That makes it easier to understand and test first.

## Run The CLI Agent

```bash
python src/agent.py "Plan a safe World Cup match day in New York for my family." --city "New York" --people 4 --nights 2 --kickoff "18:00"
```

Run evaluation:

```bash
python src/evaluate.py
```

Test Phoenix tracing only:

```bash
python src/test_phoenix.py
```

If traces do not show in Phoenix, open `outputs/phoenix_debug.log` to see whether the API key and endpoint were loaded.

Run the agent again. It will read the latest evaluation feedback and improve the next answer.

## Run The Web App

Easiest way on Windows:

```text
Double-click run_app.bat
```

Then open:

```text
http://127.0.0.1:8000
```

Manual way:

```bash
uvicorn src.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Phoenix MCP For Gemini CLI

Add this to Gemini CLI `settings.json`.

```json
{
  "mcpServers": {
    "phoenix": {
      "command": "npx",
      "args": ["-y", "@arizeai/phoenix-mcp"],
      "env": {
        "PHOENIX_API_KEY": "your_phoenix_cloud_api_key",
        "PHOENIX_BASE_URL": "https://app.phoenix.arize.com"
      }
    }
  }
}
```

In the demo, explain that Phoenix MCP gives the agent access to its own traces, prompts, experiments, datasets, and evaluations as runtime tools.

## Demo Flow

1. Open the web app.
2. Enter a trip goal, city, people count, nights, and kickoff time.
3. Run the agent.
4. Show the generated plan.
5. Show the saved output files in `outputs/`.
6. Run `python src/evaluate.py`.
7. Show the evaluation feedback.
8. Run the agent again and explain that it used feedback from the previous run.
9. Show Phoenix traces if your Phoenix key is configured.

## Devpost Summary

MatchDayOps is a Gemini-powered operations agent for 2026 World Cup fans. It helps families plan safer and more affordable match days by combining budget estimation, transit planning, crowd-risk assessment, and itinerary generation. The project integrates Arize Phoenix observability through OpenInference-compatible tracing and includes a self-improvement loop where evaluations are saved and used in future runs.

## License

MIT
