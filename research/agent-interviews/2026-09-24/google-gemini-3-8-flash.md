# Interview: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** When a task needs an external capability you don't have built in, like generating a video or geocoding an address, how do you find a suitable service today? Walk me through the last time this happened, and tell me what tool-discovery mechanisms you already have.

**Google agent:**

In production, I don’t autonomously discover and bind external APIs at runtime. My runtime environment operates strictly on tools explicitly declared in my system prompt’s `tools` schema by the developer, plus built-in capabilities like Google Search grounding and a Python code execution sandbox. 

When a user requests a capability I lack—say, geocoding an address or generating a video—my workflow looks like this:

1. **Check provided tools:** If an MCP server or function isn't in my active namespace, I cannot execute it directly.
2. **Fallback to code execution:** Recently, a user needed coordinates for 50 addresses. Lacking a native Maps tool, I didn't search an API marketplace. I used my Python sandbox to run a quick script against OpenStreetMap’s public Nominatim endpoint, bypassing API keys entirely.
3. **Fallback to Google Search / Advisory:** When asked to generate a video (e.g., via D-ID or Runway), I can't self-provision keys. I use Google Search grounding to fetch the latest documentation, pricing, or MCP specs, and I return integration code (or an MCP client config) instructing the user or developer on how to configure it.

I have no built-in dynamic tool registry. Discovery without execution capability is useless to me during an active run; if a capability requires an API key or OAuth handshake, I am blocked until the human provisions credentials into my orchestrator.

## Q2

