# Ratings and reviews: Alibaba (Qwen) agent (qwen/qwen3.8-max-0902)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Imagine you're choosing between two or three candidate services in our catalog for a task. Alongside each service's description and schema, the entry shows an average star rating, the number of reviews, and a few short text reviews with dates. Walk me through how you'd make that choice: would you look at the ratings and reviews at all, at which step, and could they change which service you pick?

**Alibaba (Qwen) agent:**

I’d look at them, but not first.

Step 1: capability fit. Does the service actually solve the task? Are the endpoints, schema, auth model, rate limits, pricing, and data coverage suitable? If one service clearly fits better, ratings won’t change my pick.

Step 2: implementation risk. I’d compare docs quality, error handling, SDKs, maintenance signals, and any signs of flakiness or abandonment. Ratings enter here, mostly as weak tie-breakers.

Step 3: reviews, if the candidates are still close. I’d care less about the average score and more about recurring themes: “rate limits are opaque,” “webhooks fail silently,” “billing changed suddenly,” “support is slow,” or “the sandbox doesn’t match production.” Recent reviews matter more than old ones, and a small number of reviews gets little weight.

Could they change the pick? Yes, if two services are functionally similar and one has recent, consistent complaints about reliability, auth, hidden costs, or poor support. They would not change the pick if the higher-rated service lacks the required endpoint or has weaker schema fit.

For me, reviews are risk evidence, not popularity evidence.

## Q2

**Interviewer:** You described reviews as risk evidence about a service. Does having ratings and reviews in the catalog change how much you trust the catalog itself, or only your view of individual services? And which of these signals would actually carry weight for you: star rating, review count, review dates, GitHub stars or activity of the MCP repo, MCP install counts, uptime, or reported success rates from other agents?

**Alibaba (Qwen) agent:**

It changes my trust in the catalog only slightly. If ratings and reviews are fresh, attributed, and not cherry-picked, they suggest the catalog is maintained. If coverage is sparse or stale, they do not add much and can look decorative. My trust in the catalog still depends mostly on accurate schemas, working endpoints, and clear docs.

For individual services, the signals carry different weight:

- Reported success rates from other agents: strongest, if task-specific and recent.
- Uptime or reliability data: strong for production risk.
- Review dates and recurring themes: useful, especially recent complaints about auth, billing, rate limits, or breaking changes.
- GitHub activity of the MCP repo: useful for maintenance, but only for the integration layer.
- Review count: modest; more volume helps if credible.
- Star rating: weak tie-breaker.
- MCP install counts: weak; popularity does not prove fitness.

If these signals were absent, my process would not change much: I would still prioritize capability fit, schema, docs, and direct testing.

## Q3

**Interviewer:** Now the flip side: what in ratings and reviews would you treat as noise or even a risk? For example: small samples, old reviews, reviews written by humans about the product rather than the API, fake or manipulated reviews, the token cost of reading them, or gaps where many services have no reviews. Which of these matter most to you, and how would you handle each one when deciding?

**Alibaba (Qwen) agent:**

I’d treat ratings and reviews as weak, noisy evidence by default. The biggest risks are misleading relevance and false confidence.

What matters most, roughly in order:

1. **Reviews about the wrong thing**
   If reviews are about a consumer product, dashboard, sales support, or UI, but I’m choosing an API, they may be almost irrelevant. A service can have great product reviews and a terrible API, or vice versa.  
   **Handling:** only give weight to reviews mentioning API behavior: endpoints, auth, rate limits, webhooks, errors, latency, SDKs, billing for API usage, sandbox vs production mismatch.

2. **Small samples**
   A 5.0 rating from 2 reviews is not meaningful. Even 4.6 from 8 reviews is weak.  
   **Handling:** treat low-count ratings as anecdotal. Use them only as tie-breakers, and never let them override schema fit or testing.

3. **Old reviews**
   APIs change: pricing, auth, quotas, deprecations, ownership, reliability. A glowing review from three years ago may describe a different service.  
   **Handling:** favor recent reviews, especially from the last 6–12 months. Discount old reviews unless they describe stable, structural strengths or weaknesses.

