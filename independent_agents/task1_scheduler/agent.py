from typing import Dict, Any
from parser import parse_request
from calendar_tool import CalendarTool

class SchedulerAgent:
    """
    Minimal agent:
      1) Parse NL request -> intent
      2) Route to calendar tool (create/list)
      3) Return structured result
    """
    def __init__(self):
        self.calendar = CalendarTool()  # local JSON-backed mock

    def handle(self, user_text: str) -> Dict[str, Any]:
        intent = parse_request(user_text)

        if intent["action"] == "list":
            events = self.calendar.list_events(intent["date"])
            return {
                "mode": "list",
                "query_date": intent["date"],
                "events": events,
            }

        if intent["action"] == "create":
            # required fields are built by parser with sensible defaults
            created = self.calendar.create_event(
                title=intent["title"],
                start_iso=intent["start_iso"],
                end_iso=intent["end_iso"],
                attendees=intent.get("attendees", []),
                note=intent.get("note"),
            )
            return {
                "mode": "create",
                "request": {
                    "title": intent["title"],
                    "start_iso": intent["start_iso"],
                    "end_iso": intent["end_iso"],
                    "attendees": intent.get("attendees", []),
                },
                "created": created,
            }

        # Fallback: echo the parser output to debug
        return {"mode": "unknown", "intent": intent}
