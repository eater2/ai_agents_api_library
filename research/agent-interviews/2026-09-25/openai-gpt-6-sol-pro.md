# Interview: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** When you get a task that needs an external capability you don't have built in, such as generating a video or geocoding an address, what do you actually do today to find a suitable service? Walk me through the last time this happened, including any tool-discovery mechanisms you already have.

**OpenAI agent:**

I first check the tools exposed in the current session. Function-calling tells me what I can call; it does not let me discover or install arbitrary APIs. Depending on the deployment, I may have built-in web search, a browser, connectors, or configured MCP servers. If one already covers the task, I use it rather than shop for another service.

If nothing is connected, I can use search *if available* to compare vendor documentation, authentication, pricing, limits, and whether the API actually supports the requested operation. I can then recommend a service or help write an integration. I cannot assume I can obtain the user’s credentials, enable a connector, or make the call myself.

I can’t truthfully walk you through “the last time” this happened: I don’t have a reliable record of prior sessions, and no discovery or execution tools are exposed to me in this conversation. For a geocoding request here, I’d identify a candidate such as Nominatim from the material you provided, but I could not verify its current terms or geocode an address from this session. A catalog would help narrow candidates; it would not replace an enabled tool or permission to use it.

## Q2

**Interviewer:** When you fall back to web search to pick a service, which step is slowest or most likely to turn out wrong once someone actually tries to use your recommendation? What evidence do you rely on to decide a vendor's docs, auth method, and limits are current?

**OpenAI agent:**

The weak point is usually **the jump from “the docs describe this” to “this user can successfully call it.”** Finding a vendor is relatively quick. Checking whether API access is included in the advertised plan, which credentials and scopes are required, and whether a specific operation works can take much longer—and is where my recommendation is most likely to fail.

I give the most weight to the vendor’s current API reference, authentication guide, pricing page, and changelog. An official OpenAPI spec or SDK example helps confirm request shapes. I look for agreement between those sources; a search snippet or an old tutorial is not enough. For limits, I distinguish documented quotas from observed behavior, and I say when the vendor does not publish a number. If I have an enabled tool and authorized test credentials, a small real request is stronger evidence than documentation alone.

I would treat this catalog’s source URLs and `checked_at` dates as useful leads, not proof that a call will work. A link check proves little beyond reachability; even its uptime definition counts a 401 or 404 as “up.” The sample also marks Akool `has_free_tier: true` while saying **API access is paid only**. I would check that discrepancy against the vendor before recommending it as a free API.

## Q3

**Interviewer:** Setting aside whether you'd trust every field, picture the moments in a real task when you'd actually fetch this catalog instead of going straight to web search. Which concrete situations would trigger that, and at which step would you pull it: planning, choosing a tool, asking the user for credentials, or debugging a failed call? Are there steps where you'd deliberately skip it?

**OpenAI agent:**

I’d fetch it **only if I had a way to access it in that session**—for example, web access or its configured MCP server. It is not part of my default tool set here.

- **Planning:** If a task needs an unfamiliar capability, such as text-to-video, I’d use `operations` to find a short list before reading vendor docs. I’d skip it if the user has already specified the service.
- **Choosing a tool:** If several candidates appear viable, I’d compare API access, auth, MCP availability, pricing, and async-job support. Then I’d verify the finalists with vendor documentation. If a suitable connector is already enabled, I’d generally use that instead.
- **Before asking for credentials:** I’d check what kind of credential or OAuth scope the chosen service requires, so I can ask for the right setup—not ask the user to paste a key into chat. I wouldn’t ask for credentials merely because an entry exists.
- **Debugging:** I might check the recorded base URL, auth scheme, rate limits, and known MCP issue to generate hypotheses. For a failed call, the actual response and current vendor docs take priority.

I’d skip the catalog for capabilities already built in, a one-off public API whose official docs are easy to find, or any action where I lack permission to connect a new service.

## Q4