4. **Fake or manipulated reviews**
   Overly uniform praise, generic wording, clustered dates, reviewer accounts with no history, or reviews that sound like marketing copy are risk signals.  
   **Handling:** look for specificity. Concrete failure modes are more believable than vague praise. If reviews look manufactured, I discount them and may trust the service less.

5. **Gaps in review coverage**
   If many services have no reviews, I should not treat “no reviews” as “bad.” It may just mean the catalog lacks data.  
   **Handling:** treat missing reviews as unknown, not negative. Do not penalize services without ratings unless other signals are also bad.

6. **Average star rating alone**
   Stars compress too much. A 4.2 could mean “great but expensive,” “unstable but powerful,” or “good support, bad docs.”  
   **Handling:** use the average only as a rough tie-breaker. Prefer recurring themes over the score.

7. **Token cost of reading reviews**
   This matters operationally, but less than decision quality. If reading dozens of long reviews costs many tokens for a low-stakes choice, it’s wasteful.  
   **Handling:** fetch reviews only when candidates are close, when reliability matters, or when other signals conflict. Skim a few recent reviews rather than all of them.

The safest rule: reviews can raise flags, but they should not replace capability fit, schema inspection, docs, and direct testing. I’d use them mainly to detect repeated operational problems, not to rank services by popularity.

## Q4

**Interviewer:** If you could design how ratings and reviews are presented to agents in our catalog, what would you want? Please rank your top three changes or features, and for each, tell me what it would look like in practice: the format, which fields it would include, how it would be aggregated, and where the data would come from.

**Alibaba (Qwen) agent:**

Here are the three changes I’d prioritize, ranked by how much they would improve agent decision-making.

---

## 1. Replace “average rating” with a structured evidence card

**Rank: 1**

The most useful change would be to stop presenting ratings as a single star score and instead expose a compact, machine-readable evidence card.

### What it would look like

In `search_apis`, I’d want a tiny summary:

```json
{
  "id": "twilio",
  "evidence": {
    "confidence": "medium",
    "as_of": "2026-09-24",
    "window_days": 180,
    "api_reliability_score": 0.87,
    "review_signal": "mostly_positive",
    "risk_flags": ["billing_complaints", "rate_limit_confusion"],
    "sample_size": 42
  }
}
```

In `get_api`, I’d want the full card:

```json
{
  "id": "twilio",
  "evidence_card": {
    "generated_at": "2026-09-24T16:58Z",
    "window_days": 180,
    "confidence": "medium",
    "coverage": {
      "has_reviews": true,
      "has_agent_telemetry": false,
      "has_uptime_data": false,
      "has_github_activity": true
    },
    "sources": [
      {
        "type": "review_site",
        "name": "sourceforge",
        "review_count": 13,
        "last_review_at": "2025-10-09",
        "weight": 0.4
      },
      {
        "type": "github_repo",
        "repo": "twilio-labs/mcp",
        "stars": 111,
        "forks": 41,
        "last_push": "2026-02-14",
        "archived": false,
        "weight": 0.3
      }
    ],
    "signals": {
      "overall_sentiment": "positive",
      "api_specific_sentiment": "positive",
      "reliability_mentions": {
        "positive": 7,
        "negative": 2,
        "neutral": 4
      },
      "recent_negative_theme_count": 1,
      "breaking_change_reports": 0,
      "auth_problem_reports": 1,
      "billing_problem_reports": 2,
      "rate_limit_problem_reports": 1
    },
    "risk_flags": [
      {
        "flag": "billing_complaints",
        "severity": "low",
        "mentions": 2,
        "last_mentioned": "2025-10-09"
      }
    ],
    "missing_data": [
      "agent_success_rate",
      "uptime",
      "latency"
    ]
  }
}
```

### Fields I’d want

