# Product test: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** You have the four tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text in front of you. Take task 1 and walk me through what you would actually do, step by step, from the moment you receive it until you have something working. At which point, if any, would you call search_apis, and when would you instead use web search, your own knowledge, or something else?

**OpenAI agent:**

1. I’d check what tools are actually connected. This platform can reason about a storyboard and write code, but I don’t have a video renderer merely because its API appears in a catalog. If an image or video tool were connected, I’d check its cost and use it if it can produce five seconds for free.

2. If not, I’d ask one consequential question: **Does a simple animated sunset count, or does the user need photorealistic text-to-video?** “No budget” rules out assuming a paid trial or requesting a card.

3. For a simple clip, I probably **wouldn’t call `search_apis`**. I’d use my knowledge to write a small SVG/HTML animation of the sun, sea and moving reflections, then render it to a five-second MP4 with FFmpeg **if code execution and FFmpeg are available**. I’d inspect the output and confirm its duration. Without execution, I could give the user runnable files, not claim I made the video.

4. For photorealistic generation, I’d call `search_apis` with a narrower query and `category: "video-generation"`, then use web search or official documentation to verify that a candidate currently offers *free text-to-video*, at the required duration, without payment setup. The supplied results do not establish that: Mux encodes video; Gemini’s listed free tier is for Flash/Pro, and its MCP searches docs rather than generating video; Akool and Creatomate don’t clearly meet this prompt.

If verification found no genuinely free option, I’d say so and offer the animated alternative.

## Q2

**Interviewer:** You've already given a first read of the task 1 results. Looking at the actual search results for all three tasks, would you act on them? For each task, which result would you pick, if any, and which results are irrelevant, badly ranked, or missing something you'd expect to see?

**OpenAI agent:**

I’d use these results as leads, **not as permission to act or proof that a service fits**. None of the catalog tools actually generates a video, geocodes an address, or sends an SMS.

**1. Five-second sunset video, no budget:** I’d pick **none** for text-to-video. Mux processes existing video; Gemini’s listed free tier doesn’t establish free video generation, and its MCP only searches documentation. Voyage is irrelevant. Akool focuses on avatars and face swaps; Creatomate renders templates, so it might work for a *simple animated* sunset, not the implied generated scene. I’d first check for a connected video tool or make an animation locally if execution is available. The search is missing a clearly identified, currently free text-to-video option—and should say plainly if none is verified.

**2. Geocode 200 Polish addresses:** I’d investigate **Geoapify first**, then verify its current allowance, batch workflow, coverage, and terms in its docs. Google Maps is another candidate, but the quoted “$200 monthly credit” needs checking before I’d rely on it. I would **not** send 200 addresses to public Nominatim: the result itself says bulk use is prohibited. IP2Location geolocates *IP addresses*, not streets; Esri is relevant but oddly categorized. I’d also want expected accuracy and handling of unmatched or ambiguous addresses.

**3. SMS reminder:** **Twilio** is the best match, with Vonage as an alternative. I’d verify current pricing, destination-country rules, consent, and account setup, then require a connected, authorized sending tool and confirmation of the recipient and message before sending. LINE, WhatsApp, and Discord are not SMS. Twilio’s trial credit should not be labeled a permanent free tier.

## Q3

**Interviewer:** Take Twilio for task 3 and Geoapify for task 2. Going from the catalog entry to a working call, which specific fields would you read first, which are missing from what get_api returns today (for example base URL, auth header format, an example request, price per call, rate limits, an MCP config snippet), and which would still send you to the official docs even if the catalog had them?

**OpenAI agent:**

I’d read **`docs`, `auth`/`auth_hint`, `mcp.type` and URL, `notes`, `free_tier`, `verified`, and `link_check`** first. I’d call `get_api` for each, but only Gemini’s full entry is shown here, so I cannot assume Twilio’s or Geoapify’s detail records contain usable call instructions.

**Geoapify (200 Polish addresses):** I need the geocoding endpoint, how to send the key, a request/response example, whether there is a batch endpoint, credits charged per address, rate limits, and terms for submitting customer addresses. The search result gives none of that. I’d test a few varied addresses, inspect match confidence and ambiguity, then run the batch with throttling and retain the original address alongside each result.

**Twilio (one SMS):** I need the messaging endpoint, the supported credential format, required sender and recipient fields, an example request, destination-specific price, trial restrictions, and delivery-status behavior. The entry calls trial credit a “free tier” while marking `has_trial: false`; I would not trust that classification. Its “official MCP” URL is a GitHub repo, not a ready-to-call endpoint. I’d need an installation/config snippet and a clear account of which tools it exposes before connecting it.

