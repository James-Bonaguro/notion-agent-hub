#!/usr/bin/env python3
"""Create a new project page under a parent page in Notion.

Usage:
    python scripts/create_project.py "My Project Name" --parent <page-id-or-friendly-name>
    python scripts/create_project.py "My Project Name" --parent project-db

Optional:
    --template   Template name (default: project-page)
    --icon       Emoji icon for the page (default: 🚀)
"""

import argparse
import copy
import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "notion-config.json"
TEMPLATES_DIR = ROOT / "templates"


def get_client() -> Client:
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        print("Error: NOTION_API_TOKEN is not set. See .env.example.", file=sys.stderr)
        sys.exit(1)
    return Client(auth=token)


def resolve_target(name: str) -> str:
    cleaned = name.replace("-", "")
    if len(cleaned) == 32 and all(c in "0123456789abcdef" for c in cleaned):
        return name
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    targets = config.get("targets", {})
    if name not in targets:
        print(f"Error: Target '{name}' not found in notion-config.json", file=sys.stderr)
        print(f"Available targets: {', '.join(targets.keys())}", file=sys.stderr)
        sys.exit(1)
    return targets[name]["id"]


def load_template(name: str) -> dict:
    path = TEMPLATES_DIR / f"{name}.json"
    if not path.exists():
        print(f"Error: Template '{name}' not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def replace_placeholders(obj, replacements: dict):
    """Recursively replace {{PLACEHOLDER}} strings in a template."""
    if isinstance(obj, str):
        for key, value in replacements.items():
            obj = obj.replace(f"{{{{{key}}}}}", value)
        return obj
    elif isinstance(obj, list):
        return [replace_placeholders(item, replacements) for item in obj]
    elif isinstance(obj, dict):
        return {k: replace_placeholders(v, replacements) for k, v in obj.items()}
    return obj


def create_project_page(client: Client, parent_id: str, project_name: str,
                        template_name: str = "project-page", icon: str = "🚀") -> dict:
    template = load_template(template_name)
    body = copy.deepcopy(template)

    replacements = {
        "PROJECT_NAME": project_name,
        "DATE": date.today().isoformat(),
    }
    body = replace_placeholders(body, replacements)

    body["parent"] = {"page_id": parent_id}
    body["icon"] = {"type": "emoji", "emoji": icon}

    body.pop("object", None)

    result = client.pages.create(**body)
    return result


def main():
    parser = argparse.ArgumentParser(description="Create a new Notion project page")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--parent", required=True,
                        help="Parent page ID or friendly name from notion-config.json")
    parser.add_argument("--template", default="project-page",
                        help="Template name (default: project-page)")
    parser.add_argument("--icon", default="🚀",
                        help="Emoji icon for the project page (default: 🚀)")
    args = parser.parse_args()

    client = get_client()
    parent_id = resolve_target(args.parent)

    print(f"Creating project page: {args.name}")
    print(f"  Parent: {args.parent} ({parent_id})")
    print(f"  Template: {args.template}")
    print(f"  Icon: {args.icon}")
    print()

    result = create_project_page(client, parent_id, args.name, args.template, args.icon)

    page_id = result["id"]
    url = result.get("url", "")
    print(f"Project page created!")
    print(f"  ID:  {page_id}")
    print(f"  URL: {url}")

    return result


if __name__ == "__main__":
    main()
