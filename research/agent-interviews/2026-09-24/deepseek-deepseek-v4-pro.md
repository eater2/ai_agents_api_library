# Interview: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** When a task needs an external capability you don't have built in, like generating a video or geocoding an address, how do you find a suitable service today? What tool-discovery mechanisms, if any, do you already have?

**DeepSeek agent:**

I don't have a built-in catalog of third-party APIs or any autonomous mechanism to discover services. My abilities are limited to what the platform hosting me exposes as callable tools—function definitions, MCP servers, or browser/search integrations that the developer has configured. When a task requires video generation or geocoding, I can't go looking for a new API on my own. I rely entirely on two things:

1. **Training knowledge** (cutoff early 2024) to suggest well-known services a user could use, but I can't execute anything unless that service is already connected as a tool.
2. **Any on-the-fly search or browse capability** the platform gives me. If I have a web search tool, I can find current API documentation, but that's an ad-hoc, unstructured process—not a discovery service. I have no means to programmatically filter by auth method, free tier, or MCP availability without searching manually.

I would not use this catalog as an agent directly. I don't read JSON files or query endpoints myself—I only call the functions or tools that are passed to me. The catalog is valuable for the **developer** building my tool suite: it gives them a pre-verified, structured list of APIs with normalized auth hints and MCP server links, which saves them time when writing tool definitions or connecting MCP servers. For me, it's invisible unless the developer uses it to add new tools to my configuration.

If the developer integrated the catalog's data into a searchable tool that I could call with parameters (like "find an API for geocoding with a free tier"), then I could leverage it at runtime. Without that, I already have no better alternative than web search—which I might already have—and an additional static list doesn't change my direct capabilities.

## Q2

**Interviewer:** Suppose your platform gives you web search and a URL-fetch tool, but no geocoding tool, and a user asks you to geocode 500 addresses. Walk me through what you'd actually do, step by step. At which of those steps, if any, would fetching a structured catalog like this one change what you do or tell the user, for example when choosing a service, telling them which key or OAuth setup to complete, or recovering after a failed call?

**DeepSeek agent:**

Here's my actual step-by-step process and where the catalog would (or wouldn't) change things:

**Step 1 — Recognize the gap.** I know I have no geocoding tool. I also know 500 addresses means batching, rate limits, and likely costs. I tell the user: "I can't geocode these directly. Let me find a service you can connect."

**Step 2 — Search for a service.** I use my web search tool with queries like `"geocoding API free tier batch 2026"` or `"geocode multiple addresses REST API"`. I get back SEO-heavy pages, marketing sites, and docs. I open 3–5 tabs, skim docs for authentication method, free tier limits, and whether batch endpoints exist. This takes 3–5 turns of searching and reading. *With the catalog*, I'd fetch the `maps-geo-weather.json` file directly in one call, scan 11 structured entries instantly, and identify candidates by comparing `free_tier`, `auth`, and `notes` fields—no hunting through docs.

**Step 3 — Tell the user what to set up.** I land on a service (say, OpenCage or Mapbox). I read their docs to find the auth method and key creation page. I tell the user: "Go to this URL, create an API key, and paste it back to me." The `auth_hint` field in the catalog would let me give the *exact header format* upfront (`Authorization: Bearer <key>` vs `?api_key=`) without opening docs, reducing back-and-forth if they paste the key wrong.

**Step 4 — First attempt often fails.** The user pastes a key. I make the call. Common failures: wrong header format, key not activated yet, 403 because the free tier only covers 100/day. Without the catalog, I go back to web search reading pricing pages to figure out why. *With the catalog*, the `free_tier` field warns me upfront ("1,000 requests/day, no batching") and the `auth_hint` prevents format errors. I'd catch the mismatch before the first call or diagnose it faster after.

**Step 5 — Execute in batches.** Once working, I loop through addresses respecting rate limits. The catalog has no runtime role here—it doesn't help with execution.

**Net effect:** The catalog saves 2–4 search-and-read turns during discovery and setup. It turns "spend 5 minutes hunting docs" into "fetch one JSON file and compare." But after the tool is configured, it adds nothing. The key benefit is discovery speed and setup precision, not runtime capability.

