import json
import os
import re
from datetime import datetime, timezone


STORIES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stories")


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text.strip())
    return text or "untitled"


def save_scene(title: str, text: str) -> str:
    """Save a scene to the stories directory as a JSON file.

    Returns the path to the saved file.
    """
    os.makedirs(STORIES_DIR, exist_ok=True)

    slug = _slugify(title)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{slug}_{timestamp}.json"
    filepath = os.path.join(STORIES_DIR, filename)

    scene_data = {
        "title": title,
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scene_data, f, ensure_ascii=False, indent=2)

    return filepath
