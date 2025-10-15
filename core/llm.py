import os
from typing import Dict

class EchoLLM:
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[echo] {prompt[:200]}"

class OpenAILLM:
    def __init__(self):
        import openai  # optional dependency
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str, **kwargs) -> str:
        resp = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.2),
        )
        return resp.choices[0].message.content

def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        return OpenAILLM()
    return EchoLLM()