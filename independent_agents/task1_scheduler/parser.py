import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

WEEKDAYS = {
    "mon": 0, "monday": 0,
    "tue": 1, "tues": 1, "tuesday": 1,
    "wed": 2, "weds": 2, "wednesday": 2,
    "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}

def _next_weekday(target_weekday: int, today: Optional[datetime] = None) -> datetime:
    today = today or datetime.now()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:  # "this Friday" when today is Friday -> use same day
        return today
    return today + timedelta(days=days_ahead)

def _parse_date_word(text: str) -> datetime:
    t = text.lower()
    now = datetime.now()
    if "tomorrow" in t:
        return now + timedelta(days=1)
    if "today" in t:
        return now

    # weekday names
    for k, wd in WEEKDAYS.items():
        if re.search(rf"\b{k}\b", t):
            return _next_weekday(wd, now)

    # default: today
    return now

def _parse_time(text: str) -> Optional[str]:
    t = text.lower()

    # keyword buckets
    if "morning" in t:
        return "09:00"
    if "afternoon" in t:
        return "15:00"
    if "evening" in t:
        return "18:00"

    # hh:mm
    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", t)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        return f"{hh:02d}:{mm:02d}"

    # h[:mm]am/pm
    m = re.search(r"\b(\d{1,2})(?::([0-5]\d))?\s*(am|pm)\b", t)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2) or 0)
        ampm = m.group(3)
        if ampm == "pm" and hh != 12:
            hh += 12
        if ampm == "am" and hh == 12:
            hh = 0
        return f"{hh:02d}:{mm:02d}"

    return None

def _parse_duration_minutes(text: str) -> int:
    t = text.lower()
    # e.g., "30-min", "30 min", "30 minutes"
    m = re.search(r"\b(\d+)\s*-\s*?min(?:ute)?s?\b|\b(\d+)\s*min(?:ute)?s?\b", t)
    if m:
        val = m.group(1) or m.group(2)
        return int(val)

    # e.g., "1 hour", "2 hours", "1h", "90m"
    m = re.search(r"\b(\d+)\s*hour(?:s)?\b|\b(\d+)h\b", t)
    if m:
        val = m.group(1) or m.group(2)
        return int(val) * 60

    m = re.search(r"\b(\d+)m\b", t)
    if m:
        return int(m.group(1))

    return 30  # default

def _parse_attendees(text: str) -> List[str]:
    # crude: look for "with <names...>"
    m = re.search(r"\bwith\s+([A-Z][a-zA-Z]+(?:[ ,]+[A-Z][a-zA-Z]+)*)", text)
    if not m:
        return []
    raw = m.group(1)
    # split on comma or 'and'
    parts = re.split(r",|\band\b", raw)
    return [p.strip() for p in parts if p.strip()]

def _parse_title(text: str) -> str:
    # try to pick a short title: words before "with", otherwise fallback keywords
    pre_with = re.split(r"\bwith\b", text, flags=re.IGNORECASE)[0]
    # heuristic nouns after "schedule/book/set up a"
    m = re.search(r"\b(schedule|book|set\s*up|create|organize)\b\s+(a|an)?\s*([a-zA-Z0-9 \-_/]+)", pre_with, flags=re.IGNORECASE)
    if m:
        candidate = m.group(3).strip()
        # trim common time words
        candidate = re.sub(r"\b(tomorrow|today|morning|afternoon|evening|on\s+\w+|at\s+.+)$", "", candidate, flags=re.IGNORECASE).strip()
        if candidate:
            return candidate.title()
    # sane fallback
    return "Meeting"

def _compose_iso(date_obj: datetime, hhmm: Optional[str], duration_min: int):
    if hhmm is None:
        hhmm = "15:00"  # sensible default
    hh, mm = [int(x) for x in hhmm.split(":")]
    start = date_obj.replace(hour=hh, minute=mm, second=0, microsecond=0)
    end = start + timedelta(minutes=duration_min)
    # return naive ISO 8601 strings
    return start.isoformat(), end.isoformat()

def parse_request(text: str) -> Dict[str, any]:
    t = text.strip()

    # Is this a list request?
    if re.search(r"\blist\b|\bshow\b|\bwhat'?s on\b|\bmy calendar\b", t, flags=re.IGNORECASE):
        date_obj = _parse_date_word(t)
        return {
            "action": "list",
            "date": date_obj.date().isoformat(),
        }

    # Otherwise treat as create
    date_obj = _parse_date_word(t)
    time_hhmm = _parse_time(t)
    duration = _parse_duration_minutes(t)
    attendees = _parse_attendees(t)
    title = _parse_title(t)

    start_iso, end_iso = _compose_iso(date_obj, time_hhmm, duration)

    return {
        "action": "create",
        "title": title,
        "attendees": attendees,
        "duration_minutes": duration,
        "date": date_obj.date().isoformat(),
        "start_iso": start_iso,
        "end_iso": end_iso,
        "note": None,
    }
