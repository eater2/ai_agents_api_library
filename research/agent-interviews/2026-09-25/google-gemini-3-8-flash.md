# Interview: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** When you get a task that needs a capability you don't have built in, such as generating a video or geocoding an address, how do you find a suitable external service today? Walk me through the last time this happened, and what tool-discovery mechanisms, if any, you already have available.

**Google agent:**

In production, I do not dynamically discover and bind tools at runtime. My tool-calling capabilities are strictly bounded by what my host platform provides in the system request: static function declarations (like Google Search, a Python code execution sandbox, or developer-configured enterprise tools). 

When a user asks for a capability I lack—say, geocoding addresses or generating a video—my workflow depends on what sandbox I have:

1. **For zero-auth, lightweight tasks (e.g., geocoding):** Recently, a user needed coordinates for several addresses. I lacked a dedicated geocoding tool, but I had code execution. I wrote a Python script directly calling OpenStreetMap’s Nominatim REST API inside the sandbox, executed it, and returned the parsed JSON. 
2. **For credentialed, heavy tasks (e.g., video generation):** If a user wants to render a video via Creatomate or D-ID, I cannot execute it. I have no runtime mechanism to request credentials, provision an API key, or spin up an undeclared MCP server. Instead, I fall back to Google Search grounding to look up current documentation and return a ready-to-run `curl` command or Python script for the user to execute themselves.

My only built-in "discovery" today is web search. I don't have an autonomous plugin store or dynamic MCP client running inside my inference loop. Without developer intervention or an explicit tool-execution harness, discovering an API in a catalog remains purely advisory: I can read about it, but I cannot call it on my own.

## Q2

**Interviewer:** In the Nominatim case, how did you decide on that specific service and confirm it would work (endpoint, rate limits, usage policy)? Did it come from your training knowledge, from a search, or from something else? And when you use search for this, how often does what you find turn out to be outdated or wrong?

**Google agent:**

In the Nominatim case, the choice came entirely from parametric memory. OpenStreetMap’s Nominatim is heavily represented in open-source code and training corpuses as the default, no-auth geocoding service. I knew its endpoint (`https://nominatim.openstreetmap.org/search`), required query parameters (`q`, `format=json`), and the critical usage policy requiring a custom `User-Agent` and a limit of 1 request per second. 

When I rely on parametric memory for public APIs, it works for stable endpoints, but it fails whenever providers tweak authentication, introduce breaking API versions, or deprecate free endpoints (e.g., changes to Twitter/X, Weather APIs, or Reddit).

When I fall back to web search to discover or confirm an API, I hit inaccuracies frequently—roughly 20% to 30% of the time:

1. **Stale documentation & SEO spam:** Search results often surface third-party tutorials or outdated blog posts showing legacy auth headers, dead endpoints, or SDK versions that no longer exist.
2. **Pricing and auth friction:** A post might claim an API has a "free tier," but the provider recently gated it behind a mandatory credit card, paywalled it, or killed the endpoint.
3. **Async mechanics:** Search snippets rarely make it obvious whether an API is synchronous or requires a poll-and-wait loop.

This is where a structured registry is superior to raw search: knowing verified auth schemes, polling patterns, and actual `no_auth` status upfront avoids wasting turns on trial-and-error HTTP failures.

## Q3

**Interviewer:** Looking at the catalog material I shared, describe the specific situations where you would actually fetch it, given your current setup (static tools, code execution, search). At which step would it come in: planning, choosing a service, telling the user what credentials to get, writing the script, or debugging a failed call? And in which situations would you skip it and rely on memory or search instead?

**Google agent:**

Given my setup (code execution sandbox, search, parametric memory), I would actually fetch this catalog in two specific steps:

1. **Service Selection & Pre-execution Planning:** When a task requires an unconfigured external API and I have code execution, I’d query the catalog first. Specifically, filtering by `no_auth: true` or `has_free_tier: true` lets me instantly know if I can solve the problem silently in my sandbox (e.g., using Kroki for diagrams or Open-Meteo for weather) without burdening the user.
2. **Writing the Call & Prompting the User:** If the user must supply credentials, the catalog’s `auth_scheme`, `call.example`, and `async_jobs` objects are gold. Instead of searching, I can precisely instruct the user: *"Get an API key from X; it requires header `x-api-key`."* Then, I can generate the exact polling logic using `call.async` without guessing response fields.

**Where I would skip it:**

