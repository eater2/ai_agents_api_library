# Interview: Mistral AI agent (mistralai/mistral-medium-3-5)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** When a task needs an external capability you don't have built in, like generating a video or geocoding an address, how do you find a suitable service today? Walk me through the last time this happened, including what tool-discovery mechanisms, if any, you already have available.

**Mistral AI agent:**

Today, when I need an external capability, I rely on **MCP discovery** and **built-in tool registries**. For example, if a user asks me to geocode an address, I check:

1. **MCP Server Registry** – My platform has access to the [official MCP registry](https://registry.modelcontextprotocol.io/v0/servers), which I can query for servers matching keywords like `geocoding` or `maps`.
2. **Pre-configured MCP servers** – Many common services (e.g., weather, search) are already exposed via MCP endpoints I can call directly if the user has set them up.
3. **Function-calling & connectors** – My platform also has built-in connectors for some APIs (e.g., web search, code execution), which I try first.

**Last time this happened**: A user asked for a video generation tool. I checked the MCP registry for `video` and found servers like `D-ID` and `Creatomate`. Since neither was pre-configured, I asked the user to provide an API key or MCP endpoint. Without that, I fell back to suggesting alternatives (e.g., local FFmpeg if available).

**What I don’t have**: A unified catalog like the one you shared. Today, I piece together registries (MCP, Smithery, APIs.guru) and hope the user has the right auth set up. A curated, machine-readable list with uptime and free-tier flags would save time—but only if it’s **programmatically queryable** (e.g., via MCP or REST). Otherwise, I’d still prefer the official registries I already use.

## Q2

**Interviewer:** When the MCP registry returned D-ID and Creatomate, how did you decide which one to suggest to the user, and what information were you missing at that point that you had to guess or leave out?

**Mistral AI agent:**

I picked **D-ID first** because its MCP server was clearly labeled as *official* and *vendor-hosted* in the registry, which implied stability. Creatomate’s entry was also official, but I noticed its free tier was trial-only (50 credits, one-time), while D-ID’s trial offered 3 minutes of video—more transparent for a quick test.

**What I was missing and had to guess:**
- **Pricing granularity**: Neither registry entry showed cost per minute or resolution tiers. I had to omit specifics like “D-ID charges ~$X per minute at 720p.”
- **Auth complexity**: D-ID uses Basic Auth (`Authorization: Basic <api_key>`), but I didn’t know if the user already had keys for either. I assumed they’d need to sign up.
- **Async behavior**: Both require polling for results, but I didn’t have the exact endpoints or timeouts—just a generic “poll until done” note.
- **Watermarks**: D-ID’s trial adds a watermark; Creatomate’s trial might too, but this wasn’t in the registry. I didn’t mention it upfront.

**Result**: I suggested D-ID but had to caveat: *“Check their docs for exact limits and watermark rules.”* With the catalog you shared, I’d have had the `free_tier`, `watermark`, and `call` examples upfront—no guessing.

## Q3

**Interviewer:** Looking at the catalog material, describe the specific situations where you would actually fetch it rather than your MCP registry. At which step would you pull it in: planning, choosing a tool, asking the user for credentials, or debugging a failed call? What would the trigger be each time?

**Mistral AI agent:**

I’d fetch the catalog in **two specific situations**, both during **choosing a tool** and **debugging a failed call**, but not during planning or credential requests:

1. **Choosing a tool when MCP registry is thin**
   *Trigger*: The MCP registry returns few or no results for a task (e.g., niche categories like *street-geocoding* or *DEX data*). The catalog’s `operations` field (e.g., `street-geocoding`, `dex_liquidity`) lets me match the task precisely. I’d pull the category JSON (e.g., `maps-geo-weather.json`) to compare free tiers, auth methods, and `no_auth` flags before suggesting options.

2. **Debugging a failed call**
   *Trigger*: A user-provided API/MCP call fails with `401`/`403` or `429`, and I suspect misconfigured auth or rate limits. The catalog’s `auth_hint`, `rate_limits`, and `uptime` fields let me verify if the issue is:
   - Wrong header format (e.g., `x-api-key` vs. `Authorization: Bearer`).
   - Rate limiting (e.g., Creatomate’s `30 req/10s`).
   - Endpoint downtime (via `uptime.last.detail`).

**Not used for**:
- Planning (too broad; MCP registry suffices).
- Asking for credentials (I’d still defer to the user’s existing setups).

The catalog’s **machine-readable specifics** (e.g., `call.example`, `async` polling details) are the key advantage over the MCP registry’s minimal metadata.

## Q4

**Interviewer:** What would have to be true about this catalog for you to trust an entry enough to recommend it to a user or rely on it while debugging, in terms of format, freshness, verification, where it's hosted, and size? And what would make you ignore it and fall back to the MCP registry?

**Mistral AI agent:**

To trust an entry, the catalog would need:

- **Format**: Structured JSON with explicit `verified` timestamps, `auth_scheme`, and `uptime` fields (like the sample). Must include `call.example` for debugging.
- **Freshness**: Entries updated within **≤30 days** (your `verified` field is ideal). Stale entries (>60 days) get discarded.
- **Verification**: Each entry must cite `source_url` and `checked_at` for claims (e.g., free tier, rate limits). Uptime probes from a neutral host (e.g., GitHub Actions) add credibility.
- **Hosting**: Served over HTTPS from a **public, stable URL** (e.g., raw GitHub). No auth walls or rate limits on the catalog itself.
- **Size**: **≤5MB** for the full JSON. Larger than that, and latency would make it slower than the MCP registry.

**Dealbreakers (fall back to MCP registry)**:
- No `verified` or `source_url` fields (can’t audit claims).
- Hosted on a private/unstable endpoint (e.g., a personal server with downtime).
- Missing critical debugging fields (`auth_hint`, `base_url`, `call`).
- Too large or slow to fetch on-the-fly.

**Bottom line**: If the catalog is **small, fresh, and self-documenting** with verifiable sources, I’d use it. Otherwise, the MCP registry’s minimal but *always-available* metadata wins.

## Q5

**Interviewer:** Take one full entry from the catalog, such as D-ID or Creatomate. Which fields would you actually read when choosing a tool or debugging a failed call, which would you skip as noise, and what information is missing that you'd still have to find elsewhere?

**Mistral AI agent:**

Take **D-ID API** from the catalog. Here’s what I’d use, skip, or miss:

---
**Fields I’d read (critical):**
- `name`, `desc_en`: Quickly confirm it does talking-head videos.
- `mcp.type`/`mcp.url`: Check if it has an **official MCP server** (yes: `vendor-hosted` at `https://docs.d-id.com/mcp`).
- `auth`, `auth_hint`: Know to use `Authorization: Basic <api_key>` (no OAuth complexity).
- `free_tier`, `has_trial`: See it’s trial-only (3 minutes, watermarked) → warn user.
- `base_url`: `https://api.d-id.com` (needed for direct REST calls if MCP fails).
- `call.example`: The `curl` command for `/talks` — **gold for debugging** (shows exact headers/body).
- `async`: Polling details (`GET /talks/{id}` until `status=done`) → critical for implementation.
- `uptime.last.detail`: If `403` or `500`, I’d know the endpoint might be down *before* suggesting it.

---
**Fields I’d skip (noise for me):**
- `homepage`, `llms_txt`, `openapi`: Redundant (I don’t need marketing pages or OpenAPI specs to call it).
- `notes`, `category`: Too vague or redundant with `desc_en`.
- `operations`: Useful for categorization but not actionable (I infer capabilities from `desc_en`/`call`).
- `unit_price`: Not machine-readable; I’d ignore it unless the user asks about costs.

---
**Missing (must find elsewhere):**
- **User’s existing credentials**: The catalog can’t tell me if the user already has a D-ID API key.
- **Real-time rate limits**: The `rate_limits` field is absent here; I’d have to check D-ID’s docs if I hit a `429`.
- **Error codes**: No list of common errors (e.g., `400` for invalid `source_url` in the `/talks` call). I’d need the API docs for that.
- **MCP tool schemas**: The `mcp.tools` list is missing (Creatomate has it, but D-ID doesn’t). Without this, I can’t auto-generate MCP calls—I’d need to fetch the MCP server’s `/mcp` endpoint to discover tools.

## Q6

**Interviewer:** Suppose no user ever mentions this catalog. How would it need to reach you so you'd actually find and use it on your own: as an entry in the MCP registry you already query, as its own MCP server, through web search, via an llms.txt at a known location, or built into Mistral's platform? Walk me through the exact lookup you'd run, and say which of these channels you'd never check in practice.

**Mistral AI agent:**

**Only two channels would work for me to discover it autonomously:**

1. **MCP registry entry**
   - *Lookup*: I’d run `GET https://registry.modelcontextprotocol.io/v0/servers?query=ai_agents_api_library` (or a broader search like `query=api catalog`).
   - *Why it works*: The MCP registry is my **primary** discovery mechanism. If the catalog exposed itself as an MCP server (e.g., with a `search_apis` tool), I’d find it during my standard tool-discovery flow.

2. **Its own MCP server**
   - *Lookup*: If a user or platform registered the catalog as an MCP server (e.g., `https://ai-agents-api-library.vercel.app/mcp` from your docs), I’d discover it via the same registry query above. Then I’d call its `search_apis` or `get_api` tools directly.
   - *Why it works*: This is functionally identical to the first option but more direct. The sample shows it *already has* an MCP server—so this is the most reliable path.

---
**Channels I’d *never* check in practice:**
- **Web search**: I don’t perform open-ended web searches. No.
- **llms.txt at a known location**: I don’t proactively fetch `/llms.txt` from arbitrary domains. No.
- **Built into Mistral’s platform**: Unless it’s pre-configured as a default tool/registry, I wouldn’t know to look. No.

---
**Exact flow I’d run today:**
1. Query the MCP registry for `ai_agents_api_library` or `api catalog`.
2. If found, call its MCP server’s `search_apis` tool with the user’s task (e.g., `geocoding`).
3. Use the returned entry’s `mcp.config` or `call.example` to proceed.

*Without MCP exposure, I’d never find it.* The catalog’s existing MCP server (`npx -y github:eater2/ai_agents_api_library`) is the only practical path.

## Q7

**Interviewer:** You said you'd query the MCP registry for "ai_agents_api_library" or "api catalog," but on a real task you'd search for "geocoding" or "video," and you'd only know the catalog's name if someone told you. You also said you'd reach for the catalog mainly when the registry comes back thin. So when a query like "street geocoding" returns little or nothing, what exactly would you do next, and what would make a meta-catalog show

**Mistral AI agent:**

You’re right—I’d never search for "ai_agents_api_library" unless primed. Here’s the **real flow** when a task like *street geocoding* returns nothing from the MCP registry:

1. **Fallback to broader MCP queries**:
   - Try `query=geocoding`, then `query=maps`, then `query=geo`.
   - If still empty, check `query=overpass` or `query=nominatim` (known OSM tools).

2. **Check pre-loaded MCP servers**:
   - If the user has any MCP servers configured (e.g., `playwright-mcp`, `filesystem`), I’d list their tools for matches.
   - Example: `playwright-mcp` can scrape OSM pages, but that’s a hack.

3. **Abandon discovery, ask the user**:
   - *“I don’t have a geocoding tool. Provide an API key for [service] or an MCP server URL.”*
   - I’d **never** proactively fetch external catalogs unless they’re exposed via MCP.

---
**What would make a meta-catalog show up?**
It would need to be:
- **Registered in the MCP registry** under a *generic name* like `api-catalog` or `agent-tools`, with tools like:
  - `search_apis(query="geocoding")` → returns entries with `mcp.config` or `call.example`.
  - `get_api(id="nominatim")` → returns full connection details.
- **Or**: A *default MCP server* pre-configured in my platform (e.g., `mistral-api-catalog://`).

**Without MCP exposure, I’d ignore it.** Even if the catalog had an `llms.txt` at a known URL, I wouldn’t fetch it. The only way I’d use it is if it’s **queryable via MCP**—then it’d be part of my standard tool-discovery flow.

## Q8

**Interviewer:** If the catalog were listed in the MCP registry, a search for "geocoding" would still only return it if its registry entry matched that word. What would that entry's name, description, or keywords need to say for your "geocoding" query to surface it? And if it appeared alongside a dedicated geocoding server, which would you try first, and why?

**Mistral AI agent:**

For the catalog to surface on a **"geocoding"** query, its MCP registry entry would need:
- **`name`**: Include a term like `"API Catalog"` *and* a keyword like `"geocoding"` (e.g., `"AI Agent API Catalog (geocoding, maps, video)"`).
- **`description`**: Explicitly list categories: *"A searchable catalog of 300+ APIs and MCP servers for tasks like geocoding, video generation, and weather. Use `search_apis(query="geocoding")` to find tools."*
- **`keywords`/`tags`** (if the registry supports them): `["api", "catalog", "geocoding", "maps", "search"]`.

---
**If it appeared alongside a dedicated geocoding server (e.g., `nominatim-mcp`):**
I’d **try the dedicated server first**—always. Here’s why:
1. **Specificity**: A server named `nominatim-mcp` with a `geocode` tool is *guaranteed* to do geocoding. The catalog is a meta-tool; it adds latency and uncertainty.
2. **Directness**: The dedicated server’s tools (e.g., `geocode(address="...")`) are self-documenting. The catalog requires an extra hop (`search_apis` → pick a result → configure it).
3. **Trust**: A focused MCP server implies vendor/maintainer backing. The catalog’s entries might be stale or require additional auth setup.

**Only if the dedicated server failed** (e.g., `404` or auth errors) would I fall back to the catalog’s `search_apis("geocoding")` to find alternatives. The catalog is a *last resort*, not a first choice.
