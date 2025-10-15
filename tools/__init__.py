from core.tools import ToolRegistry
from .google_calendar import register as register_google_calendar

def build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    register_google_calendar(reg)
    return reg