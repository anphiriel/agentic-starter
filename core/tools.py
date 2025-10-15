from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable

class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def invoke(self, **kwargs) -> Dict[str, Any]:
        ...

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list(self) -> Dict[str, str]:
        return {t.name: t.description for t in self._tools.values()}

# Simple “router”: map keywords to a tool + adapter
Router = Callable[[str, ToolRegistry], Optional[Dict[str, Any]]]

def keyword_router(user_text: str, registry: ToolRegistry) -> Optional[Dict[str, Any]]:
    text = user_text.lower()
    
    # Very tiny examples; replace with your policy/LLM tool-calling logic
    if any(k in text for k in ["meeting", "calendar", "schedule"]):
        if "tomorrow" in text:
            return {"tool": "google_calendar.create_event",
                    "args": {"title": "Meeting", "date": "tomorrow", "time": "15:00"}}
        return {"tool": "google_calendar.list_events", "args": {"date": "today"}}
    return None