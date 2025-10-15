"""
- create_event(title, date, time) -> creates a calendar event (mocked POST)
- list_events(date="today") -> returns example events (mocked GET)
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from core.tools import Tool
from .http_client import post, get

class GoogleCalendarTool(Tool):
    name = "google_calendar"
    description = "Create/list calendar events via a simple API facade."

    def __init__(self, base_url: str | None = None):
        # For demo we use httpbin.org to simulate network calls.
        # Swap base_url to the real Google Calendar API gateway.
        self.base_url = base_url or "https://httpbin.org"

    def invoke(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "google_calendar.create_event":
            return self.create_event(**kwargs)
        if action == "google_calendar.list_events":
            return self.list_events(**kwargs)
        return {"error": f"Unknown action: {action}"}

    # --- Actions ---
    def create_event(self, title: str, date: str, time: str) -> Dict[str, Any]:
        # In real life, translate date/time + timezone -> RFC3339; add attendees, etc.
        payload = {"summary": title, "date": date, "time": time}
        
        # Mocked POST (replace with your gateway that handles OAuth to Google)
        r = post(f"{self.base_url}/post", json=payload)
        return {"ok": r["status_code"] == 200, "request": payload, "response": r["json"]}

    def list_events(self, date: str = "today") -> Dict[str, Any]:
        # Return a simple, deterministic mock list (or call your backend)
        base_date = datetime.utcnow().date()
        if date == "tomorrow":
            base_date += timedelta(days=1)
        sample = [
            {"summary": "Standup", "start": f"{base_date}T09:00:00Z"},
            {"summary": "1:1",     "start": f"{base_date}T11:30:00Z"},
        ]
        # Mocked GET
        r = get(f"{self.base_url}/get", params={"date": str(base_date)})
        return {"ok": r["status_code"] == 200, "date": str(base_date), "events": sample}

# Registry helper
def register(registry):
    registry.register(GoogleCalendarTool())