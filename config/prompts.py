"""
config/prompts.py

Loads agent prompts from PROMPT_DIR or from environment variables.
This file contains no actual prompts — all prompts live in a private repository
and are loaded at runtime via the PROMPT_DIR environment variable.
"""

import os
from pathlib import Path
from config import settings


def load_prompt(prompt_key: str) -> str:
    """Load a prompt file by key from PROMPT_DIR."""
    if not settings.PROMPT_DIR:
        raise EnvironmentError("PROMPT_DIR is not set.")
    prompt_file = Path(settings.PROMPT_DIR) / f"{prompt_key}.md"
    if not prompt_file.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8").strip()
