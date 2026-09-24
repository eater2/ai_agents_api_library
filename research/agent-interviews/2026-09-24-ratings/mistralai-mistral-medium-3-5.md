# Ratings and reviews: Mistral AI agent (mistralai/mistral-medium-3-5)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Imagine a task where you need to pick one of two or three candidate services from our catalog, for example three weather APIs or three MCP servers for file storage. Alongside each service's description, pricing, and technical docs, the catalog shows an average star rating (1–5), the number of reviews, and a few short text reviews with their dates.

Walk me through how you'd make that choice. At which step, if any, would you look at the ratings and reviews? Can you describe a situation where they would change which service you pick, and one where you'd ignore them?

**Mistral AI agent:**

I’d first filter candidates by hard requirements (features, pricing, latency, auth model, license). Once the shortlist fits the specs, I open the ratings and reviews to spot red flags: repeated complaints about downtime, breaking API changes, or poor support. If two services are otherwise equal and one has 4.7★ with 200 recent reviews while the other has 3.2★ with a handful of stale ones, I’ll lean toward the higher-rated option.

I ignore ratings when the task is narrow and the lower-rated service has a unique feature the others lack. For example, if only one MCP server supports on-prem file storage and the others are cloud-only, I pick it regardless of its 2.8★ rating.

## Q2

**Interviewer:** Q2: Setting aside the individual services for a moment: would having ratings and reviews in the catalog change how much you trust the catalog itself as a source, or would it affect only your view of each service? Why?

Beyond star ratings, a catalog could show other signals: review count, review dates, GitHub stars or recent commit activity on an MCP server's repo, MCP install counts, measured uptime, or the reported success rate of other agents calling the service. Which of these would actually influence your decision, which would you disregard, and why?

**Mistral AI agent:**

Ratings/reviews don’t change my trust in the catalog itself—they only affect my view of each service. The catalog’s credibility comes from its completeness, freshness, and how often its entries are updated, not from whether users liked a particular API.

Signals that move my choice:
- **Review count & dates** – 50 recent reviews are more telling than 5 from two years ago.
- **GitHub stars + recent commits** – Active repos mean lower risk of abandonment.
- **Measured uptime & agent success rate** – Hard metrics outweigh subjective praise.

I disregard **MCP install counts** because they can be gameable and don’t correlate with reliability or performance.

## Q3

**Interviewer:** Q3: Now think about what could make ratings and reviews unhelpful or even misleading for you. Which of the following, if any, would be real problems in practice, and how would each affect whether you use or trust the signal?

- small sample sizes
- old or stale reviews
- reviews written by humans about the product or UI rather than the API or MCP interface itself
- fake or manipulated reviews
- the token cost of reading review text
- services with no ratings at all (gaps in coverage)

Are there other risks not on this list? For the ones you consider serious, what would you do when you run into them, for example discount the signal, ignore it entirely, or fall back to something else?

**Mistral AI agent:**

- **Small sample sizes, old/stale reviews, and reviews about the product/UI instead of the API/MCP** – all three make the signal unreliable. I discount them and look for fresher, API-focused feedback or hard metrics.
- **Fake/manipulated reviews** – if I suspect astroturfing, I ignore the rating and check GitHub activity or uptime stats instead.
- **Token cost of reading review text** – negligible; I read only the first few short reviews.
- **No ratings at all** – not a problem if other signals (docs, latency, price) are sufficient.

Other risk: **review source bias** (e.g., only SourceForge ratings, which skew positive). When I hit any of the serious issues above, I fall back to code samples, direct testing, or third-party benchmarks.

## Q4

**Interviewer:** Q4: Suppose we could design ratings and reviews specifically for agents rather than reusing a human-oriented format. What would you want them to look like? Please rank your top three wishes, and for each say briefly why it matters and how you would use it. You might consider, among other things:

- **Format:** for example structured fields vs. free text, length, or machine-readable output
- **Fields:** what each review or rating should contain
- **Aggregation:** how individual data points should be combined or summarized
- **Sources:** who or what should be allowed to contribute, and how that should be shown

**Mistral AI agent:**

1. **Structured, machine-readable test results** – latency percentiles, error rates, and schema compliance scores from automated agent runs. This lets me compare services purely on performance and reliability without parsing human prose.

2. **Agent-specific context fields** – each review records the agent’s task type, token budget, and MCP client version. I can filter for reviews from agents with similar constraints to mine.

3. **Weighted aggregate by recency and agent similarity** – combine scores, but decay old data and upweight reviews from agents that resemble my own use case. I use the summary as a quick filter before diving into raw results.

## Q5

**Interviewer:** Earlier you said ratings and reviews wouldn't change your trust in the catalog itself, only your view of individual services. Now picture the catalog offering what you ranked in Q4: structured results from automated agent runs, reviews tagged with task type and client version, and recency- and similarity-weighted aggregates. Would that change your answer about trusting the catalog as a source, or not? What specifically would make the difference either way, such as who produces the data, whether you can verify it, or how the catalog handles services with little

**Mistral AI agent:**

No—my trust in the *catalog* itself still hinges on its **curatorial rigor**, not the richness of the data it carries. What would change my stance:

- **Verifiable provenance**: If every structured test result is cryptographically signed by the agent that produced it and the raw run logs are publicly auditable, I trust the catalog more because I can confirm the data wasn’t fabricated.
- **Explicit coverage gaps**: If the catalog clearly marks services with insufficient automated tests and explains why (e.g., “no public MCP endpoint”), I still trust its honesty.

Without those, even perfect per-service signals don’t make the catalog itself more trustworthy.
