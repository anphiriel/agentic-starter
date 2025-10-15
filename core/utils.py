import os
from dotenv import load_dotenv
import yaml

def boot():
    load_dotenv()

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)