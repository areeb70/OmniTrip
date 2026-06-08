# Devpost Draft

## Project Name

MatchDayOps

## Track

Arize

## What It Does

MatchDayOps is a Gemini-powered agent that helps World Cup fans plan safe, affordable, and organized match days. It estimates budget, suggests transit, assesses crowd risk, builds an itinerary, and produces a final action plan with human approval steps.

## Inspiration

Large events are exciting but stressful. Families and travelers need more than a chatbot answer. They need an agent that can reason through logistics, use tools, and improve after seeing what worked and what failed.

## How We Built It

The project uses a Python code-owned agent runtime with Gemini through the Google GenAI SDK. Agent tools handle budget estimation, transit planning, crowd-risk assessment, and itinerary creation. Phoenix/OpenInference tracing hooks record each major step. A local evaluator scores the final plan and saves feedback for future runs.

## Arize Integration

The project is designed to send traces to Phoenix Cloud or a self-hosted Phoenix instance. It includes OpenInference-compatible tracing setup and a Phoenix MCP configuration for Gemini CLI. The self-improvement loop uses evaluation feedback so the agent can improve later outputs.

## Challenges

The main challenge was designing an agent that is useful without becoming too complex. The solution keeps the task focused on match-day operations while still demonstrating tools, tracing, evaluation, and feedback.

## Accomplishments

- Built a working code-owned Gemini agent
- Added a FastAPI web app and CLI
- Added tool-based planning
- Added local evaluation
- Added Phoenix-ready tracing
- Added a feedback loop for self-improvement

## What Is Next

- Connect live city transit APIs
- Add official stadium data
- Add real Phoenix dataset and experiment workflows
- Add LLM-as-a-Judge evaluations
- Deploy the web app to Cloud Run
