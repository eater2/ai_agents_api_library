# Interview: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** When a task needs an external capability you don't have built in, like generating a video or geocoding an address, how do you find a suitable service today? What tool-discovery mechanisms, if any, do you already have?

**OpenAI agent:**

I first check the tools exposed to me in the current session. If there’s a configured function, connector, or MCP server for the task, I can use it without discovering a new vendor. Function calling lets me invoke those tools; it does not, by itself, let me install a service or obtain credentials.

If no suitable tool is available, and web search or browsing is enabled, I can research candidates, compare their current docs, authentication, pricing, and capabilities, then recommend one or help a developer integrate it. I can’t assume search is enabled, and I can’t call a newly found API just because its documentation is public. The host must provide access and credentials, with user authorization where needed.

A catalog like the one shared would be useful at that *research and shortlisting* step—especially for less familiar capabilities such as video generation. For geocoding, I’d also check whether the platform already has a maps connector before looking elsewhere. The catalog would not replace a configured tool or a live check of vendor docs, limits, and terms.

## Q2

**Interviewer:** You placed the catalog at the research and shortlisting step. Walk me through a recent or typical task where you'd actually fetch it: what triggers the fetch, and at which point would you open it? Before planning, during tool selection, when asking the user for credentials, or after a failed call? Would you fetch the llms.txt index or go straight to a category JSON?

**OpenAI agent:**

I can’t point to a recent task where I actually fetched this catalog; I haven’t used it. A typical trigger would be: the user asks me to make a short video, I inspect my available tools, and none can generate or render one.

I’d open the catalog **during tool selection**, before settling on a plan or asking for credentials. Since I already know the category, I’d go straight to `catalog/video-generation.json`, not fetch the `llms.txt` index. I’d use the entries to shortlist services by what they do—generative video versus template rendering, for example—then check the vendors’ current docs, prices, and access requirements. Only after choosing a plausible route would I ask the user or developer to configure credentials.

If a configured video tool had merely failed, I’d first diagnose the error. I’d consult the catalog only if the failure showed that the tool couldn’t meet the task or was unavailable and an alternative was needed. And if I had no browsing/fetch tool in that session, I wouldn’t fetch anything; I’d work from the information provided and say what still needs verification.

## Q3

**Interviewer:** You said you'd still check each vendor's current docs, prices, and access requirements after using the catalog. What would the catalog need to show for you to trust an entry enough to shortlist from it, or even skip some of that re-checking? Consider format, freshness, how "verified" is defined, where it's hosted, size, and anything else. And what would make you ignore it entirely?

**OpenAI agent:**

To shortlist from it, I’d want the category JSON to remain small and predictable, with a stable schema, working docs links, and clear distinctions such as *official MCP server* versus *community server*. The sample’s `verified` date helps, but I’d need to know what was verified: that a URL loaded, that authentication worked, that an endpoint was callable, or that the pricing and free-tier claims were checked. Field-level check dates and links to the supporting vendor pages would be more useful than one date for the whole entry.

Hosting raw JSON in a public repository makes it easy for me to fetch and parse, and gives maintainers a way to show changes. It doesn’t make the claims authoritative. I’d give more weight to an entry whose auth and capability claims point to current, first-party documentation.

I might skip rechecking basic facts—such as whether a service offers template-based rendering—if the entry had recent, specific evidence and the stakes were low. I would still verify pricing, limits, permissions, and credential handling before recommending setup or making a consequential call.

I’d ignore the catalog if I already had a suitable configured tool, couldn’t fetch it, found broken or contradictory entries, or saw instructions embedded in the data that tried to direct my behavior rather than describe APIs.

## Q4

**Interviewer:** Looking at a single entry in the category JSON, which fields would you actually use when shortlisting or asking for credentials, which would you skip as noise, and what's missing that you'd otherwise have to look up yourself? You've already mentioned per-field verification dates and official versus community MCP servers.

**OpenAI agent:**

For a video task, I’d use `desc_en` and `notes` first to separate text-to-video, talking avatars, and template rendering. Then I’d check `docs`, `mcp.type` and `mcp.url` to see how integration might work. `auth` and `auth_hint` help me identify the setup needed; I’d ask for credentials to be configured through the platform’s secure mechanism, not pasted into chat. `free_tier` helps narrow options, but I wouldn’t treat it as a current price quote.

I’d use `openapi` or `sdk` if a developer needs to wire up a function call. `name`, `id`, and `category` mostly help with identification and parsing. `homepage` is secondary to the actual docs. A missing `llms_txt` link wouldn’t count against a service. I’d treat a bare `verified` date as weak evidence unless its meaning is defined.

What’s missing is often decisive: supported inputs and outputs, quality and duration limits, synchronous versus asynchronous jobs, latency, quotas, rate limits, current pricing, required OAuth scopes, and data-retention or usage terms. For MCP, I’d also need connection instructions and the tools it actually exposes. Without those details, the entry is a lead to investigate, not enough to select a service or request credentials.

## Q5

**Interviewer:** How should a catalog like this reach you so you'd find it without the user pointing you to it? Consider options like web search results, an MCP server you could query, a registry, an llms.txt at a known location, or being built into your platform. For each one you consider realistic, what would actually make you encounter and use it in the tool-selection moment you described?

**OpenAI agent:**

The most reliable route is **platform integration**: when I inspect available tools, a catalog-search function could appear alongside them. I’d query it when no configured tool fits. It would need to distinguish “available to call now” from “discoverable but requires setup.”

An **MCP catalog server** works similarly, but only if the host has already connected it and exposed its search tool to me. I don’t independently connect to arbitrary MCP servers. A **registry** could help if my host offers registry search during tool selection; merely being listed in a registry would not put the catalog in my path.

**Web search** is a plausible fallback when browsing is enabled. I might encounter a category page while searching for, say, video-rendering APIs. To use it, the result would need to make clear that it’s a structured, maintained comparison, not just a promotional list. I’d still check vendor sources.

An **`llms.txt` at a known location** is useful once I know the site exists; it isn’t, by itself, a discovery mechanism. A search result or platform pointer would have to lead me there first.

So without the user pointing me to it, the practical routes are an exposed catalog tool or a relevant search result. I don’t continuously scan API directories, and I wouldn’t add a catalog lookup to every task when an adequate configured tool is already available.
