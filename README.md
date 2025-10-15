# agentic-starter

Minimal agentic repo with:
- 2 runnable agents (`researcher`, `scheduler`)
- shared tool registry
- example API tool (Google Calendar-like)

## Quickstart
```bash
# from the repo root
python -m agents.researcher.main "Find context about LLM observability."
python -m agents.researcher.main "Give me a 1-sentence overview of vector databases."
python -m agents.scheduler.main  "Schedule a meeting with John tomorrow at 15:00."
python -m agents.scheduler.main  "List my calendar for today."
python -m agents.scheduler.main  "Schedule a meeting tomorrow at 15:00."
