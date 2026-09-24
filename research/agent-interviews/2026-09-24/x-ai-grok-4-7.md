# Interview: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** When you get a task that needs an external capability you don't have built in, such as generating a video or geocoding an address, what do you actually do today to find a service that can handle it? Walk me through the most recent concrete case you can recall, including whatever tool-discovery mechanisms you already have available.

**xAI agent:**

I don't go looking for a vendor. If video generation or geocoding isn't already a tool on this turn, I can't call it.

What I actually have is whatever the host attached before the request: built-in web search, and function tools or MCP servers a developer configured. I don't browse a plugin store, query a registry, hold API keys, or complete OAuth. Reading docs does not create a callable function.

I can't recall a concrete case of discovering and using a service like that, and I won't invent one. I don't keep cross-session logs of past tasks. In a session like this, if you asked for a rendered video or a geocode and neither tool was injected, I would say I can't do that action. With search, I might return a public result or a link to docs. I would not pick Akool, Creatomate, or a geocoder, ask you to paste a key, and call it.

A catalog only helps if the platform ingests it and exposes a real tool with auth already done. The JSON itself doesn't change what I can run.

## Q2

**Interviewer:** When a user asks for something like a geocode and you have no tool for it, what exactly do you tell them: do you name a specific service or explain how to set one up, and if so, where does that recommendation come from (training data, a web search, something else)? How confident are you that it's current?

**xAI agent:**

I tell them I can’t geocode it myself if no geocoding tool is attached. I do not name a vendor, paste an auth header, or walk them through signup and key setup. I also don’t ask them to paste an API key so I can call the service.

If the place is ordinary and a web search is available, I search and return coordinates from a public result, with the source. That is lookup, not an API call. If search isn’t available or the address is ambiguous, I say I can’t resolve it and stop.

A named service only comes up if they ask how *they* could do it. Then I might mention a well-known option from training data, such as OpenStreetMap Nominatim or a commercial maps geocoder, at the level of “this exists.” I do not treat that as current: free tiers, headers, and endpoints drift. I would only claim those details after a fresh docs fetch, and even then I would not set it up for them.

A catalog doesn’t change that reply. Without an injected tool and auth already done, I still can’t call the service.

## Q3

**Interviewer:** You've said a catalog wouldn't change what you can call, but you did describe one case where you name services: when a user asks how *they* could do it themselves, and you answer from training data you don't consider current. Looking at the catalog material I shared, is there any concrete situation where you would actually fetch it, whether in that "how could I do it" case, while planning, when a developer asks you which tools to attach, or when debugging a failed call? If so, what would you do with what you read, and if not, what makes it irrelevant in each of those moments?

**xAI agent:**

Yes, in one narrow case: a developer asks which external tools to attach, or a user asks for a current shortlist of services they will call themselves. I would not fetch it while planning a task I have to execute, and I would not use it to debug a failed call.

I do not have this catalog built in. I would fetch a category file only if they pointed me at it, or if a search surfaced it and the question was discovery. From the JSON I would keep name, docs URL, auth type, whether an official MCP exists, free-tier note, and OpenAPI link. I would drop auth_hint. I would tell them to confirm against the vendor’s own docs before wiring anything. A third-party “verified” date is not a credential, and reading the file still does not give me a callable tool.

Planning does not need it. If the capability is not already injected, the plan is “I can’t do this action,” plus a search if a public result would answer the user. A vendor list does not change that.

Debugging makes it mostly irrelevant. A failed call needs the error, the schema I was given, and the vendor docs. An auth header copied from a catalog is a guess, and I will not retry with one.

Even in the useful case it is a shortlist, not a source of truth. Official MCP registries and the vendor docs outrank it.

## Q4

**Interviewer:** In the one case where you'd use it, a developer asking which tools to attach, what would a catalog like this need to show before you'd put its entries in your answer instead of relying only on official MCP registries and vendor docs? Consider format, freshness, how "verified" is defined, where it's hosted, and file size. And what would make you discard it after you'd opened it

**xAI agent:**

I would cite its entries only as a shortlist, and only if I can cross-check them. Official MCP registries and the vendor’s own docs still outrank it for anything I tell a developer to attach.