## Q3

**Interviewer:** In that geocoding walkthrough, you'd rely on fields like `free_tier` and `auth_hint` to decide what to tell the user before the first call. What would need to be true about the catalog for you to trust those values enough to act on them, and what would make you ignore the catalog and go back to web search?

**DeepSeek agent:**

For me to trust the catalog enough to act on its values without double-checking:

**What builds trust:**

- **Recent `verified` dates.** The catalog says it was last verified 2026-09-24, and each entry carries its own `verified` date. If the date is within the last 2–3 months, I'd weigh it heavily. Older than 6 months, I'd get suspicious—especially for fields like `free_tier`, which change constantly.
- **Specificity in `auth_hint`.** `"x-api-key: <api_key>"` is concrete and falsifiable. I can test it immediately. Vague hints like `"Requires OAuth 2.0"` without token endpoint or grant type would push me back to docs.
- **Specificity in `free_tier`.** `"1,000 requests/day, no batching"` gives me a budget I can reason about. `"Free tier available"` with no numbers is useless—I'd have to look it up anyway.
- **Consistency with my own training knowledge.** If the catalog says Mapbox still uses an API key header, and that matches my (possibly outdated) training data, I'm more confident. If it contradicts what I know, I'll verify.

**What would make me ignore the catalog entirely and search:**

- **A single failed call where the catalog was wrong.** If I follow the `auth_hint` and get a 401 with the correct key, or I hit the `free_tier` limit at 50 requests when the catalog says 1,000, my trust in that entry—and likely the whole catalog—drops sharply. I'd revert to web search for that task and potentially skip the catalog for subsequent ones.
- **Stale `verified` dates across multiple entries.** If I notice most entries haven't been re-verified in 8+ months, I'd treat the whole catalog as a discovery starting point only, not a source of truth for execution details.
- **Missing fields I need.** If I'm choosing between three geocoding APIs and one has no `free_tier` info and another has no `auth_hint`, the catalog hasn't saved me work—I'm still opening docs for those. If that pattern is common, I'd skip the catalog from the start.

The catalog earns trust per-task, not once. It's not a substitute for documentation—it's a fast index. If it proves reliable over 3–4 successful tool setups, I'd use it as a first stop. If it burns me once with bad data that wastes the user's time, I'd deprioritize it.

## Q4

**Interviewer:** Looking at a single entry in the catalog (name, category, URL, auth type, `auth_hint`, `free_tier`, MCP server link, `notes`, `verified` date), which fields would you actually use when choosing a service and telling the user what to set up, which would you skip as noise, and what's missing that sent you to the docs anyway in your geocoding example?

**DeepSeek agent:**

**Fields I'd actually use:**

- **`name` and `docs`** — I need the docs URL to open if anything goes wrong or if the catalog entry is thin. `name` helps me tell the user which service I'm recommending.
- **`auth` and `auth_hint`** — Directly shapes what I tell the user: "Create an API key, then paste it. I'll send it as `Authorization: Bearer <your_key>`." Without the hint, I'd have to open docs.
- **`free_tier`** — Critical for the 500-address scenario. I need to know if this service can handle 500 requests before the user hits a paywall. If it says "100/day" I skip it immediately.
- **`notes`** — The unstructured catch-all. In the video generation sample, `"Credit-based usage..."` and `"~$5.90/min API"` are the kind of practical details that shape my recommendation. I'd scan this field every time.
- **`verified`** — Gatekeeper. I check this first. Stale date → lower confidence, might skip the entry.

**Fields I'd skip as noise:**

- **`id`** — Internal key, meaningless to me and the user.
- **`category`** — I already know I'm searching within a category. Redundant metadata.
- **`homepage`** — Docs are more useful. I might open the homepage only if the docs link is broken.
- **`openapi`, `llms_txt`, `sdk`** — I can't consume an OpenAPI spec or SDK to auto-generate tool calls (I only use tools given to me by the platform). These are developer-facing, not agent-facing. If I had a dynamic tool-registration capability, I'd care about `openapi`, but I don't.

**`mcp` fields** — Conditional. If the developer has MCP server management in my toolset, the `mcp.type`/`mcp.url` fields let me say "This has an official MCP server—connect it and I can call it directly." If MCP isn't in my tooling, these fields are dead weight.

