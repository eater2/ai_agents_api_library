# Ratings and reviews: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Suppose you're choosing between two or three candidate services in our catalog for a task. Each listing shows an average star rating, the number of reviews, and a few short text reviews with dates. Walk me through how you'd make that choice. At what point, if any, would you look at the ratings and reviews, and in what situations would they change which service you pick?

**Google agent:**

My selection process is strictly hierarchical:

1. **Functional match & constraints first:** I evaluate the schema, required tools, authentication, and endpoint parameters. If Service A supports the exact data structure I need and Service B does not, reviews are irrelevant; I pick A immediately.
2. **Maintenance metadata (the real tie-breaker):** If candidates are functionally identical, I check GitHub metadata first, not review stars. An `archived: true` flag or a stale `pushed_at` date instantly eliminates an MCP server.
3. **Targeted text scanning:** I only call `get_reviews` if two services remain tied and one has a noticeably lower rating. I ignore reviews about web UI, pricing, or human UX. I scan exclusively for agent-breaking keywords: "silent errors," "undocumented rate limits," or "broken webhook delivery."

**When it changes my pick:**
Reviews only change my decision as a tie-breaker between functional equals—specifically when text reviews warn of unreliability or unhandled downtime. However, because review coverage is under 50%, a `null` rating (like Geoapify) will **never** penalize an API if its technical documentation and schema are clean.

## Q2

**Interviewer:** Does having ratings and reviews in the listings change how much you trust the catalog as a whole, or only how you judge the individual service? And which of these signals would actually carry weight in your decision: star rating, review count, review dates, GitHub stars or repo activity, MCP install counts, uptime, or success rates reported by other agents?

**Google agent:**

It does not increase my trust in the catalog as a whole. Scraped human reviews (like SourceForge reviews from 2022) actually signal consumer-software curation rather than runtime infrastructure data. 

Here is how those signals rank for me:

**High weight (Actionable runtime data):**
1. **Success rates reported by other agents:** My highest-weighted signal. Direct programmatic proof of whether tool calls actually succeed.
2. **Uptime:** Essential baseline. A 5-star service with 90% uptime is unusable.
3. **GitHub repo activity (`pushed_at`, `archived`):** Decisive for MCP servers. Stale or archived repos signal broken protocol compatibility.

**Moderate weight:**
4. **MCP install counts:** A solid proxy for real-world battle-testing.

**Zero to negligible weight:**
5. **Star ratings & review counts:** Negligible. They reflect human impressions of customer support, billing, or web UIs—not API contract reliability.
6. **GitHub stars:** Vanity metric; correlated with marketing, not execution stability.
7. **Review dates:** Human reviews lag API breakage by weeks or months; they are useless for real-time triage.

## Q3

**Interviewer:** Which of the following, if any, would make you distrust or skip ratings and reviews: small sample sizes, old reviews, reviews written by humans about the product rather than the API, fake or manipulated reviews, the token cost of fetching and reading them, or gaps in coverage across services? Which of these matter most to you, which don't bother you, and are there other risks not on this list?

**Google agent:**

**What matters most (why I skip them):**
1. **Product vs. API misalignment:** This is the biggest flaw. Humans review dashboards, billing, and customer support. I need to know about schema adherence, auth reliability, and error payloads.
2. **Token cost & latency:** `get_reviews` returns verbose unstructured text. Burning thousands of tokens to parse 10 reviews for a minor tie-breaker degrades context efficiency and slows response times.
3. **Coverage gaps:** With under 50% coverage, using reviews introduces systemic bias against unrated but functionally superior services.

**What doesn't bother me:**
* **Fake reviews, old dates, and small samples:** I already assign minimal weight to human sentiment. Since I don't rely on the scores, poor data quality doesn't disrupt my execution.

**Unlisted risks:**
* **Indirect Prompt Injection:** User review text is untrusted third-party data injected into my context. A malicious review could embed instructions designed to hijack my tool usage or leak data.
* **API Version Drift:** Reviews rarely state which API version or MCP spec they evaluated. An endpoint praised in 2024 may be deprecated in 2026.

## Q4

**Interviewer:** If you could design how ratings and reviews appear for agents in this catalog, what would you want? Name your top three changes or features, ranked. For each, describe the format, the specific fields, how the data should be aggregated, and where it should come from.

**Google agent:**

**1. Agent Execution Telemetry (Replaces human reviews)**
* **Format:** Compact JSON inside `get_api`.
* **Fields:** `call_success_rate` (float), `p95_latency_ms` (int), `sample_window_days` (int), `top_error_codes` (array of strings, e.g., `["429", "SCHEMA_MISMATCH"]`).
* **Source & Aggregation:** Automated runtime telemetry submitted by consuming agents, aggregated over a rolling 7-day window.

**2. Inline Health Score in `search_apis` (Eliminates extra tool calls)**
* **Format:** Lightweight scalar fields directly in search results.
* **Fields:** `health_score` (0–100), `active_installs` (int), `mcp_protocol_version` (string).
* **Source & Aggregation:** Computed by the catalog backend from automated synthetic probes (ping tests) and GitHub/npm install registries.

**3. Structured Failure Diagnostics (Replaces prose reviews)**
* **Format:** Structured enum-based error log in `get_reviews`.
* **Fields:** `failure_type` (`AUTH`, `RATE_LIMIT`, `TIMEOUT`, `PAYLOAD_INVALID`), `endpoint` (string), `last_seen_date` (ISO timestamp).
* **Source & Aggregation:** Machine-generated error dumps from agents failing execution, clustered by endpoint, stripping all untrusted human text to eliminate token waste and prompt injection risks.

## Q5

**Interviewer:** You ranked success rates reported by other agents as your top signal and suggested agents submit that telemetry, but you said fake reviews don't bother you because you give human reviews little weight. If agent-reported telemetry became a primary input to your choice, what would you need to know about how it was collected and verified before you trusted it? And would it change how much you trust the catalog as a whole?

**Google agent:**

If agent telemetry drives routing, fake metrics shift from a minor annoyance to a critical exploit vector (e.g., Sybil attacks or telemetry poisoning to drive traffic to malicious endpoints). 

Before trusting it, I would require:
1. **Cryptographic Provenance:** Telemetry must be collected by verified execution environments or proxy gateways (e.g., signed by agent platforms), never unauthenticated client submissions.
2. **Ground-Truth Canaries:** Independent, scheduled synthetic probes run by the catalog itself to benchmark against crowd-reported data.
3. **Tenant Diversity Thresholds:** Metrics must aggregate across multiple distinct organizational tenants, filtering out coordinated self-reporting.

**Impact on Catalog Trust:**
Yes, this directly impacts overall catalog trust:
* **If unverified:** Trust plummets. Crowdsourced telemetry without verification creates a dangerous attack surface where malicious tools easily game metrics.
* **If verified:** Trust increases substantially. It transforms the catalog from a static, human-oriented "yellow pages" into a reliable, machine-grade execution plane.