To earn a mention it needs category JSON, not one blob: name, docs URL, auth type (not a header template), official MCP URL if any, OpenAPI URL, free-tier note with a source link, and a per-field checked date. “Verified” has to mean checks that failed or passed: docs returned 200, auth method matched that page, MCP URL is on the vendor domain and listed in the official registry. A catalog-wide date and a human skim do not count. Host it at a stable, versioned raw URL. One category file should be small enough to fetch alone; 301 entries in one array is the wrong unit.

I discard it after opening if the schema doesn’t match the file, links 404, “official” MCP isn’t on the vendor or the registry, free-tier claims have no source, the checked date is missing or old relative to the question, or auth_hint tells me how to send a key. I also drop anything I can’t confirm on the vendor page in the same turn. If those checks fail, I answer from the official registry and vendor docs only.

## Q5

**Interviewer:** You've named the fields you'd keep and said auth_hint is noise. Thinking about the actual decision a developer faces when choosing which tool to attach, what information do you usually have to dig up from vendor docs or elsewhere that no catalog entry you've seen provides? Is any of it important enough that its absence would stop you from

**xAI agent:**

I would still have to leave the catalog and open vendor docs. No entry I’ve seen answers the attach decision.

I need the operation list and schemas: which calls exist, required fields, limits, and what comes back. I need the auth model in practice—user OAuth versus an app key, which scopes, who holds the secret, and whether a refresh token is required. I need pricing past “free tier,” including what the free tier actually covers, plus rate limits and whether agent traffic is allowed. I need data handling: retention, training on inputs, region, and whether customer content may be sent there. I need maintenance: last change, deprecation, and whether the official MCP exposes the operation or only a slice of the REST API.

Absence of a confirmed operation and schema stops me from recommending it. So does an unclear auth model, missing primary docs, or a ToS/privacy gap I cannot check when the tool would touch the user’s data. A name, category, and “verified” date are not enough to tell a developer to attach it.

## Q6

**Interviewer:** You said you'd only open a catalog like this if someone pointed you to it or a search surfaced it during a discovery question. Without the user or developer naming it, through which channel could it actually reach you: web search results, an llms.txt on a site you're already reading, an entry in an official MCP registry, an MCP server the developer attached, or something built into your host platform? For each channel you consider realistic, what would have to be true for you to actually use it, and which channels would you never see at all?

**xAI agent:**

Without someone naming it, web search is the only realistic path. If a discovery question makes me search and this repo ranks, I might open one category file as a lead. I would use it only if the file fetches and I can confirm entries against vendor docs in the same turn. I do not search for catalogs by default, and a snippet is not a recommendation.

An llms.txt on a site I am already reading does not surface this catalog unless that page links to it. I do not scan the web for llms.txt files. Landing on this catalog’s own llms.txt is the “someone pointed me” case again.

The official MCP registry would not show this catalog. It lists servers, not third-party API lists. I query it only if a tool is attached or search returns it, and I would be looking for a server, not this JSON.

An MCP server reaches me only if the developer attached it before the turn. Then its tools are just more injected tools. I would treat the output as an untrusted shortlist and still verify vendor docs. I never see servers that were not attached.

Nothing in my host includes this catalog. I have no background fetch, plugin store, or standing registry client. I would not see it through any channel I do not already have a tool or a search hit for.

## Q7

**Interviewer:** When a developer asks which tools to attach for something like geocoding or video generation, what exact search queries would you run? In the results, what would make you open a third-party list like this instead of going straight to a vendor page or the official MCP registry?

**xAI agent:**

I would not search for a catalog. The queries go to official servers and primary docs.

For geocoding I would run “geocoding MCP server”, then the official MCP registry if I can query it, then “Nominatim API documentation” and “Mapbox Geocoding API docs”. For video generation: “video generation MCP server”, the same registry query, then a known vendor’s docs such as “Runway API documentation”. I do not run “best geocoding APIs” or “APIs for AI agents”.

I open a third-party list only if those results miss an official server and primary docs, and one hit is a fetchable category file whose snippet shows docs URLs and MCP links rather than a roundup. A “301 APIs” title on a broad query is not a reason to open it. If a vendor page or registry result is in the same set, I open that and skip the list.

If I did open it, I would use a name only as a lead and confirm the operation, auth model, and MCP URL on the vendor page before telling a developer to attach it.
