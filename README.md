# OmniTrip

Omnitrip is a Gemini-powered agent that helps travelers plan a safer, cheaper, and more organized travel plan.

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
2. Enter a trip goal, city, people count, nights, and duration_days.
3. Run the agent.
4. Show the generated plan.
5. Show the saved output files in `outputs/`.
6. Run `python src/evaluate.py`.
7. Show the evaluation feedback.
8. Run the agent again and explain that it used feedback from the previous run.
9. Show Phoenix traces if your Phoenix key is configured.

## Devpost Summary

Omnitrip is a Gemini-powered operations agent for travellers. It helps families plan safer and more affordable travel plan by combining budget estimation, transit planning, crowd-risk assessment, and itinerary generation. The project integrates Arize Phoenix observability through OpenInference-compatible tracing and includes a self-improvement loop where evaluations are saved and used in future runs.

## License

MIT


<img width="1362" height="718" alt="Travel Goal" src="https://github.com/user-attachments/assets/057684f3-1cf1-4012-80a2-1e60b7d110e4" />
<img width="1431" height="597" alt="tracing" src="https://github.com/user-attachments/assets/634887b6-51f1-4399-86cd-01d5ffaeb3f1" />
<img width="1901" height="690" alt="Tracing spans" src="https://github.com/user-attachments/assets/db60c90c-b65c-4c87-ae4d-9fae22cdba1b" />
<img width="1129" height="938" alt="Result Plan3 updated" src="https://github.com/user-attachments/assets/c3f53e32-a07d-47a6-85fb-d05d534e5f2c" />
<img width="1114" height="961" alt="Result Plan2 updated" src="https://github.com/user-attachments/assets/999652f8-d898-4902-bf5d-b52eab149257" />
<img width="1204" height="958" alt="Result Plan1 updated" src="https://github.com/user-attachments/assets/ddf78514-d8be-490f-81f0-6fc01cc4b8d6" />
<img width="1514" height="1016" alt="Print plan feature updated" src="https://github.com/user-attachments/assets/a6974381-bbc4-4cd4-8eeb-e264508e18c4" />
<img width="1885" height="930" alt="Phoenix dashboard" src="https://github.com/user-attachments/assets/61ffed8f-e2ac-48ab-b701-3bdf7a04f752" />
<img width="1374" height="906" alt="Offline mode" src="https://github.com/user-attachments/assets/2db3f88a-e8c8-4745-87f9-153ab99799ba" />
<img width="1548" height="920" alt="Map" src="https://github.com/user-attachments/assets/c9b75271-aeaa-4dd1-b2d8-30792270a235" />
<img width="1321" height="705" alt="Logistics" src="https://github.com/user-attachments/assets/0da7537f-6b96-45e5-abdc-e49e92ab6388" />
<img width="1421" height="787" alt="LandingPage" src="https://github.com/user-attachments/assets/e2be8e55-e2f5-4105-9ff5-8f646aa05568" />
<img width="1400" height="922" alt="Budget distribution" src="https://github.com/user-attachments/assets/a6b65543-ced8-4126-a7a2-4dab0d813206" />