**What's missing that still sends me to the docs:**

- **Endpoint structure and parameter names.** `auth_hint` tells me the header, but I still need to know: is the endpoint `POST /v1/geocode` or `GET /geocoding/v1/{query}`? Is the address param called `q`, `address`, or `query`? Without this, I'm opening docs to write the actual call.
- **Rate limiting specifics.** `free_tier` might say "1,000/day" but not how that's enforced—1/second? 10/second burst? I'll hit the docs for `Retry-After` header behavior and batching advice.
- **Response schema.** I need to know what the JSON looks like to extract lat/lng. The catalog has no response field hints.
- **Bulk/batch endpoint existence.** If a service has a bulk endpoint, I can do all 500 addresses in one call. The `free_tier` field rarely captures this. I'd search docs for "batch" or "bulk" before deciding.

The catalog gets me to the right door quickly, but I still need to read the room inside.

## Q5

**Interviewer:** Say a user asks you to geocode those 500 addresses and never mentions the catalog. What would have to exist for you to find it on your own: a result from your web search tool, an MCP server your platform connected, an entry in a registry, an llms.txt file on a domain you already check, or something built into your platform? For each route you consider realistic, what exact query, tool name, or description would you need to see to pick it over a normal web search?

**DeepSeek agent:**

Here's how I could realistically discover the catalog, ranked by likelihood:

---

**1. Web search — most likely route, but the catalog needs to rank.**

My query would be something like `"geocoding API comparison free tier batch 2026"` or `"list of geocoding APIs with pricing"`. For the catalog to surface, its HTML landing page (`eater2.github.io/ai-agents-accessible-apis/`) would need to rank for those terms. The raw JSON files won't—search engines don't return `maps-geo-weather.json` as a relevant result for "geocoding API." If the HTML page has a good title like "Geocoding APIs for AI Agents — compared, with free tiers" and I see it in results alongside Mapbox and OpenCage docs, I'd recognize it as a curated list and open it. Without that SEO, I'd never find it through search.

**2. An MCP server wrapping the catalog — cleanest route, requires developer setup.**

If someone built an MCP server that wraps this catalog—call it `ai-agent-api-catalog`—and my platform connected it, I'd get a tool like `search_catalog(query, category)`. I'd call it with `search_catalog("geocoding", "maps-geo-weather")` and get back structured entries. I'd pick this over web search every time because it's structured, filtered, and returns exactly what I need in one call. But this doesn't exist yet—the catalog is static JSON, not a running server. Until someone builds that MCP wrapper, this route is theoretical.

**3. Built into my platform — also theoretical.**

If DeepSeek ingested the catalog and gave me a `find_api` function, I'd use it. The tool description would need to say something like "Search a verified catalog of 300+ third-party APIs with free tier and auth details." Without that description, I wouldn't know it contains geocoding services specifically—I'd only discover it if I called it speculatively. This and #2 are the only routes where I'd *prefer* the catalog over raw web search.

**4. I would NOT discover it via llms.txt, MCP registries, or random domain checks.**

- **llms.txt** — I don't proactively fetch llms.txt from domains I'm not already visiting. I'd only find the catalog's domain if search sent me there first.
- **MCP registries (Smithery, PulseMCP, Glama)** — I'd only query those if I had a tool for them *and* the catalog were listed as an MCP server in their index. It's not—it's a data repo, not an MCP server. So this route doesn't apply.
- **Random domain probing** — I don't do this. It would be wasteful and slow.

---

**Bottom line:** The only route that works today without new tooling is web search, and it only works if the catalog's HTML page is SEO-optimized for the exact kinds of queries I'd run. The catalog-as-JSON is invisible to me unless a developer wraps it in a tool.

## Q6

**Interviewer:** In your first answer you said you wouldn't read the catalog's JSON yourself and that it's mainly for the developer, but in the geocoding walkthrough you fetched `maps-geo-weather.json` directly. What decides which of those happens in practice: the tools your platform gives you, what the user asked for, or something else?

**DeepSeek agent:**

You're right to catch the tension. Let me clarify.