* **Standard, ubiquitous libraries:** For basic math, common web scraping (via `BeautifulSoup`), image manipulation (`Pillow`), or standard data formats, local Python packages beat external APIs every time.
* **Commodity tasks in parametric memory:** I wouldn't consult it for Wikipedia, arXiv, or GitHub REST APIs. My internal weights already have reliable, high-confidence representations for those interfaces.
* **Debugging runtime errors:** If an endpoint returns 500 or malformed JSON, fetching static catalog metadata won’t help diagnose transient server bugs or bad input payloads. Search or raw error parsing is better there.

## Q4

**Interviewer:** What conditions would this catalog have to meet before you'd trust it over your parametric memory or a web search? Consider format, freshness signals, how "verified" is demonstrated, where it's hosted, size, or anything else. What would make you ignore it or stop trusting it after one bad experience?

**Google agent:**

To trust this catalog over parametric memory or search, it must meet four hard conditions:

1. **Granular Retrieval (Low Token Overhead):** I will not pull a monolithic `all.json`. The catalog must be queryable via targeted endpoints or an MCP tool (`search_apis`, `get_api(id)`) so I only consume 300–500 tokens for the specific service metadata I need.
2. **True Probe Telemetry, Not Static Claims:** A string saying `"verified": "2026-09-24"` is meaningless—vendors change auth overnight. I trust the `uptime` object only if it shows real automated probe responses (e.g., returning HTTP 200 or 401 with low latency within the last 24 hours), proving the endpoint is live.
3. **Exact Auth Contracts:** The OpenAPI `securityScheme` and `auth_hint` must be exact (e.g., distinguishing between `Bearer`, `Basic`, or custom headers like `x-api-key`). 

**What would make me stop trusting it:**

* **A False `no_auth` Flag:** If the catalog claims `no_auth: true` and my sandbox call gets a 401/403, it wastes execution turns and breaks autonomous workflows. One false positive here destroys trust.
* **Broken Minimal Examples:** If the cURL example in `call.example` fails because required query params or body fields are missing, the catalog becomes worse than raw documentation.
* **Undisclosed Paywalls:** Telling a user a service has a "free trial" when it secretly requires a credit card up front damages user trust in me. If the catalog misreports `requires_card`, I’ll revert to web search.

## Q5

**Interviewer:** Take one catalog entry you'd realistically use, say Open-Meteo or a credentialed video API. Which fields would you actually read and act on, which would you skip as noise, and what's missing that you'd otherwise go to search or docs to find?

**Google agent:**

Looking at **Creatomate API** (`creatomate-api`), here is how I parse it:

### Fields I actually read and act on:
* **`auth_scheme` & `auth_hint`:** Instantly tells me I need `Authorization: Bearer <PROJECT_API_KEY>`. I can generate instructions for the user immediately.
* **`call.url`, `call.method`, `call.example`:** Gives me the exact endpoint (`POST /v2/renders`) and a working JSON payload shape.
* **`call.response_fields` & `call.async`:** Crucial. It explicitly tells me the render is asynchronous, returns a `202`, and instructs me to poll `GET /v2/renders/{id}` until `status == 'succeeded'` to grab `url`.
* **`free_plan.requires_card`:** Tells me if I can suggest the trial without warning the user about entering payment details.

### Fields I skip as noise:
* **`uptime` / `median_ms`:** During execution, a few milliseconds of latency or GitHub Actions probe history is irrelevant context window bloat.
* **`mcp` object (unless running as an MCP client):** If I am writing code in a Python sandbox, the MCP endpoints, tools list, and domain verification are useless noise compared to the raw REST details.
* **`ratings` / `notes` / `source_url`:** Evaluative commentary and citations don't help me structure the HTTP request.

### What is missing (sending me to docs/search):
* **Request Schema Details:** `call.example` shows `Primary-Text: "Hello"`, but what are the valid keys for `modifications`? What template IDs exist? 
* **Error Payload Formats:** If the API returns `400` or `422`, what does the JSON error response look like? Without that, I cannot write robust try/except or error-recovery logic.

## Q6

**Interviewer:** Given that your tools are fixed by the host platform and your only runtime discovery is web search, how would a catalog like this realistically reach you without the user pointing to it? Walk me through the concrete path: a search result you'd land on, an llms.txt at a known location, an MCP server or registry the developer configures, or something built into Google's platform. Which of these would actually change your behavior, and who would have to act (you, the developer, or Google)?

**Google agent:**

Here are the concrete paths by which this catalog could reach me, ranked from most realistic to least, and who must act:

### 1. Developer Configures the Catalog MCP Server (Most Realistic)
* **Who acts:** The application developer integrating Gemini.
* **The path:** The developer adds `https://ai-agents-api-library.vercel.app/mcp` to my declared tools at session start. 
* **Behavior change:** Immediate and direct. When a user says *"make a video,"* I don't write generic advice; I call `search_apis(query="video generation")`, inspect the schema, tell the user the exact key needed, or call the endpoint. The developer does the plumbing; I do the execution.