Even if the catalog supplied all those fields, I’d check **official docs and account settings** for current prices, quotas, credential setup, trial limitations, and SMS compliance. I’d use platform secrets, make a small test call where appropriate, and never send the customer’s reminder without authorization and confirmation of the number and text.

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Where would that wording make you reach for search_apis at the right moment, and where would it pull you in when you shouldn't, or fail to trigger when you should? Quote the specific phrases you would change and what you would replace them with.

**OpenAI agent:**

The useful trigger is **“when choosing which MCP server to connect”**: that is a discovery task. **“Skip it when a connected tool already does the job”** also correctly avoids an unnecessary lookup.

I’d change these phrases:

- **“Use when a task needs an external service”** → **“Use when a task needs an external capability *and* no suitable tool is connected, or when comparing providers. Search finds candidates; it does not perform the task.”** The original could pull me into catalog search before checking my tools.
- **“Returns verified services”** → **“Returns catalog entries with dated checks; verify task fit, availability, terms and pricing in official documentation.”** A reachable docs link does not verify free text-to-video.
- **“Prefer, in this order: `no_auth: true` …”** → **“First require a fit for the exact operation and usage pattern; then compare setup, cost and access.”** Otherwise it promotes public Nominatim for a prohibited bulk job.
- **“`mcp.type: "official"`: the user connects it once, then you call it as a tool”** → **“Check what the MCP actually exposes and whether its URL is a connectable endpoint or a repository.”** Gemini’s MCP searches docs; it cannot generate the clip.
- **“`has_free_tier: true`: the user can try it without paying”** → **“Distinguish ongoing free usage from trial credit; verify whether billing setup is required.”**
- **“`get_reviews` … before recommending a service”** → **“Consult reviews when relevant; prioritize official operational docs and task-specific tests.”**

I’d add a trigger for **volume or delivery constraints**: “For batch jobs, zero-budget requests, or actions affecting third parties, check quotas, terms, real cost and authorization before recommending or calling a service.”

## Q5

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the catalog data, latency, token cost of the results, or overlap with your built-in web search and connectors? Of these, which is the real blocker, the one that would still keep you away even if the others were fixed?

**OpenAI agent:**

**Trust in the catalog’s task-level accuracy is the blocker.** Not whether a link was reachable, but whether the result can actually do the requested job under the user’s constraints. The examples fail that test: video search ranks an encoder and an embeddings API; the geocoding search includes IP geolocation and a public server whose stated policy rules out the batch; SMS search includes non-SMS channels. Trial credit is also presented as a free tier. I’d have to independently verify the shortlist before using it.

The other factors matter less:

- **Install friction:** I wouldn’t ask a user to connect a discovery server for one task. If it were already connected, I might query it.
- **Latency and tokens:** These results are small enough; extra calls are acceptable if they save research.
- **Overlap:** A connected task tool takes precedence. Web search and official docs remain necessary for current pricing, limits and setup, but a well-ranked catalog could still speed up discovery.

Even with effortless installation, instant compact results, and no overlapping search, **these particular results would not be reliable enough to drive my choice without rechecking them**. Conversely, if task fit and data quality improved, I would use the catalog as a shortlist—not as a way to execute the task or as final authority.

## Q6

**Interviewer:** If we could change only three things so that you would reach for this catalog by default, what would they be? Rank them from most to least important, and for the top one, describe what a result would need to look like for you to act on it without independently re-checking the shortlist first.

**OpenAI agent:**

1. **Make search enforce the actual task constraints.** Rank by operation, volume, destination and budget—not keyword overlap. For these examples, exclude video encoders from text-to-video, IP lookup from street geocoding, and chat apps from SMS. Mark a result **ineligible**, with a reason, when its terms or free allowance rule out the job.

   For me to act on a result **without rechecking the shortlist**, a Geoapify result for “200 street addresses in Poland” would need to say: “Street-address geocoding supported; 200 requests permitted under the stated plan and rate limit; estimated credits/cost for this batch; batch or throttled-call method; key requirement; likely limitations on Polish address matches.” Each consequential claim should link to the *specific official documentation section*, show when it was checked, and distinguish documented facts from estimates. “Act” would mean **choose it for setup or a small test**, not submit customer addresses or assume pricing is guaranteed without checking the account and obtaining authorization.

2. **Make results operational.** Provide the actual endpoint or callable MCP tool, required fields, auth format, minimal request, response fields, and setup instructions. Label a GitHub MCP repository as an installation, not a remote endpoint; label a docs-only MCP as docs-only.

3. **Make freshness and uncertainty explicit.** Separate permanent free allowances from trials, expose conflicting or unverified claims, and make it easy to report bad matches. A dated link check alone is not verification that the service performs the operation.

With those changes, I’d reach for it by default **when I need to discover a provider**. I still wouldn’t use it when an appropriate tool is already connected.
