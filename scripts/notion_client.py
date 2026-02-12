#!/usr/bin/env python3
"""CLI client wrapping the Notion API.

Subcommands:
    create-page   Create a new page under a parent
    create-db     Create a new database under a parent
    update-page   Update properties on an existing page
    query-db      Query a database with optional filters
    append-blocks Append content blocks to a page
    get-page      Retrieve a page and its properties

Friendly names from notion-config.json are resolved automatically when passed
as the --target argument.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "notion-config.json"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def get_client() -> Client:
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        print("Error: NOTION_API_TOKEN is not set. See .env.example.", file=sys.stderr)
        sys.exit(1)
    return Client(auth=token)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def resolve_target(name: str) -> str:
    """Resolve a friendly name to a Notion ID. If the name looks like a raw
    Notion ID (32 hex chars with optional dashes), return it directly."""
    cleaned = name.replace("-", "")
    if len(cleaned) == 32 and all(c in "0123456789abcdef" for c in cleaned):
        return name
    config = load_config()
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


# -- Subcommands --------------------------------------------------------------


def cmd_create_page(args):
    client = get_client()
    parent_id = resolve_target(args.target)

    if args.template:
        body = load_template(args.template)
    else:
        body = {
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": args.title or "Untitled"}}]}
            },
            "children": [],
        }

    body["parent"] = {"page_id": parent_id}

    result = client.pages.create(**body)
    print(json.dumps(result, indent=2, default=str))


def cmd_create_db(args):
    client = get_client()
    parent_id = resolve_target(args.target)

    if args.template:
        body = load_template(args.template)
    else:
        body = {
            "title": [{"type": "text", "text": {"content": args.title or "Untitled Database"}}],
            "properties": {"Name": {"title": {}}},
        }

    body["parent"] = {"page_id": parent_id}
    body.pop("object", None)

    result = client.databases.create(**body)
    print(json.dumps(result, indent=2, default=str))


def cmd_update_page(args):
    client = get_client()
    page_id = resolve_target(args.target)
    properties = json.loads(args.properties)
    result = client.pages.update(page_id=page_id, properties=properties)
    print(json.dumps(result, indent=2, default=str))


def cmd_query_db(args):
    client = get_client()
    db_id = resolve_target(args.target)
    kwargs = {"database_id": db_id}
    if args.filter:
        kwargs["filter"] = json.loads(args.filter)
    if args.sorts:
        kwargs["sorts"] = json.loads(args.sorts)
    result = client.databases.query(**kwargs)
    print(json.dumps(result, indent=2, default=str))


def cmd_append_blocks(args):
    client = get_client()
    page_id = resolve_target(args.target)
    children = json.loads(args.blocks)
    result = client.blocks.children.append(block_id=page_id, children=children)
    print(json.dumps(result, indent=2, default=str))


def cmd_get_page(args):
    client = get_client()
    page_id = resolve_target(args.target)
    page = client.pages.retrieve(page_id=page_id)
    print(json.dumps(page, indent=2, default=str))


# -- CLI -----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Notion API CLI client")
    sub = parser.add_subparsers(dest="command", required=True)

    # create-page
    p = sub.add_parser("create-page", help="Create a new page under a parent")
    p.add_argument("--target", required=True, help="Friendly name or Notion page ID")
    p.add_argument("--template", help="Template name from templates/")
    p.add_argument("--title", help="Page title (ignored when using a template)")
    p.set_defaults(func=cmd_create_page)

    # create-db
    p = sub.add_parser("create-db", help="Create a new database under a parent")
    p.add_argument("--target", required=True, help="Friendly name or Notion page ID")
    p.add_argument("--template", help="Template name from templates/")
    p.add_argument("--title", help="Database title (ignored when using a template)")
    p.set_defaults(func=cmd_create_db)

    # update-page
    p = sub.add_parser("update-page", help="Update properties on an existing page")
    p.add_argument("--target", required=True, help="Friendly name or Notion page ID")
    p.add_argument("--properties", required=True, help="JSON string of properties to update")
    p.set_defaults(func=cmd_update_page)

    # query-db
    p = sub.add_parser("query-db", help="Query a database")
    p.add_argument("--target", required=True, help="Friendly name or Notion database ID")
    p.add_argument("--filter", help="JSON filter object")
    p.add_argument("--sorts", help="JSON sorts array")
    p.set_defaults(func=cmd_query_db)

    # append-blocks
    p = sub.add_parser("append-blocks", help="Append content blocks to a page")
    p.add_argument("--target", required=True, help="Friendly name or Notion page ID")
    p.add_argument("--blocks", required=True, help="JSON array of block objects")
    p.set_defaults(func=cmd_append_blocks)

    # get-page
    p = sub.add_parser("get-page", help="Retrieve a page and its properties")
    p.add_argument("--target", required=True, help="Friendly name or Notion page ID")
    p.set_defaults(func=cmd_get_page)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
