from dataclasses import dataclass
from typing import Dict, Any
from .llm import get_llm
from .tools import ToolRegistry, keyword_router

@dataclass
class AgentConfig:
    system_prompt: str
    llm_model: str = "gpt-4o-mini"

class Agent:
    def __init__(self, name: str, config: AgentConfig, tools: ToolRegistry):
        self.name = name
        self.config = config
        self.tools = tools
        self.llm = get_llm()

    def run(self, user_input: str) -> Dict[str, Any]:
        
        # 1) Try routing to a tool
        route = keyword_router(user_input, self.tools)
        if route:
            tool_name = route["tool"]
            args = route["args"]
            tool_group, method = tool_name.split(".")
            tool = self.tools.get(tool_group)
            result = tool.invoke(action=method, **args)
            return {"agent": self.name, "action": tool_name, "result": result}

        # 2) Otherwise, just respond via LLM
        prompt = f"{self.config.system_prompt}\n\nUser: {user_input}\nAssistant:"
        text = self.llm.generate(prompt, model=self.config.llm_model)
        return {"agent": self.name, "action": "llm.generate", "result": {"text": text}}