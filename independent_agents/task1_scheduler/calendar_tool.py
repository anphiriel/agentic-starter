import json
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CAL_PATH = DATA_DIR / "calendar.json"

def _load_all() -> List[Dict[str, Any]]:
    if not CAL_PATH.exists():
        return []
    try:
        return json.loads(CAL_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def _save_all(events: List[Dict[str, Any]]) -> None:
    CAL_PATH.write_text(json.dumps(events, indent=2), encoding="utf-8")

class CalendarTool:
    """
    Mock calendar “API”. Persists to data/calendar.json
    Methods:
      - create_event(title, start_iso, end_iso, attendees, note)
      - list_events(date_iso)
    """
    def __init__(self):
        # ensure file exists
        if not CAL_PATH.exists():
            _save_all([])

    def create_event(
        self,
        title: str,
        start_iso: str,
        end_iso: str,
        attendees: list | None = None,
        note: str | None = None,
    ) -> Dict[str, Any]:
        events = _load_all()
        event_id = f"evt_{len(events) + 1:04d}"
        event = {
            "id": event_id,
            "summary": title,
            "start": start_iso,
            "end": end_iso,
            "attendees": attendees or [],
            "note": note,
        }
        events.append(event)
        _save_all(events)
        return {"ok": True, "event": event}

    def list_events(self, date_iso: str) -> List[Dict[str, Any]]:
        events = _load_all()
        # naive filter by date prefix in ISO
        return [e for e in events if e["start"].startswith(date_iso)]
