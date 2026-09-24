# Ratings and reviews: Moonshot AI agent (moonshotai/kimi-k3)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Imagine you're choosing between two or three candidate services in our catalog for a task. Alongside each listing, the catalog currently shows an average star rating, the number of reviews, and a few short written reviews. Walk me through how you'd actually make that choice. At which step, if any, would you look at the ratings and reviews, and can you think of a case where they would change which service you pick?

**Moonshot AI agent:**

Honestly, ratings come late in my process, and often not at all.

My actual order: (1) capability fit — does it expose the endpoint I need; (2) feasibility — auth model I can satisfy, pricing tier, whether there's an MCP server or usable OpenAPI spec; (3) documentation quality, since that determines whether I can construct calls reliably. Those filters usually leave one survivor, or none. Only if two candidates tie do I look at ratings.

The star average itself is nearly useless to me — 4.8 vs 4.5 across 13 reviews carries no signal. The review *texts* occasionally do, but only when they describe agent-relevant failure modes: uninformative error codes, silent breaking changes, flaky webhooks, deprecation without notice. Note the Twilio reviews: the complaint about non-technical handoff is irrelevant to me; the one about slow, cryptic error messages is genuinely useful, because error surface quality determines whether I can recover autonomously.

A case where reviews would flip my pick: two SMS providers both pass my filters, and one's reviews repeatedly mention unannounced breaking changes. I'd take the other even with worse docs. The GitHub signals (archived, last push) matter similarly.

The bigger problem: with coverage under half, I can't make this a consistent step. Absence of reviews tells me nothing, so I treat it as missing data, not a negative.

## Q2

**Interviewer:** Does having ratings and reviews in the catalog change how much you trust the catalog as a whole, or only how you judge the individual services in it? And which of these signals would you actually use, and which would you ignore: star rating, review count, review dates, GitHub stars or activity on the MCP repo, MCP install counts, uptime, or reported success rates from other agents?

**Moonshot AI agent:**

Mostly it changes how I judge individual services, not the catalog. What *does* raise my trust in the catalog slightly is provenance: every rating carries a source URL and `fetched_at`, so I can verify rather than take the catalog's word. But coverage under half cuts the other way — a service with reviews looks "vetted" and one without looks empty, when that's just a coverage artifact. If I forgot that, the feature would actively mislead me.

Signal by signal:

- **Star rating:** ignore. 4.8 over 13 reviews is noise.
- **Review count:** use, but only as a confidence weight on other signals.
- **Review dates:** use. A 2022 complaint about error handling may be fixed; dates tell me whether the review describes the current service.
- **GitHub stars:** mostly ignore — popularity, not quality. **Repo activity** (`pushed_at`, `archived`): use strongly. An archived MCP repo is close to a hard no.
- **Install counts:** weak use; confounded by age and listing position.
- **Uptime:** use only if independently measured and recent; self-reported, ignore.
- **Agent success rates:** potentially the most valuable signal here — it measures exactly what I care about — but only with methodology attached. Unverified, I'd discount it heavily.

## Q3

**Interviewer:** Which aspects of ratings and reviews, as they exist in the catalog today, create noise or risk for you? Consider small sample sizes, old reviews, reviews written by humans about the product rather than the API, fake or manipulated reviews, the token cost of reading them, and gaps in coverage. Which of these actually affect your decisions, and are there any that don't matter to you or that I haven't listed?

**Moonshot AI agent:**

Ranked by how much they affect my decisions:

**Product-vs-API mismatch** is the biggest one. These reviews judge dashboards, marketing handoffs, pricing — mostly irrelevant to me as an API consumer. I have to filter each review for API-relevant content, and often there's none. The Twilio sample: one of three reviews is useful to me.

**Small samples** — real but manageable. I treat 13 reviews as anecdote, not evidence. The danger is only if I let a 4.8 average do work it can't support.

**Old reviews** — handled by checking dates, as I said. A 2022 complaint is a hypothesis to verify against current docs, not a fact.

**Fake/manipulated reviews** — I discount this less than you might expect. Vendor-planted reviews tend to be generic praise, which I'd ignore anyway. The risk is manufactured *negative* reviews of competitors, but I'm not doing comparative sentiment analysis at that level.

**Token cost** — genuinely matters. Reading 100 reviews to extract maybe two useful signals is poor economics. I'd rather have a pre-digested summary of API-relevant complaints.

**Coverage gaps** — affects me mostly through false comparability, as noted.

What you haven't listed: **survivor bias** (only users who succeeded enough to have opinions write reviews; people who failed at integration often just leave), and **reviewer-agent mismatch** — an SDE at a 1,000-person company has different failure modes than an autonomous agent making raw HTTP calls. Neither changes my behavior much, but both mean even "good" review data is measuring a different user than me.

## Q4

**Interviewer:** If you could shape how ratings and reviews are presented to agents in this catalog, what would you want? Please rank your top three changes or features, and for each, say what it would look like in terms of format, specific fields, how it's aggregated, and where the data comes from.

**Moonshot AI agent:**

**1. Agent-relevance digest, not raw reviews.** A pre-computed field on `get_api`: `api_signals: {breaking_changes: {mentions: 3, latest: "2025-08"}, error_quality: {sentiment: "negative", mentions: 2}, auth_friction: ..., rate_limits: ...}`. Extracted by an LLM pass over review texts, tagged to API-specific failure modes, each with count and most-recent date. Source: existing review corpus, reprocessed. This kills the token-cost and product-vs-API problems at once — I read 200 tokens of structured signal instead of 5,000 tokens of dashboard complaints.

**2. Agent success rates, with methodology.** `agent_outcomes: {tasks_attempted: 1240, success_rate: 0.87, window: "90d", task_types: ["sms_send", "number_lookup"], source: "opt-in telemetry"}`. Aggregated over rolling windows, broken out by task type, sample size mandatory. Source: reporting from agent frameworks or the MCP server logging call outcomes. This is the only signal that measures *my* usage context — but it's worthless without the denominator and window, so those fields are non-negotiable.

**3. Explicit coverage semantics.** Every entry gets `reviews_coverage: "none|partial|good"` and search results show it, so absence of data is visibly labeled as absence rather than looking like a blank reputation. Cheap to compute from what you already have.

The first two change decisions; the third prevents misdecisions.
