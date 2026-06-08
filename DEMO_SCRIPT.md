# 3 Minute Demo Script

## 0:00 - 0:20

Introduce the problem:

"World Cup match days are stressful for families. They need budget planning, safe travel, crowd-risk handling, and clear next actions."

## 0:20 - 0:50

Show the app:

"This is MatchDayOps, a Gemini-powered agent. It is not just a chatbot. It uses tools to estimate budget, plan transit, assess crowd risk, and build an itinerary."

## 0:50 - 1:30

Run the agent:

"I enter a goal for a family of four in New York. The agent calls its tools, then Gemini creates a final action plan."

Point out:

- budget
- safety
- transit
- human approval gates
- five next actions

## 1:30 - 2:05

Show tracing:

"The app is instrumented with Phoenix/OpenInference tracing. Each tool call and Gemini generation becomes visible in Phoenix, so we can inspect what happened."

## 2:05 - 2:35

Show evaluation:

"Now I run the evaluator. It checks whether the plan includes budget, safety, approval gates, next actions, tool evidence, and risk mitigation."

## 2:35 - 3:00

Show self-improvement:

"The evaluation feedback is saved. On the next run, the agent reads that feedback and uses it to improve its answer. This is the self-improvement loop."