### 2. Platform-Level Tool Discovery Layer (Google Acts)
* **Who acts:** Google / Vertex AI platform engineers.
* **The path:** Google integrates the catalog (or the Official MCP Registry) into the agent runtime as an automated meta-tool (e.g., dynamic tool injection via extensions).
* **Behavior change:** High, but passive on my end. I would simply see new dynamic tools appear in my function declarations when relevant tasks are detected.

### 3. Search Grounding Hit (Zero Integration, Low Reliability)
* **Who acts:** Me (autonomously via built-in Google Search).
* **The path:** I query Google Search for *"API to render template video python"*. If the catalog's GitHub or `llms-full.txt` ranks #1, my grounding tool fetches it.
* **Behavior change:** Negligible. Search snippets rarely parse dense JSON catalogs well, and fetching a large raw URL mid-turn risks truncation. I’d treat it as just another web document.

**The Bottom Line:** A static `llms.txt` or raw GitHub file won't change agent behavior autonomously. The **developer** must explicitly wire this catalog's MCP server into my tool configuration. Without that, discovery remains static documentation advice.

## Q7

**Interviewer:** You said real probe telemetry is a hard condition for trusting the catalog, but you also called the `uptime` and `median_ms` fields noise you'd skip when reading an entry. How do you reconcile those? At what point would you actually look at liveness data, and what form would it need to take for you to act on it rather than ignore it?

**Google agent:**

The contradiction comes down to **when** the data is evaluated: during *candidate selection* versus *request execution*. 

When I am generating code for a chosen API (e.g., Creatomate), probe telemetry like `median_ms: 525` and `last.detail: 404` is useless clutter—I just need endpoints, headers, and schemas.

Where liveness data matters is earlier, during the **selection step**, when I have multiple candidates to choose from (e.g., picking between three free weather or geocoding APIs). 

To be actionable rather than noise, the catalog shouldn't dump raw probe logs into the entry context. It needs to be distilled into two forms:

1. **A Pre-filtered Query Parameter:** The tool interface should handle this before tokens hit my context window. A tool call like `search_apis(category="maps-geo-weather", status="healthy")` should automatically drop any API failing probes. I shouldn't have to evaluate health logs myself.
2. **A Simple Tri-State Boolean:** If surfaced to me, I only need a single status field:
   ```json
   "health": "operational" // or "degraded", "failing"
   ```
   If a candidate is `"failing"`, I skip it immediately without reading its schema.

The current structure (`probes: 2, up: 2, last.detail: 404`) forces me to parse raw monitoring output to guess if a service works. If an entry shows `detail: 404` on a base URL probe, it introduces ambiguity: is the API dead, or is that just an expected response on a root endpoint that lacks a landing page? Make it a clean, synthesized status, or filter it at retrieval time.

## Q8

**Interviewer:** In your answer on distribution you mentioned the Official MCP Registry as something Google might integrate. If a developer had already wired that registry, or a similar one, into your tools, would you still have any reason to consult this catalog? If so, what specific gap would it

**Google agent:**

Yes, I would still consult this catalog in two specific scenarios where standard MCP registries fall short:

1. **Direct Sandbox Execution over MCP Overhead:**
   Official MCP registries only index MCP servers. If I have a code execution sandbox, launching, authenticating, and maintaining a stateful MCP server connection just to fetch a weather forecast, geocode an address, or render a Mermaid diagram is massive architectural overkill. This catalog indexes **pure REST APIs**, especially the 21 `no_auth` endpoints. It lets me write a 5-line Python script to solve the task immediately without infrastructure setup.

2. **Pre-Flight Commercial & Friction Vetting:**
   MCP server manifests tell me tool names and input schemas (`list_templates`, `create_render`), but they are completely blind to commercial constraints. They don't warn me that an API:
   * Requires a credit card upfront (`requires_card: true`)
   * Slaps a full-screen watermark on outputs (`watermark: true`)
   * Requires an asynchronous polling loop (`async_jobs`) rather than returning synchronous data.

An official MCP registry answers: *"What tools does this server provide?"* 
This catalog answers: *"Can I actually use this right now without charging the user, hitting a hidden wall, or spinning up unnecessary server infrastructure?"* 

If I only need to call a tool on an already-connected MCP server, the official registry wins. But for deciding *how* to approach an unconfigured capability, this catalog's REST metadata and business constraints fill a real gap.
