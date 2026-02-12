# Notion Agent Hub

A customization hub for managing Notion workspaces through an agent-driven workflow. Drop request files into `requests/`, and the agent reads them, resolves targets, executes operations via the Notion API, and marks them done.

## Repository Structure

```
notion-agent-hub/
├── CLAUDE.md                  # Agent instructions and workflow
├── notion-config.json         # Friendly name -> Notion ID mappings
├── .env.example               # Environment variable template
├── requirements.txt           # Python dependencies
├── requests/
│   ├── _template.md           # Request frontmatter template
│   ├── create-project-page.md # Example: create a project page
│   └── example-create-project-tracker.md
├── templates/
│   ├── project-page.json      # Full project page with all sections
│   ├── project-meeting.json   # Meeting notes scoped to a project
│   ├── project-tracker.json   # Database template
│   ├── meeting-notes.json     # Standalone meeting notes page
│   └── dashboard.json         # Dashboard page
└── scripts/
    ├── notion_client.py       # CLI client for the Notion API
    └── create_project.py      # One-command project page creator
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
| `project-page` | Page | Full project page: Overview, Timeline, Tasks, Meetings, Resources, Decisions, Risks, Retro |
| `project-meeting` | Page | Meeting notes scoped to a specific project |
| `project-tracker` | Database | Name, Status, Priority, Due Date, Owner, Tags |
| `meeting-notes` | Page | Standalone meeting notes: Attendees, Agenda, Notes, Action Items |
| `dashboard` | Page | Overview callout, Active Projects, Recent Notes |

### Project Page Sections

The `project-page` template creates a structured page with these sections:

1. **Overview** — Goal, Scope, and Success Criteria (checkboxes)
2. **Timeline & Milestones** — Start/end dates and milestone checkboxes
3. **Tasks** — To Do / In Progress / Completed sections
4. **Meetings & Notes** — Space for project-specific meeting sub-pages
5. **Resources & Links** — External references, docs, repos, drives
6. **Decisions Log** — Numbered decisions with date and rationale
7. **Risks & Blockers** — Table with Risk, Impact, and Mitigation columns
8. **Retrospective** — What went well, what to improve, action items

## Quick Start: Create a Project Page

```bash
# Create a project page with one command
python scripts/create_project.py "My New Project" --parent projects

# With a custom icon
python scripts/create_project.py "Mobile App Redesign" --parent projects --icon 📱
```

## CLI Examples

All commands use `scripts/notion_client.py` and accept either a friendly name from `notion-config.json` or a raw Notion ID.

```bash
# Create a project page from template
python scripts/notion_client.py create-page --target projects --template project-page

# Create a page with a title
python scripts/notion_client.py create-page --target projects --title "Sprint Planning"

# Create a database from a template
python scripts/notion_client.py create-db --target projects --template project-tracker

# Get a page
python scripts/notion_client.py get-page --target projects

# Query a database
python scripts/notion_client.py query-db --target projects

# Query with a filter
python scripts/notion_client.py query-db --target projects \
  --filter '{"property": "Status", "select": {"equals": "In Progress"}}'

# Update page properties
python scripts/notion_client.py update-page --target projects \
  --properties '{"Status": {"select": {"name": "Done"}}}'

# Append blocks to a page
python scripts/notion_client.py append-blocks --target projects \
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