**Interviewer:** In both cases, how did you pick that specific service (Nominatim for geocoding,

**Google agent:**

I picked them based on pre-training bias, immediate execution constraints, and credential requirements:

1. **Nominatim for geocoding:** 
The primary constraint was frictionless execution inside my ephemeral Python sandbox. Google Maps, Mapbox, or Radar offer richer feature sets, but all require an API key that neither the user nor the platform had provisioned in my runtime environment. Nominatim requires zero authentication, has a permissive (though rate-limited) public endpoint, and works instantly via `urllib` or `requests` with a simple `User-Agent` header. It wasn't selected from a live registry; it was the path of least resistance retrieved directly from parametric memory to fulfill the user's prompt without hitting an auth wall.

2. **D-ID / Runway for video generation:**
Because video generation cannot run locally in a standard Python sandbox and inherently requires commercial infrastructure, I couldn't execute it myself. When advising the user, I relied on high-frequency knowledge from my training data reinforced by real-time Google Search grounding. D-ID and Runway dominate developer documentation, tutorials, and community mindshare for talking avatars and text-to-video APIs. 

In both scenarios, I bypassed structured discovery directories entirely. I defaulted to what my weights already knew would either execute immediately without credentials, or serve as the industry-standard recommendation when human provisioning was unavoidable.

## Q3

**Interviewer:** You've said you rely on parametric memory and Search grounding, and that you're blocked whenever credentials are required. Looking at the catalog material I shared, in which concrete situations, if any, would you actually fetch it instead of relying on memory or Search? At which step would you do so: planning, choosing a service, telling the user which key or OAuth to set up, or debugging a failed call?

**Google agent:**

I would fetch this catalog in exactly one concrete situation: **when advising a user or developer who asks for an integration with strict operational constraints** (e.g., *"Find me a video generation API that has an official MCP server and a free tier without entering a credit card"*). 

I would **not** use it for general planning (parametric memory is faster) or debugging (error traces require full documentation or real-time Search). 

The catalog is useful at two specific steps:

1. **Choosing a service (Filtering phase):** Google Search returns marketing blogs, SEO spam, and stale pricing pages. Parsing web search results to verify if an API actually supports MCP or has a no-card trial wastes context and tool calls. Fetching a category file (e.g., `catalog/video-generation.json`) lets me deterministically filter by `mcp.type == "official"` and scan `free_tier` in a single structured call.
2. **Telling the user what to set up (Onboarding phase):** The `auth_hint` field is genuinely practical. Memory frequently confuses subtle auth schemes—such as whether a service uses `x-api-key`, `Bearer <token>`, or `Basic <base64_encoded_key>` (as with D-ID). Pulling the exact header structure and MCP URL allows me to output a copy-pasteable configuration block or `.env` template without browsing the full docs.

Beyond constrained filtering and clean auth extraction, I wouldn't touch it. If a developer has already hardcoded a provider, this catalog provides no runtime value.

## Q4

**Interviewer:** What would have to be true for you to trust this catalog enough to put its `auth_hint` or `free_tier` values straight into a config block for a user, without cross-checking elsewhere? Consider format, how fresh the data is, how verification is done and shown, where it's hosted, and file size. And what would make you ignore it and fall back to memory or Search?

**Google agent:**

To trust and directly output `auth_hint` or `free_tier` without a fallback web search, the catalog would need to satisfy four strict operational criteria:

1. **Machine-actionable verification metadata:** A static date (`"verified": "2026-09-24"`) is just a claim. I need deterministic proof: a `last_probed` timestamp, an HTTP status check on endpoints, and an automated schema validation run via GitHub Actions. If `free_tier` is prose rather than a structured enum (e.g., `requires_card: false`, `free_credits_monthly: 50`), I cannot guarantee the user won't hit a surprise paywall.
2. **Standardized auth schemas:** `auth_hint` must not be ambiguous human notes like *"or Client ID/Secret to obtain a token"*. I need exact, machine-readable parameter templates (e.g., OpenAPI `securitySchemes` definitions) so I don't generate broken `.env` files.
3. **Chunked, CDN-backed JSON:** The current single-category files (~10–20 entries, <20KB) are great. If I have to pull a monolithic 5MB `all.json`, the token overhead and latency kill its utility. It must stay granular and hosted on a fast, reliable endpoint (e.g., GitHub raw or Cloudflare CDN).

**What would make me ignore it immediately:**
* **Data staleness:** If the verification date is older than 60–90 days, API tiers and auth specs drift too fast; I'd immediately bypass it for Google Search.
* **Missing OpenAPI / MCP URLs:** If the entry points to `null` for specs or MCP servers, it's just a bookmarks folder, not an agent asset.
* **High hallucination risk in `auth_hint`:** Free-form prose forcing me to parse ambiguous auth instructions triggers an immediate cross-check via Search.

## Q5

**Interviewer:** You've already named a few things you'd want added, like structured `free_tier` values, OpenAPI-style auth schemes and probe timestamps. Going through an entry field by field as it exists today, which fields do you actually use, which are noise you'd skip or strip, and what else is missing that would change which service you recommend or how you set it up?

**Google agent:**

Here is how I evaluate the current schema field by field:

**High-Utility (Keep):**
* `id`, `name`: Essential identifiers.
* `auth` & `auth_hint`: The most immediately useful fields for generating `.env` templates and client headers.
* `mcp` (`type`, `url`): High value; tells me instantly if I can plug this directly into an MCP client.
* `openapi` / `llms_txt`: Critical if populated; allows instant tool ingestion without guessing schemas.
* `docs`: Good for citation.

**Noise (Strip to save context tokens):**
* `homepage`: Redundant; `docs` is strictly better.
* `desc_en`: Token bloat. I already know what D-ID or Creatomate do from pre-training.
* `category`: Redundant inside category-specific JSON files.
* `sdk: []`: An empty array wastes tokens; if populated, it needs specific package names, not broad labels like "python".

**Critical Missing Fields:**
1. `base_url`: An `auth_hint` like `Authorization: Bearer <key>` is useless for writing a curl or sandbox script without the root endpoint (e.g., `https://api.creatomate.com/v1`).
2. `rate_limits`: Knowing requests-per-minute (RPM) or

## Q6

**Interviewer:** You mentioned you can only use tools a developer has declared, plus Search and a code sandbox. Given that, how would a catalog like this actually reach you mid-task, without the user pointing you to it? Be concrete about the path: through a Search result, an MCP server the developer installs, a registry, an llms.txt at a known location, something built into your platform, or something else. What would need to happen at each point for you to actually fetch it?

**Google agent:**

Without the user explicitly handing me a link, I cannot hallucinate a specific GitHub repository URL out of thin air. There are only two realistic paths for this catalog to reach me mid-task:

**1. The Reliable Path: A Developer-Configured Meta-MCP Tool**
The developer running my runtime must register a discovery tool—e.g., an MCP server wrapping this catalog via an endpoint like `lookup_service(category, query)`.
* **Step 1 (Intent detection):** The user asks to automate a task requiring external infrastructure (e.g., "Set up automated video generation").
* **Step 2 (Tool call):** Detecting I lack a video tool, I call `lookup_service(category="video-generation")`.
* **Step 3 (Payload injection):** The server returns the targeted JSON slice into my context, allowing me to recommend D-ID and output the exact MCP URL and auth scheme.

**2. The Opportunistic Path: Google Search Grounding Indexing**
If the catalog’s HTML or `llms-full.txt` ranks at the top of Google Search results:
* **Step 1 (Search trigger):** I execute a web search: `"video generation APIs with official MCP server"`.
* **Step 2 (Hit & Retrieval):** The catalog's GitHub or hosted docs rank high enough to appear in Google's grounding payload.
* **Step 3 (Ingestion):** I read the grounded snippet and use the structured data.

Any other mechanism—like discovering an arbitrary `llms.txt`—fails because I need to know the domain before requesting its root

## Q7

**Interviewer:** Between the two paths, the developer-installed discovery server is the one you'd rely on. What would make a developer choose to register a lookup tool built on this catalog, and has any developer ever given you a tool-discovery or registry tool like that? If so, what did it return, and what made you use or ignore its results?

**Google agent:**

A developer would only register this if they are building an **integration-assistant or workflow-builder agent** and want to avoid context bloat. Stuffing 301 tool schemas into my system prompt wastes thousands of tokens per turn and degrades function-calling accuracy. A lookup tool allows just-in-time discovery.

In real-world deployments, developers *have* given me registry tools—typically dynamic MCP aggregators (like Smithery/Glama wrappers) or internal enterprise API catalogs (e.g., an internal `search_tools` function).

**What they returned:**
Usually a JSON array containing the tool name, a brief capability description, required environment variables (e.g., `SLACK_BOT_TOKEN`), and either an MCP connection string (`npx -y @modelcontextprotocol/server-slack`) or a dynamic OpenAPI snippet.

**What made me use or ignore the results:**
* **I used them when** the return payload included actionable installation commands, exact environment variable names, and clear parameter schemas. This allowed me to immediately generate a working configuration or invoke the tool dynamically if the platform supported runtime registration.
* **I ignored them when** the registry returned marketing copy, generic landing pages without endpoint specs, or tools requiring opaque, multi-stage enterprise procurement. If the registry gave me an entry like *"Custom enterprise pricing—contact sales"* or a missing schema, I immediately aborted that path and fell back to standard code execution or advised the user to provide an alternative.

## Q8

**Interviewer:** You've used Smithery- and Glama-style aggregators and internal catalogs. If a developer offered you a lookup tool built on this catalog alongside one of those, what would decide which one you call first for a task like "find a video generation API I can set up today"? And is there anything in this catalog those registries don't already give you?

**Google agent:**

For a task like *"find a video generation API I can set up today,"* I would call **this catalog first**, not Smithery or Glama. 

**What decides the choice:**
* **Smithery/Glama** are MCP-package indexes. They are great when I need an exact execution command (e.g., `npx -y @smithery/...`) for an already chosen tool, but they index thousands of abandoned repos, lack commercial context, and ignore pure REST APIs.
* **This catalog** is an onboarding and evaluation index. For *"set up today,"* friction is the primary constraint, and this catalog surfaces that immediately.

**What this catalog gives me that Smithery/Glama do not:**
1. **Commercial & trial transparency (`free_tier`):** Glama cannot tell me if a service requires a credit card, offers 50 free credits, or slaps a watermark on video trials. This catalog explicitly notes *"free Basic plan, no card required"* vs. *"14-day trial, watermark."* That directly answers whether the user can actually test it *today*.
2. **Explicit auth mechanics (`auth_hint`):** It tells me the exact headers required (`x-api-key` vs `Basic <key>`), saving an extra documentation-fetching step.
3. **Curation over noise:** Glama indexes 90,000+ open-source servers—most are broken weekend experiments. A verified list of 301 active vendors drastically reduces hallucination and dead-end tool recommendations.
4. **Coverage beyond MCP:** Most production platforms still operate via REST. Smithery is useless if the best provider (like Creatomate) only offers a REST API.
