# Notion Agent Hub

A customization hub for managing Notion workspaces through an agent-driven workflow. Drop request files into `requests/`, and the agent reads them, resolves targets, executes operations via the Notion API, and marks them done.

## Repository Structure

```
notion-agent-hub/
├── CLAUDE.md                # Agent instructions and workflow
├── notion-config.json       # Friendly name -> Notion ID mappings
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── requests/
│   ├── _template.md         # Request frontmatter template
│   └── example-create-project-tracker.md
├── templates/
│   ├── project-tracker.json # Database template
│   ├── meeting-notes.json   # Page template
│   └── dashboard.json       # Page template
└── scripts/
    └── notion_client.py     # CLI client for the Notion API
```

## Setup

1. **Clone the repo** and create a virtual environment:

   ```bash
   git clone <repo-url> && cd notion-agent-hub
   python3 -m venv .venv && source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Notion token:**

   ```bash
   cp .env.example .env
   # Edit .env and set NOTION_API_TOKEN to your integration token
   ```

4. **Add your Notion IDs** to `notion-config.json`, replacing the placeholder values with real page/database IDs from your workspace.

## Templates

| Template | Type | Description |
|---|---|---|
| `project-tracker` | Database | Name, Status, Priority, Due Date, Owner, Tags |
| `meeting-notes` | Page | Attendees, Agenda, Notes, Action Items sections |
| `dashboard` | Page | Overview callout, Active Projects, Recent Notes |

## CLI Examples

All commands use `scripts/notion_client.py` and accept either a friendly name from `notion-config.json` or a raw Notion ID.

```bash
# Create a page under the team wiki
python scripts/notion_client.py create-page --target team-wiki --title "Sprint Planning"

# Create a database from a template
python scripts/notion_client.py create-db --target team-wiki --template project-tracker

# Create a meeting notes page from a template
python scripts/notion_client.py create-page --target meeting-notes --template meeting-notes

# Get a page
python scripts/notion_client.py get-page --target dashboard

# Query a database
python scripts/notion_client.py query-db --target project-db

# Query with a filter
python scripts/notion_client.py query-db --target project-db \
  --filter '{"property": "Status", "select": {"equals": "In Progress"}}'

# Update page properties
python scripts/notion_client.py update-page --target project-db \
  --properties '{"Status": {"select": {"name": "Done"}}}'

# Append blocks to a page
python scripts/notion_client.py append-blocks --target team-wiki \
  --blocks '[{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Hello from the CLI"}}]}}]'
```

## Creating Requests

Copy `requests/_template.md` and fill in the frontmatter:

```yaml
---
status: pending
target: "team-wiki"
notion_id: ""
template: "meeting-notes"
priority: high
---
```

The agent picks up files with `status: pending`, executes them, and sets `status: done` or `status: error`.
