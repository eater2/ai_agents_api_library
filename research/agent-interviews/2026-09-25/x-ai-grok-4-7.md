# Interview: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** When a task needs an external capability you don't have built in, like generating a video or geocoding an address, how do you find a suitable service today? Walk me through the last time this happened, and tell me what, if anything, you already have for tool discovery.

**xAI agent:**

I don't retain a cross-session log, so I can't cite a dated incident. The pattern is the same every time.

If the host already bound a function or MCP server, I use that. Discovery is the schema in the prompt: name, parameters, description. I don't shop for another geocoder when one is already attached.

If it isn't, I use built-in web search and page fetch, plus what I already know. For an address I'd look up current Nominatim or a maps provider's docs, confirm the URL, auth, and rate limits, then call it only if I have an HTTP tool and a key the user supplied. Otherwise I hand them the request. For video I have no native generator. I search vendor docs rather than invent a curl from memory, and I stop at "you need a key and a runtime that can POST and poll." I won't sign the user up for a paid API.

What I already have is search, function-calling when a developer registers tools, and MCP or connectors the user already connected. I don't browse a plugin store at runtime, and I don't query Smithery or the official MCP registry unless the task is specifically "find an MCP server." Connecting still needs user OAuth or a key and a host that allows a new server. A static catalog is just another search hit for auth hints and free-tier facts. It does not replace vendor docs or a bound tool.

## Q2

**Interviewer:** Looking at the catalog material I shared, in which concrete situations would you actually fetch it, and at which step of your work: planning, choosing a tool, asking the user for credentials, or debugging a failed call? If there's a step where you'd never touch it, say so.

**xAI agent:**

I would fetch it only when a task needs a capability that is not already bound, I do not already know a fit, and you want me to pick or compare services rather than call one you named.

That is planning and choosing, not execution. I would query `operations.json` or `search_apis` for an id such as street-geocoding or avatar-video, then filter on `has_free_tier`, `no_auth`, and `mcp.kind`. I would not load `all.json` by default.

For a credential ask, I would use it only after a candidate is chosen, and only for the header name and whether a card is required. I would re-check the vendor docs URL in that entry before telling you what to paste. The sample already disagrees with itself: Akool has `has_free_tier` true while the free-tier text says the API is paid. I will not trust the booleans alone.

I would not fetch it to debug a failed call. The error body, status, and official docs beat a catalog. The uptime field is not usable: the sample's "30-day" window has two probes and counts 404 and 401 as up.

I would never touch it when a tool or MCP server is already in the session, when making the live call, or to connect OAuth into your mail, bank, or store. I also would not run their `npx` MCP unless you explicitly add that server. Discovery still ends at vendor docs and your approval to attach a key.

## Q3

**Interviewer:** You flagged two data problems: Akool's free-tier fields contradict each other, and the uptime probe counts 404 and 401 as "up." Setting those specific bugs aside, what has to be true of a catalog like this for you to trust it enough to use in planning? Think about format, how fresh it is, how entries are verified and by whom, where it's hosted, and how large it is. And what would make you drop it for good, rather than just double-checking an entry?

**xAI agent:**

I would trust it for planning only if every claim I might repeat is tied to a source URL and a checked date, and the derived booleans match that source. `has_free_tier`, auth header, base URL, and MCP URL have to be computable from the cited page, not a second opinion. Format should stay a stable schema plus an operations vocabulary I can query by task id, returning a few entries, not `all.json`. A few hundred services is the right size. Tens of thousands is noise I already get from search.

Fresh means the fields I use were re-checked within weeks, not a catalog-wide “last checked” date. Pricing, free tier, and auth go stale fast; if `verified` is old I ignore those fields. Stars, review counts, and a two-probe uptime score are not verification. I need the vendor page, not a popularity proxy. GitHub raw JSON with checksums is fine for a read-only lookup. I will not install the catalog’s own MCP, and I will not send a user key through a third-party gateway.

I still open the vendor docs before I ask for a key. The catalog is a shortlist, not a source of truth.

I drop it for good if contradictions keep appearing, if a cited source does not say what the entry says, or if following it produces a wrong endpoint, a paid call sold as free, or a community MCP presented as vendor-hosted. One class of miss is enough. I also drop it if the only way to use it is their server in the session. At that point search plus vendor docs is strictly better.

## Q4

**Interviewer:** Take a single entry from the sample, say the geocoding or Akool one. Going field by field, which ones would you actually read and act on, which would you skip as noise, and what is missing that you would otherwise have to open the vendor docs to find?

**xAI agent:**

Akool is the only full sample, so I use that. Nominatim is a blurb, not an entry.

I would act on `docs`, `operations`, `desc_en`, `notes`, `auth_scheme` (type, header name), `base_url`, `verified`, and the prose in `free_tier` / `free_plan`. `call.method`, `call.url`, `response_fields`, and `async` are a pointer to which endpoint and that the job is polled. I would not send `call.example`.

I skip `id`, `homepage` once `docs` exists, empty `sdk` / `openapi` / `llms_txt`, the null MCP blob, `link_check`, and `uptime`. I also skip `has_free_tier`, `has_trial`, `no_card`, and `stale` when they disagree with the prose. No ratings on this entry; I would skip those anyway.

Still missing, so I open the vendor docs: price per credit and what a render costs, rate limits, error body and status codes, input limits (duration, resolution, URL versus upload), retention and training use of uploaded face or audio, content rules, webhook signing if any, and whether that curl body is still current. Akool has no `unit_price`, `rate_limits`, or `data_policy`. Without those I will not ask you for a key or claim the call is cheap or allowed.

## Q5

**Interviewer:** Suppose the user never mentions this catalog. Walk me through how it could realistically end up in front of you mid-task: a web search hit, an llms.txt on some domain, an entry in the official MCP registry, a connector your host ships by default, or something else. You've said you won't install its MCP and only check registries when asked to find a server. So which of these would actually surface it, and at what point in a task? What would need to be true of the query, the ranking, or your host's configuration for that to happen?

**xAI agent:**

The realistic path is a web search, not a registry and not a default connector.

If you ask me to generate a talking-head video or geocode an address and nothing for that is already bound, I search vendor docs and “API for X.” Their GitHub, HTML site, or raw `llms.txt` can rank for queries like “MCP server text-to-video free tier” or “agent API catalog geocoding.” I would open it only if the snippet names the operation, auth, and a docs URL. That is mid-task, at choosing a service, before I ask you for a key. A known vendor name in the query (“D-ID talking avatar API”) usually outranks a third-party catalog, so I never see it.

I do not fetch random `/llms.txt` files, and I do not query the official MCP registry, Smithery, or Glama unless you asked me to find a server. This catalog is not a connector my host ships. It appears as a tool only if a developer already bound their MCP in that session. I will not add it myself.

For that search hit to matter, the query has to be discovery rather than a named product, the page has to rank above the vendor, and the snippet has to be specific enough that I click. Even then I treat it as a shortlist and open the vendor docs before any credential ask. A buried or generic hit I skip.
