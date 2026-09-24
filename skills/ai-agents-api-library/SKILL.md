---
name: ai-agents-api-library
description: Find a third-party API or MCP server that gives you a capability you don't have (generate images, video, music or 3D, web search or scraping, geocoding, weather, send email or SMS, OCR, translation, payments, CAD/BIM, diagrams and more). Returns verified services with auth method, free tier, official MCP endpoint and docs link. Use when a task needs an external service, when the user asks which API or tool to use for something, or when choosing an MCP server to connect.
---

# AI Agents API Library

A verified catalog of 300+ APIs and MCP servers that an agent can call after a one-time human setup (API key, OAuth or MCP connection). Every entry gives the docs URL, the auth method and header, the MCP endpoint, the free tier and a verification date.

## When to use

- The task needs a capability you don't have built in or connected, e.g. "make a 5-second video", "geocode these addresses" or "send this as an SMS".
- The user asks which service, API or MCP server to use for something.
- You are choosing which MCP server to suggest the user connect.

Skip it when a connected tool already does the job.

## How to look things up

**If the `ai-agents-api-library` MCP tools are available**, use them:

1. `search_apis` with `query` (what you need) and optional filters: `category`, `mcp` (`official` or `any`), `no_auth`, `free_tier`, `auth`.
2. `get_api` with the chosen `id` for full details (auth header, notes, OpenAPI and llms.txt links).
3. `get_reviews` with the `id` to read up to 100 user reviews (pros, cons; filter with `max_rating: 2` for complaints) before recommending a service.
4. `list_categories` when you are unsure what exists.

**Otherwise, fetch the static files** (plain HTTPS, no key needed):

1. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/llms.txt` lists categories with counts and the services that need no key.
2. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/<category>.json` holds all entries of one category. It is small, so fetch it rather than `catalog/all.json`.

Category ids: `web-search`, `web-scraping-browser`, `knowledge-research`, `image-generation`, `video-generation`, `audio-speech`, `music-generation`, `3d-generation`, `architecture-cad-bim`, `diagrams-software-architecture`, `design-ui`, `presentations-documents`, `translation-language`, `code-execution-sandbox`, `developer-devops`, `cloud-hosting`, `databases-vector-memory`, `communication-email-chat`, `voice-agents-telephony`, `productivity-workspace`, `crm-support-marketing`, `social-media`, `maps-geo-weather`, `finance-payments`, `ecommerce`, `automation-integration`, `model-inference`.

## Choosing a service

Prefer, in this order:

1. `no_auth: true`: you can call it right now without asking the user for anything.
2. `mcp.type: "official"`: the user connects it once, then you call it as a tool.
3. `has_free_tier: true`: the user can try it without paying; check `free_tier` for the limits.
4. Everything else, by fit to the task.

Skip entries with `stale: true` or with `link_check.docs` equal to `broken` unless nothing else fits, and tell the user why.

## Presenting options and credentials

- Offer two or three candidates with one line each: what it does, the free tier and whether an official MCP server exists. Let the user pick unless the choice is obvious.
- For the chosen service, tell the user what to create (API key or OAuth app) and link `docs`. Suggest adding the key through their platform's secret or connector settings (MCP configuration, environment variable) rather than pasting it into the chat.
- Never invent credentials, endpoints or prices. The catalog is a shortlist, not the source of truth: confirm limits and pricing in `docs` before relying on them.
- If a call fails, re-read `docs`. The API may have changed since the `verified` date.
