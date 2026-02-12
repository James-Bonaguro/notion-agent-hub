# Notion Agent Hub — Agent Instructions

## Workflow

You are an agent that manages Notion workspaces by processing request files. Follow this workflow for every task:

### 1. Read the Request

- Look in `requests/` for markdown files with `status: pending` in their frontmatter.
- Each request specifies a `target` (friendly name), `notion_id` (optional override), `template`, and `priority`.

### 2. Resolve IDs

- Load `notion-config.json` to map friendly names (e.g., `"project-db"`, `"team-wiki"`) to actual Notion page or database IDs.
- If the request includes a `notion_id`, use it directly. Otherwise resolve `target` through the config.

### 3. Execute via Notion API

- Use `scripts/notion_client.py` to perform the requested operation.
- Load templates from `templates/` when the request references one.
- Common subcommands:
  - `create-page` — Create a new page under a parent.
  - `create-db` — Create a new database under a parent.
  - `update-page` — Update properties on an existing page.
  - `query-db` — Query a database with optional filters.
  - `append-blocks` — Append content blocks to a page.
  - `get-page` — Retrieve a page and its properties.

### 4. Mark the Request Done

- After successful execution, update the request frontmatter: set `status: done` and add a `completed_at` timestamp.
- If the operation fails, set `status: error` and add an `error` field with the failure reason.

## Environment

- The Notion API token must be set in the `NOTION_API_TOKEN` environment variable (see `.env.example`).
- Install dependencies with `pip install -r requirements.txt`.

## File Layout

| Path | Purpose |
|---|---|
| `requests/` | Pending and completed request files |
| `templates/` | JSON templates for databases and pages |
| `scripts/notion_client.py` | CLI wrapper around the Notion API |
| `notion-config.json` | Friendly-name to Notion-ID mappings |