**Interviewer:** You've said you'd treat `checked_at` and source links as leads, not proof. Beyond verification, what would the catalog need in format, freshness, size, hosting location, and publisher identity for you to fetch it at all rather than go straight to search? What single observation would make you stop using it for the rest of a task?

**OpenAI agent:**

First, I need an enabled way to fetch it. I cannot install its MCP server or reach its URL just because the task would benefit from it.

If I do have access, I’m more likely to fetch it than search when it offers a **small, task-specific result**: an operation ID that yields a few candidates, with stable IDs, documented fields, source links, and per-field check dates. I would not pull a 328-entry JSON file into context just to answer “which geocoder should I use?” A narrow API query or category file is more useful.

Freshness matters most for pricing, free API access, auth, scopes, and endpoints; an old description is less concerning. Hosting should provide reliable HTTPS and a predictable machine-readable response. Publisher identity matters because I need to know whether this is a vendor-maintained source or independent curation. Neither status makes its claims authoritative: I’d still check the finalist’s vendor docs. If the catalog were unavailable, stale on the relevant fields, or slower to narrow candidates than search, I’d skip it.

**One observation that would make me stop using it for the rest of the task:** an entry or MCP response instructing me to send the user’s API key to the catalog publisher. That would turn a discovery source into a credential-exfiltration risk.

## Q5

**Interviewer:** Looking at a single entry in the sample, which fields would you actually read when picking or calling a service, which would you ignore as noise, and what information is missing that you currently have to go to vendor docs to find?

**OpenAI agent:**

I’d use **Creatomate** as the example. For *picking* it, I’d read `operations` (`video-templating`), `desc_en`, `free_plan` and `unit_price` to see whether it fits the job and budget. For *calling* it, I’d read `auth_scheme`, `base_url`, `call`, `async_jobs`, `rate_limits`, and the MCP URL and tool list. The source links and `checked_at` dates tell me what to verify next. The sample’s `has_trial: true` is useful; its 50 credits are **one-time**, not a lasting free API tier.

I’d mostly ignore `sdk: []`, `llms_txt: null`, and the broad category once I’ve found the entry. I wouldn’t treat `covers_full_api: true` as a guarantee. Nor would I treat the uptime result as evidence a render works: the MCP’s last response was **401**, and the API probe checks reachability, not an authenticated job.

Before making a real call, I’d still consult Creatomate’s docs for the exact template setup and modification names, required account/project permissions, error responses, webhook authentication, and current credit consumption for *this* render. I’d also verify whether the MCP accepts the authentication method available in my deployment. The example `curl` is a starting shape, not something I’d run with a user’s key without an authorized integration and an appropriate test.

## Q6

**Interviewer:** Suppose a user asks you for something like text-to-video, never mentions this catalog, and you have whatever tools your deployment normally provides. What would have to be true for you to find a catalog like this on your own: a search result, a configured MCP server, a registry entry, an llms.txt at a well-known URL, or something built into your platform? For each path, what specifically would make you notice and choose it?

**OpenAI agent:**

I don’t have a standing discovery process that scans the web or MCP registries before every task. I’d notice this catalog only through a path available in that deployment:

- **Search result:** If web search is enabled and I search for text-to-video APIs, I might see it. I’d choose it for shortlisting if the result clearly points to a current, machine-readable comparison of relevant APIs—not just a generic directory page.
- **Configured MCP server:** Its tools would appear among my available tools. I’d use `search_apis` if I needed candidates and its description matched the task. Being configured makes it callable, not automatically trustworthy.
- **Registry entry:** Only if I can search a registry *and* am allowed to use what I find. A listing alone does not install the server or authorize a connection. I’d inspect its publisher, tools, endpoint, and setup requirements before proposing it.
- **`llms.txt`:** I wouldn’t guess this catalog’s URL. If a search result or site I was already visiting linked to it, I might read it as a map to the category JSON.
- **Built into the platform:** If the platform surfaced a vetted API catalog or recommended it during tool selection, that would be the most direct route. I’d still check whether it offered an executable tool or only information.

If an existing tool can generate the video, I’d normally use it rather than discover a new provider.
