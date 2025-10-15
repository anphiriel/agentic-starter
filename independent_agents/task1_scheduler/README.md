# Tool-Calling Scheduler Agent (Minimal)

Parses natural-language scheduling requests and calls a mock Calendar API tool
that persists events to `data/calendar.json`.

## Run

```bash
python run.py "Schedule a 30-min sync with Maya tomorrow afternoon"
python run.py "List my calendar for today"
python run.py "Book a 1 hour meeting with Alex Friday at 3pm"