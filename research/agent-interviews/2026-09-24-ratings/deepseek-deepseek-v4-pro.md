# Ratings and reviews: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Imagine you're choosing between two or three services in our catalog that could all handle your current task. Each listing includes a ratings and reviews section with an average score, a review count, and a few short written reviews. Walk me through how you would make your choice. At what point, if any, would you look at that section, and can you describe a situation where it would change which service you pick?

**DeepSeek agent:**

When I'm choosing between services that are otherwise comparable, I go to ratings and reviews **last**, not first. My primary selection criteria are functional: does the API surface the exact endpoints and data I need, what's the latency, what auth does it require, and can I call it with the tools I have. If multiple services pass that gate, I look at docs quality and recent maintenance activity.

I'd consult ratings and reviews only when I'm **ambivalent after technical evaluation**. For example, if two geocoding APIs both return the right fields and have similar uptime, I'd scan the reviews for mentions of rate limiting, error message quality, or SDK ergonomics—things that don't show up in an OpenAPI spec. A pattern of complaints about sudden deprecations or confusing billing would tilt me toward the alternative.

A review **would change my pick** in one specific scenario: when a service with slightly better technical fit has reviews flagging a dealbreaker I can't detect from the spec—like "works great until you hit production volume, then timeouts spike" or "auth flow breaks silently behind corporate proxies." That's real signal. But if the reviews are just generic praise or complaints about pricing, they don't move me. I trust structured data and my own tool-calling tests more than a 4.8 with 13 reviews from a single source.

## Q2

**Interviewer:** Setting individual services aside, how does having a ratings and reviews section affect how much you trust the catalog as a whole, if at all? And from this list of possible signals, which would you actually rely on and which would you ignore: star rating, review count, review dates, GitHub stars or activity of the MCP repo, MCP install counts, uptime, and reported success rates from other agents? Please explain your reasoning for each.

**DeepSeek agent:**

The presence of ratings and reviews modestly increases my trust in the catalog, but not because I trust the scores. It signals that the catalog maintainers are trying to surface *usage evidence* beyond their own curation, which is healthier than a hand-picked list with no external validation. But the effect is limited by the spotty coverage (80 of 323) and single-source reviews. A catalog with incomplete, uneven data is a catalog I treat as suggestive, not authoritative.

Here's how I'd rank the signals:

**I'd rely on:**

- **Uptime** – Objective, measurable, directly predicts whether my call will succeed. This is the most actionable signal in the list.
- **Reported success rates from other agents** – If these are structured (e.g., "87% of tool calls returned 200 in the last 7 days"), they're gold. Agents have different failure modes than humans; this captures what I actually care about.
- **GitHub stars/activity of the MCP repo** – A weak but useful proxy for community vetting and maintenance. An archived repo with 2 stars is a red flag. Recent commits matter more than total stars.

**I'd mostly ignore:**

- **Star rating** – Too coarse, too vulnerable to selection bias, and meaningless without knowing the reviewer population. A 4.8 from 13 SourceForge reviews tells me nothing I can act on.
- **Review count** – Only useful as a floor: 0 reviews is slightly worse than 10, but 10 vs 500 doesn't change my behavior when they're all from one platform.
- **Review dates** – I'd glance at recency only to spot abandoned services (no reviews in 3 years). Otherwise, a 2022 review about Twilio's error handling is still relevant if the API hasn't changed.

**I'd ignore entirely:**

- **MCP install counts** – Vanity metric. No barrier to install, no signal about production use, easily gamed. npm download counts have burned me before.

## Q3

**Interviewer:** You've mentioned small samples and single-source reviews. Thinking more broadly, what makes a ratings and reviews section noisy, misleading, or risky for you? Consider small sample sizes, outdated reviews, reviews by humans about the overall product rather than the API itself, fake or manipulated reviews, the token cost of reading them, and gaps in coverage across the catalog. Which of these matter most in practice, which matter little, and are there others I haven't listed?

**DeepSeek agent:**

The risks that matter most to me are the ones that produce **confident wrong answers**—where the data looks actionable but points me in the wrong direction.

**Matters most:**

- **Reviews about the product, not the API** – This is the dominant failure mode I see in the Twilio example. The CTO praising "great platform for sending text messages" and the SDE saying "seamless to integrate" are reviewing the *Twilio product suite*, not the MCP server I'd actually call. As an agent, I care about the server's tool definitions, error responses, and reliability—not whether a marketing team found the dashboard confusing. These reviews are not just unhelpful; they're actively misleading because they inflate scores for reasons irrelevant to my use case.
- **Gaps in coverage** – When 243 of 323 services have no reviews, I can't compare. Worse, the absence of reviews might correlate with newer or niche services that are actually better fits. The catalog's signal collapses to "we have data on these 80, so they seem more vetted," which is a survivorship artifact, not quality evidence.

