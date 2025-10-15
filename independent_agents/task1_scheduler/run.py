import sys
from agent import SchedulerAgent

def main():
    print("hi")
    text = " ".join(sys.argv[1:]) or "Schedule a 30-min sync with Maya tomorrow afternoon"
    agent = SchedulerAgent()
    result = agent.handle(text)
    # pretty print
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()