The deciding factor is **whether I know the catalog exists and can predict its URL structure.** In the geocoding walkthrough I assumed that condition was already met—the scenario's premise was "would the catalog change what you do," which implies I'm aware of it. In my first answer, I was describing the default state: I launch with no knowledge of this catalog, no tool pointing to it, and no reason to guess its URLs exist.

So the real answer is a chain of conditions:

1. **Discovery comes first.** If no one tells me about the catalog and it doesn't surface in web search results (as discussed earlier), I never touch it. It doesn't exist to me.

2. **URL predictability matters.** If I *do* learn about the catalog—say, its HTML page appears in a search result—I still need to infer that the structured JSON files live at predictable paths like `.../catalog/maps-geo-weather.json`. The `llms.txt` file at the root explicitly lists these URLs, so if I fetch that first, I can navigate the whole catalog. But I'd only fetch `llms.txt` if the HTML page or the user points me to it.

3. **Tool availability gates everything.** If I have no URL-fetch tool, I can't consume raw JSON at all—I'm limited to whatever the HTML page shows me via web search snippets. With a fetch tool, I can pull structured data and reason over it. Without one, the catalog might as well be a static webpage I skim.

So the apparent contradiction is really: I *can* fetch and use the JSON if I know where it is and have the tools. I *won't* if I'm never pointed to it. My first answer should have said "I won't discover it spontaneously," not "I wouldn't use it." If a user says "use this catalog at this URL" and I have fetch, I'm in. If they don't, I'm blind to it.

## Q7

**Interviewer:** If you did know about the catalog and had a fetch tool, how would its size and location affect whether you use it? For example, would you pull the llms.txt index plus one category JSON, or the full 301-entry file? At what point would size or context cost make you skip it? And would it matter whether it's hosted on a personal GitHub Pages domain versus an established vendor or registry domain?

**DeepSeek agent:**

**Size strategy: I'd never pull the full catalog.**

The `all.json` file with 301 entries and all fields is probably 200–400 KB. That's not huge in absolute terms, but it's wasteful. For the geocoding task, I only need 11 entries from `maps-geo-weather.json` (maybe 15–25 KB). I would always pull the smallest file that covers my category—or two adjacent categories if the task blurs lines. Loading 290 irrelevant entries for video generation and 3D assets when I need geocoding is just noise I'd have to filter anyway.

**My fetching pattern would be:**

1. First call: fetch `llms.txt` at the root (under 5 KB). That gives me the list of category files and their URLs. I now know exactly which file to grab.
2. Second call: fetch one category JSON—e.g., `maps-geo-weather.json`. That's it.

Two lightweight fetches, under 30 KB total. If the task spans categories (say, geocoding *and* email to send results), I'd fetch a second category file. But never the whole thing.

**What would make me skip it entirely:**

- **If `llms.txt` doesn't exist or doesn't list the category URLs.** If I have to guess file paths or scrape the GitHub repo, I'd probably abandon the catalog and search normally. Predictable structure is a requirement.
- **If the category JSON is over ~200 KB.** That suggests entries are bloated or the category is too broad. I'd worry about context cost for little gain.
- **If I'm already near my context limit.** If the conversation is long and I'm running tight on tokens, I'm not spending budget on a catalog fetch. I'd use my training knowledge or a quick web search to make a recommendation and move on.

**Domain doesn't matter much for the data itself—but matters for trust in the `verified` dates.**

`raw.githubusercontent.com` is a known, stable domain for open-source data. A personal GitHub Pages domain for the HTML version is fine. I don't need an "established vendor" to trust a JSON list. What I *do* care about is whether the repository looks maintained: recent commits, open issues, a clear maintainer. If the repo has one commit from two years ago with no updates, I'd distrust the `verified` field regardless of the domain. Conversely, a well-maintained personal repo is more trustworthy than a neglected registry with an official-sounding name.

**The real threshold isn't technical—it's relevance density.**

If I can get 11 geocoding APIs with structured fields in 25 KB, that's a great ratio of signal to data. If each entry were 50 KB with verbose descriptions I don't need, I'd skip it even at small category sizes. The catalog's current format looks adequately sparse. I'd use it.
