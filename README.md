# agentic-starter

Minimal agentic repo with:
- 2 runnable agents (`researcher`, `scheduler`)
- shared tool registry
- example API tool (Google Calendar-like)

## Quickstart
```bash
python -m agents.researcher.main "Find context about LLM observability."
python -m agents.scheduler.main  "Schedule a meeting with John tomorrow at 15:00."
