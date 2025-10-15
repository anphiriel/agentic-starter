import sys
from core.agent import Agent, AgentConfig
from core.utils import boot, load_yaml
from core.prompts import load_text
from tools import build_registry

def main():
    boot()
    user_input = " ".join(sys.argv[1:]) or "What is LLM observability?"
    cfg = load_yaml(__file__.replace("main.py", "config.yaml"))
    system = load_text(__file__.replace("main.py", "prompts/system.txt"))
    agent = Agent("researcher", AgentConfig(system_prompt=system, llm_model=cfg["llm_model"]), build_registry())
    out = agent.run(user_input)
    print(out)

if __name__ == "__main__":
    main()