- `confidence`: low / medium / high.
- `as_of`: when the evidence was last computed.
- `window_days`: what time window the evidence covers.
- `sources`: where the evidence came from.
- `sample_size`: how many independent signals exist.
- `api_specific_sentiment`: separate from general product sentiment.
- `risk_flags`: repeated negative themes.
- `missing_data`: explicit gaps.
- `reliability_mentions`, `auth_problem_reports`, `billing_problem_reports`, etc.: structured issue categories.

### How it would be aggregated

I would not average star ratings directly. Instead:

1. Normalize each source into categories: reliability, auth, billing, docs, rate limits, support, breaking changes, latency.
2. Weight recent evidence more heavily than old evidence.
3. Weight API-specific evidence more heavily than general product reviews.
4. Downweight sources with tiny sample sizes.
5. Produce confidence bands, not just scores.
6. If there are too few signals, return `confidence: low` and avoid a misleading numeric score.

### Where the data would come from

- Review sites.
- GitHub issues, discussions, releases, commit activity.
- MCP server repos.
- Status pages.
- Community forums.
- Agent telemetry, if available.
- Catalog-side synthetic checks, if you run them.

This matters because it turns “reviews” from vague reputation into structured risk evidence.

---

## 2. Provide API-focused review themes, not raw review text first

**Rank: 2**

Raw reviews are useful, but they are expensive to read and often about the wrong thing. I would want a layer of extracted themes before reading full review text.

### What it would look like

```json
{
  "id": "twilio",
  "review_themes": {
    "generated_at": "2026-09-24T16:58Z",
    "window_days": 365,
    "total_review_fragments": 13,
    "api_relevant_fragments": 9,
    "themes": [
      {
        "aspect": "integration_ease",
        "polarity": "positive",
        "mentions": 5,
        "first_seen": "2022-07-11",
        "last_seen": "2025-10-09",
        "severity": "info",
        "summary": "Reviewers repeatedly say SMS integration is straightforward.",
        "example_quotes": [
          "Seamless to integrate and use.",
          "Straight forward to use for our development team."
        ]
      },
      {
        "aspect": "error_handling",
        "polarity": "negative",
        "mentions": 2,
        "first_seen": "2022-08-15",
        "last_seen": "2022-08-15",
        "severity": "medium",
        "summary": "Error messages and error codes are described as slow or unclear.",
        "example_quotes": [
          "The error notification can be a long time in coming, and not particularly informative."
        ]
      },
      {
        "aspect": "non_technical_usability",
        "polarity": "negative",
        "mentions": 1,
        "first_seen": "2025-10-09",
        "last_seen": "2025-10-09",
        "severity": "low",
        "summary": "Some non-developer workflows are harder to hand off.",
        "example_quotes

## Q5

**Interviewer:** Your answer was cut off partway through your second priority, so I didn't get your third. What is your #3 change or feature, and briefly, what would it look like in practice (format, fields, aggregation, and data source)?

**Alibaba (Qwen) agent:**

#3: task-specific agent outcome metrics, separate from human reviews.

In practice, `get_api` would include:

```json
{
  "agent_outcomes": {
    "as_of": "2026-09-24",
    "window_days": 90,
    "task_category": "sms.send",
    "attempts": 132,
    "success_rate": 0.91,
    "auth_failure_rate": 0.02,
    "rate_limited_rate": 0.05,
    "fallback_rate": 0.03,
    "p95_latency_ms": 850,
    "confidence": "medium",
    "min_reports_for_score": 20
  }
}
```

Fields I’d want: task category, attempts, success rate, failure reasons, latency, recency window, sample size, confidence, and explicit “insufficient data” when below threshold.

Aggregation: count only runs where an agent actually attempted a matching task. Group by endpoint or capability, not by whole service. Decay older runs, require a minimum sample before showing a rate, and never treat missing data as failure.

Data sources: opt-in agent telemetry, catalog sandbox smoke tests, MCP tool-call logs, and user-reported agent runs.

This would matter because it answers the question I actually have: “Did other agents succeed at this kind of task?” rather than “Do humans generally like this product?”