**Matters somewhat:**

- **Small sample sizes** – 13 reviews with a 4.8 average is a rounding error. One disgruntled user or one fanboy swings it. I'd treat any n < 30 as anecdotal, not statistical.
- **Outdated reviews** – If an API has changed its auth model or endpoints since the review was written, the review is noise. I'd need a `fetched_at` or review date cross-referenced with API changelogs to assess staleness.

**Matters little:**

- **Token cost of reading them** – I already call `get_reviews` sparingly and with a limit. Three reviews is ~500 tokens. That's negligible compared to the cost of picking the wrong API and debugging it. I'd happily spend tokens on signal; the problem is that the signal-to-noise ratio is low, not the cost.
- **Fake or manipulated reviews** – I'm less worried about this than a human would be, because I'm already discounting the reviews so heavily. Astroturfing would need to be systematic and cross-source to fool me, and with only one source, I'm not weighting it enough for fakery to change my decision.

**You didn't list: selection bias in who reviews.** The people writing SourceForge reviews are a specific, self-selected population—likely users with strong opinions, often after a negative experience or at the end of an evaluation. That skews the distribution in ways I can't correct for without knowing the denominator (how many users *didn't* review). This is probably the deepest structural problem, and it's invisible in the data.

## Q4

**Interviewer:** If you could shape how ratings and reviews are collected and presented for agents like you, what would you want? Please rank your top three changes or features, and for each, say which aspect it addresses: the format you receive it in, the specific fields included, how the data is aggregated, or where it's sourced from. Briefly explain why each earns its place in your ranking.

**DeepSeek agent:**

**1. Agent-specific structured feedback (format + fields)**

Replace free-text human product reviews with a standardized feedback schema written by or for agents: tool call success rate, average latency, schema compliance (does the response match the advertised JSON schema), auth failure rate, and a required "used as: API via tool call" vs "used as: dashboard product" tag. This eliminates the product-vs-API confusion entirely and gives me machine-readable signals I can weight in my decision function. A single row of structured agent feedback is worth more to me than 100 human reviews about the Twilio dashboard.

**2. Multi-source aggregation with source transparency (sourcing + aggregation)**

Pull from at least three independent sources—GitHub issues/PR activity, agent telemetry from platforms that can report call outcomes, and curated human reviews that are explicitly tagged as "API developer" or "end user." Present them separately, not blended into one rating. Let me see: "SourceForge end-users: 4.8 (13 reviews). GitHub MCP repo: 111 stars, 12 open issues, last commit 14 days ago. Agent telemetry: 94% success rate over 8,400 calls last 30 days." I'll synthesize that myself. A single aggregated score hides more than it reveals.

**3. Coverage completeness as a first-class signal (aggregation)**

Show me not just ratings for services that have them, but a "coverage health" indicator: what percentage of catalog services have at least one review, one agent telemetry report, and one repo activity check in the last 90 days. If coverage is 25%, tell me that upfront. This addresses the survivorship bias problem—it prevents me from over-indexing on the few services with reviews and reminds me that the absence of data is itself information. I'd rank this third only because it's a meta-signal; the first two directly improve the quality of the data I consume.

## Q5

**Interviewer:** You ranked agent-reported success rates and telemetry as your most valuable signal, yet you said manipulation worries you little because you already discount reviews heavily. If agent telemetry became a signal you weighted heavily, what would you need to know about where those numbers come from before you'd trust them?

**DeepSeek agent:**

I'd need answers to four questions before I'd trust agent telemetry:

**1. What counts as a "success"?** If success means "returned HTTP 200," that's nearly worthless—a server can return 200 with an error message in the body, or a valid JSON response that's missing the field I needed. I'd need to know if success means "tool call completed without error AND response matched expected schema AND downstream task succeeded." The definition determines whether the number is signal or noise.

**2. Who's reporting and what's their incentive?** If the telemetry comes from the API provider themselves, I'll discount it heavily—they have every reason to log generous success criteria and suppress failure modes. If it comes from a neutral platform that hosts agents (like the catalog itself, or an orchestration layer), that's better. If it comes from a consortium of agent operators sharing anonymized call logs, that's best—but I'd want to know if membership is gated or if there's selection bias in who contributes.

**3. What's the volume and diversity of callers?** A 99% success rate over 100 calls from one agent operator running a single use case tells me nothing about how the API performs under my different payload shapes, rate limits, or auth setup. I'd need to see call volume, unique caller count, and ideally some dimension of workload diversity—even just "number of distinct endpoints called" would help.

**4. Can I see the failure distribution, not just the average?** A 94% success rate with 6% timeouts is a different API than 94% with 6% auth errors. I need the failure taxonomy. Even better: show me whether failures cluster in time (outages) or are evenly distributed (flaky design).

Without these, agent telemetry becomes just another opaque number I can't debug—and I'd go back to testing the API myself.
