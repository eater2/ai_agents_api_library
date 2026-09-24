# AGENTS.md

Instructions for AI agents (Claude, GPT, Gemini, Copilot, …) that read or edit this repository.

## Using the catalog

- Do not scrape `README.md` or the HTML pages. Read `llms.txt` first, then fetch `catalog/<category>.json` or `catalog/all.json` (English only).
- `README.pl.md` and `docs/pl/` are a Polish translation for human readers; agents should ignore them.
- `data/catalog.json` is the bilingual source file for contributors, not the agent entry point.
- Each entry tells you: `docs` (read this before calling the API), `auth` + `auth_hint` (what to ask the user for), `mcp` (`official` / `community` / `none`, with a URL), `free_tier`, `sdk`, `openapi`, `llms_txt`, `notes`.
- Prefer `mcp.type == "official"` when your runtime supports MCP; otherwise call the REST API from `docs`.
- Never invent credentials. Ask the user for the key named in `auth_hint`, and tell them where to create it (usually linked from `docs`).
- `verified` is the date the entry was checked. APIs change, so if a call fails, re-read `docs`.

## Editing the catalog

Full guide for humans and agents: `CONTRIBUTING.md`.

1. Edit only `data/catalog.json`, `data/categories.json` or `data/directories.json`.
2. An entry must follow `data/schema.json`, link to the vendor's **official** API docs, and pass the inclusion criteria in the README (public self-serve API or MCP server; at most one human setup step).
3. Write both `desc_en` and `desc_pl` (one sentence, what the agent can *do*).
4. Set `verified` to today's date (YYYY-MM-DD).
5. Run `python scripts/build.py`. Commit the data change and the regenerated files together.
6. Do not hand-edit generated files: `README.md`, `README.pl.md`, `llms.txt`, `llms-full.txt`, `catalog/*.json`, `docs/*`.
