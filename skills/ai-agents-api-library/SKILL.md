---
name: ai-agents-api-library
description: Find a third-party API or MCP server for an operation you cannot do with your model, built-in tools or currently connected tools (generate video, images, music or 3D, geocoding, weather, send email or SMS, OCR, speech, payments, CAD/BIM and more). Returns catalog entries with auth method, free plan vs trial, MCP endpoint, docs link, an example request and unit price. Use when a task needs such an operation, when the user asks which API or MCP server to use, when the user names a service you are about to use for a batch, a message or a payment, or when a call failed for a service-side reason you can't fix and another service would unblock the task.
---

# AI Agents API Library

A catalog of 300+ APIs and MCP servers that an agent can call once a human has provisioned credentials (API key, OAuth or MCP connection). Each entry gives the docs URL, the auth method and header, the MCP server, the free plan and a last-checked date. Popular services also carry a minimal example request (`call`) and the price of one operation (`unit_price`).

"Last checked" (`verified`, `link_check`) means links and listed facts were checked on that date. It does not prove that a service does your exact task. Results are ranked by operation fit, evidence, lasting free plan, card and auth effort and bulk limits, not by your budget or region.

## When to use

- The task needs an operation unavailable through your model, built-in tools or currently connected tools: "make a 5-second video", "geocode 200 addresses", "send this as an SMS". One quick check: if you cannot name the tool that does it, search.
- The user asks which service, API or MCP server to use for something.
- The user names a service ("geocode with Nominatim", "send it through Twilio"), or you are about to use one for a batch, a message, a payment or another third-party action: call `get_api` first. A vendor you already know is not a checked vendor; the entry shows bulk bans, docs-only MCP servers and trial limits.
- A call failed for a service-side reason you can't fix (auth rejected after checking permissions, quota, billing required, unsupported format or region) and a different service would unblock the task. Not after a malformed request of your own: fix that first.

Skip it when a built-in or connected tool already does the job within this task's volume, cost and data limits, or when you can do it yourself: translating text, drawing a Mermaid or SVG diagram, writing code, summarizing. If that tool is exhausted or lacks a required option, search anyway.

## How to look things up

**If the `ai-agents-api-library` MCP tools are available**, use them:

1. `search_apis` with `query` naming the operation (the verb, e.g. "text to video", "street address geocoding", "send sms") and optional filters: `category`, `mcp` (`official`, `remote` for a hosted endpoint with nothing to install, or `any`; docs-only servers never count), `no_auth`, `free_tier` (lasting free use; add `include_trials` to accept one-off credits), `no_card` (free plan without a payment card), `auth`, `volume` (`bulk` for batch jobs).
   Each result has `match`: `exact` = the entry lists the operation and its example call or an MCP tool performs it; `listed` = the entry lists it without that evidence; `adjacent` = a related operation. `exact` is still a search label: check that the endpoint or tool accepts the user's actual inputs (text vs image, country, format). `mcp_fit` says whether the MCP server has a tool for the operation.
2. `get_api` with the chosen `id` for full details: auth header, `call` example, `unit_price`, `rate_limits`, `mcp.config`, notes.
3. Optional: `get_reviews` with the `id` when real-world quality matters (filter with `max_rating: 2` for complaints).
4. `list_categories` to see which categories exist before searching by `category`.

If no result does the requested operation, say so. Retry once with `category`, then fall back to web search. Do not settle for an adjacent service (video hosting is not video generation; messaging apps are not SMS).

**Otherwise, fetch the static files** (plain HTTPS, no key needed):

1. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/llms.txt` lists categories with counts and the services that need no key.
2. `https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/<category>.json` holds all entries of one category. It is small, so fetch it rather than `catalog/all.json`.

Category ids: `web-search`, `web-scraping-browser`, `knowledge-research`, `image-generation`, `video-generation`, `audio-speech`, `music-generation`, `3d-generation`, `architecture-cad-bim`, `diagrams-software-architecture`, `design-ui`, `presentations-documents`, `translation-language`, `code-execution-sandbox`, `developer-devops`, `cloud-hosting`, `databases`, `databases-vector-memory`, `communication-email-chat`, `sms-messaging`, `voice-agents-telephony`, `productivity-workspace`, `crm-support-marketing`, `social-media`, `maps-geo-weather`, `finance-payments`, `ecommerce`, `automation-integration`, `model-inference`.

## Choosing a service

1. **Fit first.** Keep only entries whose `desc_en` (or `call.operation`) is the exact operation asked for, and whose `rate_limits`, `notes` and terms allow the volume. A no-key service that forbids bulk use is out for a batch job.
2. **Then compare access and cost** among the entries that fit:
   - `no_auth: true`: no credential required; check permitted use and volume before calling.
   - An MCP server the user can connect: check `mcp.kind`, `mcp.config` and `mcp_fit`. A hosted endpoint (`transport` `streamable-http` or `sse`) needs no installation, but may still require connection, authentication and a tool for the operation; a `stdio` server or a GitHub repo must be installed; `docs_only: true` means the server only searches documentation and cannot perform the operation.
   - Free use: `free_plan.kind` `free_tier` is a lasting free quota; `trial` is one-off credit that runs out, often with restrictions (e.g. only verified phone numbers). On a zero budget, expect many "free" offers to be trials. Check `free_plan.requires_card` and compare `unit_price` with the expected volume.
3. Skip entries with `stale: true` or `link_check.docs` equal to `broken` unless nothing else fits, and tell the user why.

## Presenting options and credentials

- Offer two or three candidates with one line each: what it does, free plan or unit price, and how it connects (no key, remote MCP, install, REST). Let the user pick unless the choice is obvious.
- For the chosen service, tell the user what to create (API key or OAuth app) and link `docs`. Suggest adding the key through their platform's secret or connector settings (MCP configuration, environment variable) rather than pasting it into the chat.
- Before calling or recommending for a batch, a zero budget or an action that reaches third parties (SMS, email, payments), check quotas, terms, real cost and authorization.
- Never invent credentials, endpoints or prices. Fields with a `source_url` and check date are good enough for a first cheap, read-only call; confirm pricing only beyond the free quota, and terms for batch or commercial use.
- Start from `call.example` only if its operation and required inputs match the task, replacing the placeholders. If a call fails, re-read `docs`: the API may have changed since the last-checked date.
