"""
Quick Scheduler — single-file example agent.
Usage:
  python -m single_agents.quick_scheduler "Schedule a meeting tomorrow at 15:00 with John"
  python -m single_agents.quick_scheduler "List my calendar for today"
"""

import os
import sys
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional


# Tiny tooling

class Tool:
    name: str = "tool"
    description: str = "abstract tool"

    def invoke(self, action: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError


class GoogleCalendarTool(Tool):
    """
    Mock Calendar tool. 
    Replace with API call.
    """
    name = "google_calendar"
    description = "create/list calendar events (mocked)"

    def invoke(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "google_calendar.create_event":
            return self.create_event(**kwargs)
        if action == "google_calendar.list_events":
            return self.list_events(**kwargs)
        return {"ok": False, "error": f"Unknown action: {action}"}

    def create_event(self, title: str, date: str, time: str) -> Dict[str, Any]:
        event = {"summary": title, "date": date, "time": time}
        # Pretend success and return a fake event id
        return {"ok": True, "event": {**event, "id": "evt_mock_123"}}

    def list_events(self, date: str = "today") -> Dict[str, Any]:
        sample = [
            {"summary": "Standup", "start": f"{date}T09:00Z"},
            {"summary": "1:1 with TL", "start": f"{date}T11:30Z"},
        ]
        return {"ok": True, "date": date, "events": sample}



class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise TypeError("Attempted to register a non-Tool instance")
        if not tool.name:
            raise ValueError("Tool must have a non-empty name")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

# ---------- LLM (optional OpenAI) ----------

class EchoLLM:
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[echo] {prompt[:200]}"

def get_llm():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return EchoLLM()

    try:
        import openai
        client = openai.OpenAI(api_key=key)
    except Exception:
        # If openai lib isn't installed, fall back to echo
        return EchoLLM()

    class _OpenAIWrapper:
        def generate(self, prompt: str, **kwargs) -> str:
            model = kwargs.get("model", "gpt-4o-mini")
            temperature = kwargs.get("temperature", 0.2)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            return resp.choices[0].message.content
    return _OpenAIWrapper()

# ---------- Router ----------

import re
from datetime import datetime, timedelta


def _extract_time(text: str) -> Optional[str]:
    # Match HH:MM or H:MM 24h time
    m = re.search(r"\b(\d{1,2}:\d{2})\b", text)
    if not m:
        return None
    hh, mm = m.group(1).split(":")
    try:
        h, m_ = int(hh), int(mm)
        if 0 <= h <= 23 and 0 <= m_ <= 59:
            return f"{h:02d}:{m_:02d}"
    except ValueError:
        return None
    return None


def _extract_date(text: str) -> Optional[str]:
    t = text.lower()
    today = datetime.today().date()
    if "today" in t:
        return today.isoformat()
    if "tomorrow" in t:
        return (today + timedelta(days=1)).isoformat()
    # YYYY-MM-DD
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            return dt.isoformat()
        except ValueError:
            return None
    return None


def _extract_with_name(text: str) -> Optional[str]:
    # naive: capture word(s) after 'with '
    m = re.search(r"with\s+([A-Z][A-Za-z\-']+(?:\s+[A-Z][A-Za-z\-']+)*)", text)
    if m:
        return m.group(1)
    return None


def keyword_router(user_text: str) -> Optional[Dict[str, Any]]:
    t = user_text.strip()
    tl = t.lower()
    if not t:
        return None

    mentions_calendar = any(k in tl for k in ["calendar", "meeting", "schedule", "event", "appoint"])
    if not mentions_calendar:
        return None

    date_str = _extract_date(t)
    time_str = _extract_time(t)
    name = _extract_with_name(t)

    intent_create = any(k in tl for k in ["schedule", "create", "add", "book"]) and (date_str is not None and time_str is not None)
    intent_list = ("list" in tl or "show" in tl or "what" in tl) and (date_str is not None or "today" in tl)

    if intent_create:
        title = f"Meeting with {name}" if name else "Meeting"
        return {
            "tool": "google_calendar",
            "action": "google_calendar.create_event",
            "args": {"title": title, "date": date_str, "time": time_str},
        }

    # default to list if no clear create intent
    return {
        "tool": "google_calendar",
        "action": "google_calendar.list_events",
        "args": {"date": date_str or "today"},
    }

# ---------- Agent ----------

@dataclass
class AgentConfig:
    name: str = "quick_scheduler"
    system_prompt: str = (
        "You are a practical scheduling assistant. Prefer using calendar tools "
        "when the user asks about meetings or schedules; otherwise, answer briefly."
    )
    llm_model: str = "gpt-4o-mini"

class Agent:
    def __init__(self, config: AgentConfig):
        self.cfg = config
        self.llm = get_llm()
        self.registry = ToolRegistry()
        self.registry.register(GoogleCalendarTool())

    def run(self, user_input: str) -> Dict[str, Any]:
        # Try a simple keyword route to a tool
        route = keyword_router(user_input)
        if route:
            tool = self.registry.get(route["tool"])
            result = tool.invoke(route["action"], **route["args"])
            return {
                "agent": self.cfg.name,
                "mode": "tool",
                "tool": route["action"],
                "result": result,
            }

        # Otherwise, answer with the LLM
        prompt = f"{self.cfg.system_prompt}\n\nUser: {user_input}\nAssistant:"
        text = self.llm.generate(prompt, model=self.cfg.llm_model)
        return {"agent": self.cfg.name, "mode": "llm", "text": text}

# ---------- Entry Point ----------

def main():
    user_input = " ".join(sys.argv[1:]) or "List my calendar for today"
    agent = Agent(AgentConfig())
    out = agent.run(user_input)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()       