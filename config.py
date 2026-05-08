import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".codelens_config"


def save_config(data: dict) -> None:
    existing = load_config()
    existing.update(data)
    CONFIG_PATH.write_text(json.dumps(existing, indent=2))


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())
