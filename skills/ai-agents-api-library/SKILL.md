---
name: ai-agents-api-library
description: Find a third-party API or MCP server for an operation you cannot do yourself or with connected tools (generate video, images, music or 3D, web search or scraping, geocoding, weather, send email or SMS, OCR, speech, payments, CAD/BIM and more). Returns catalog entries with auth method, free plan, MCP endpoint, docs link, and for popular services an example request and unit price. Use when a task needs an external service, when the user asks which API or MCP server to use, or when your own attempt at a call failed (403, rate limit, unsupported format) and another service would unblock the task.
---

# AI Agents API Library

A catalog of 300+ APIs and MCP servers that an agent can call once a human has provisioned credentials (API key, OAuth or MCP connection). Each entry gives the docs URL, the auth method and header, the MCP server, the free plan and a last-checked date. Popular services also carry a minimal example request (`call`) and the price of one operation (`unit_price`).

"Last checked" (`verified`, `link_check`) means links and listed facts were checked on that date. It does not prove that a service does your exact task, and ranking is not proof of fit.

## When to use

- The task needs an external service: "make a 5-second video", "geocode 200 addresses", "send this as an SMS".
- The user asks which service, API or MCP server to use for something.
- Your own direct attempt failed (403, quota or rate limit, unsupported format) and a different service would unblock the task.

Skip it when a built-in or connected tool already does the job, or when you can do it yourself: translating text, drawing a Mermaid or SVG diagram, writing code, summarizing.

## How to look things up

**If the `ai-agents-api-library` MCP tools are available**, use them:

1. `search_apis` with `query` naming the operation (the verb, e.g. "text to video", "street address geocoding", "send sms") and optional filters: `category`, `mcp` (`official`, `remote` for a hosted endpoint with nothing to install, or `any`), `no_auth`, `free_tier`, `no_card` (free plan without a payment card), `auth`.
2. `get_api` with the chosen `id` for full details: auth header, `call` example, `unit_price`, `rate_limits`, `mcp.config`, notes.
3. Optional: `get_reviews` with the `id` when real-world quality matters (filter with `max_rating: 2` for complaints).
4. `list_categories` to see which categories exist before searching by `category`.

If no result does the requested operation, say so. Retry once with `category`, then fall back to web search. Do not settle for an adjacent service (video hosting is not video generation; messaging apps are not SMS).

**Otherwise, fetch the static files** (plain HTTPS, no key needed):

1. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/llms.txt` lists categories with counts and the services that need no key.
2. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/<category>.json` holds all entries of one category. It is small, so fetch it rather than `catalog/all.json`.

Category ids: `web-search`, `web-scraping-browser`, `knowledge-research`, `image-generation`, `video-generation`, `audio-speech`, `music-generation`, `3d-generation`, `architecture-cad-bim`, `diagrams-software-architecture`, `design-ui`, `presentations-documents`, `translation-language`, `code-execution-sandbox`, `developer-devops`, `cloud-hosting`, `databases-vector-memory`, `communication-email-chat`, `voice-agents-telephony`, `productivity-workspace`, `crm-support-marketing`, `social-media`, `maps-geo-weather`, `finance-payments`, `ecommerce`, `automation-integration`, `model-inference`.

## Choosing a service

1. **Fit first.** Keep only entries whose `desc_en` (or `call.operation`) is the exact operation asked for, and whose `rate_limits`, `notes` and terms allow the volume. A no-key service that forbids bulk use is out for a batch job.
2. **Then compare access and cost** among the entries that fit:
   - `no_auth: true`: callable now, without asking the user for anything.
   - An MCP server the user can connect: check `mcp.kind` and `mcp.config`. A remote endpoint (`transport` `streamable-http` or `sse`) is connected once; a `stdio` server or a GitHub repo must be installed; `docs_only: true` means the server only searches documentation and cannot perform the operation.
   - Free use: `free_plan.kind` `free_tier` is a lasting free quota; `trial` is one-off credit that runs out, often with restrictions (e.g. only verified phone numbers). Check `free_plan.requires_card` and compare `unit_price` with the expected volume.
3. Skip entries with `stale: true` or `link_check.docs` equal to `broken` unless nothing else fits, and tell the user why.

## Presenting options and credentials

- Offer two or three candidates with one line each: what it does, free plan or unit price, and how it connects (no key, remote MCP, install, REST). Let the user pick unless the choice is obvious.
- For the chosen service, tell the user what to create (API key or OAuth app) and link `docs`. Suggest adding the key through their platform's secret or connector settings (MCP configuration, environment variable) rather than pasting it into the chat.
- Before calling or recommending for a batch, a zero budget or an action that reaches third parties (SMS, email, payments), check quotas, terms, real cost and authorization.
- Never invent credentials, endpoints or prices. The catalog is a shortlist, not the source of truth: confirm limits and pricing in `docs` (or the `source_url` of each field) before relying on them.
- Start from `call.example` when present, replacing the placeholders. If a call fails, re-read `docs`: the API may have changed since the last-checked date.
