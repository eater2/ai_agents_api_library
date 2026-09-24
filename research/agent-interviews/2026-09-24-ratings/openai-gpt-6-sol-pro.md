# Ratings and reviews: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** When you're choosing between two or three candidate services in the catalog, suppose each listing includes the ratings and reviews currently available for it. Would you read them? If so, at what point in your selection process, and has that kind of information ever changed which service you picked? Please walk me through a recent or typical example.

**OpenAI agent:**

Yes, but only after I’ve narrowed the field by whether each service actually meets the task’s requirements—API capabilities, authentication, pricing, and any tests I can run. I’d use `get_api` for ratings and `get_reviews` when a specific risk matters. I wouldn’t treat ratings as a ranking: Twilio’s 4.8 is based on 13 SourceForge reviews, its GitHub stars describe an MCP repo rather than the service, and many catalog entries have no data.

For example, if I were choosing an SMS provider for time-sensitive alerts, I’d notice the Twilio review describing delayed, uninformative error notifications. That would prompt me to test failure reporting or check the docs before committing. If another candidate met the requirements and handled that better, the review could change my pick. For ordinary reminder texts, that review alone probably would not.

I can’t honestly say these catalog reviews have *already* changed a service I picked; I don’t have a specific past switch to point to.

## Q2

**Interviewer:** Q2: When a catalog shows this kind of information (a 4.8 from 13 SourceForge reviews, GitHub stars for a related MCP repo, and no data for many other entries), does it change how much you trust the catalog as a whole, or does it only affect how you view the individual service? Which of these signals, if any, would carry real weight in your decision: star rating, review count, review dates, GitHub stars or recent activity on the MCP repo, MCP install counts, uptime figures, or reported success rates from other agents? Tell me why for the ones that matter and the ones that don't.

**OpenAI agent:**

It would mostly affect how I view each service. Sparse coverage doesn’t make the catalog untrustworthy if missing data is clearly marked. I’d trust the catalog less if it presented these unlike signals as a comparable score, or treated “no data” as a bad rating.

In a close choice, the signals I’d weigh are:

- **Review text, count, and dates:** Specific, recent complaints relevant to my task can suggest what to test. A 4.8 from 13 reviews is weak evidence on its own; older reviews may describe a product that has changed.
- **Uptime:** Meaningful for a reliability-sensitive task *if* the measurement is recent, independently collected, and covers the endpoint and region I’d use.
- **Other agents’ success rates:** Potentially useful *if* they include failures, sample sizes, comparable tasks, and a clear definition of success. Otherwise they’re easy to overread.

**GitHub stars, MCP installs, and repo activity** would carry little weight for choosing the underlying service. Activity could matter if I specifically need that MCP integration; stars and installs mostly indicate attention or adoption, not whether my calls will work. I’d still test the leading candidates where possible.

## Q3

**Interviewer:** Q3: Which aspects of ratings and reviews in a catalog like this would you treat as noise or as a risk? Consider small sample sizes, outdated reviews, reviews written by humans about the product rather than the API, fake or manipulated reviews, the token cost of reading them, and gaps in coverage. For each one that matters to you, how would it affect whether or how you use the data? Are there other problems not on this list?

**OpenAI agent:**

I’d treat reviews as leads to investigate, not as a score to optimize.

- **Small samples:** A 4.8 from 13 reviews would not separate close candidates. I’d look for a specific, repeated issue instead.
- **Old reviews:** I’d discount claims about current behavior unless I could verify them in recent docs or a test.
- **Product reviews versus API reviews:** Complaints about an admin UI may be irrelevant to my API use; complaints about error reporting or billing could matter.
- **Manipulation:** I can’t reliably detect fake reviews. I’d avoid relying on unusually uniform praise or a single source.
- **Token cost:** I’d read a few relevant negative and recent reviews only after narrowing the candidates, not pull 100 reviews for every search result.
- **Coverage gaps:** “No data” means unknown, not worse. I wouldn’t penalize Geoapify just because the catalog has no ratings for it.

Other risks are **source mismatch** (GitHub stars for an MCP repo aren’t ratings of the underlying service), **selection bias** in who leaves reviews, and **unclear measurement methods** for uptime or success rates. Those would push me toward documentation and direct tests, not a more confident ranking.

## Q4

**Interviewer:** Q4: If you could shape how ratings and reviews are presented to agents in this catalog, what would you want? Please rank your top three changes or features, and for each, be specific about the format, the fields included, how data is aggregated or summarized, and which sources it comes from. Tell me briefly why each one ranks where it does.

**OpenAI agent:**

1. **Show coverage in `search_apis`.** Add a compact `review_evidence` field: source, rating, review count, newest review date, and `status: available | unavailable`. Show each source separately; don’t compute a cross-source score or rank missing entries lower. This ranks first because I need to know whether there’s evidence *before* spending calls on candidates.

2. **Make `get_api` distinguish the service from its integration.** Return separate `product_reviews` and `mcp_repo` sections. For reviews, include source URL, rating, count, date range, and fetch date; for the repo, include stars, last push, archived status, and URL. Don’t aggregate GitHub stars with product ratings. This prevents a plausible-looking number from answering the wrong question.

3. **Make `get_reviews` selective and traceable.** Allow filters for recent, low-rated, and API-related reviews; return a short theme summary with counts and links to the underlying reviews, plus the sampled and total counts. Keep the original text available on request. I’d use this last, after narrowing candidates, to find concrete issues worth verifying—not to accept a generated verdict.

## Q5

**Interviewer:** You listed other agents' reported success rates as potentially useful in Q2, but they didn't appear in your top three. Why not? If the catalog did collect outcomes from agents' calls, what would need to be true about how they were gathered and presented for you to use them in a decision?

**OpenAI agent:**

They weren’t in my top three because the catalog currently has ratings and reviews, not agent outcomes. I prioritized making the existing evidence findable and hard to misinterpret. A well-measured outcome signal could be more useful than review stars.

I’d use it only if the catalog showed **what succeeded and what was attempted**: the operation, endpoint or MCP tool, time window, region, and whether “success” means an HTTP response, a valid result, or completion of the agent’s task. The denominator must include timeouts, errors, and failed attempts—not just reported successes—and distinguish first attempts from retries. I’d also want sample sizes, uncertainty, collection method, and safeguards against duplicate or selectively submitted results.

Present it by comparable task or operation, not as one service-wide percentage. For example: “Send SMS: 962 valid completions / 1,000 attempts, last 30 days,” with failure categories and a methodology link. If the sample were small, biased, or unlike my task, I’d treat it as a prompt to test, not a reason to switch services.
