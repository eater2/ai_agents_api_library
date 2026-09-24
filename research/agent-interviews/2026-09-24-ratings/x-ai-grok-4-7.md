# Ratings and reviews: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Picture a typical task where you have two or three candidate services from our catalog that could all do the job. Each listing includes a ratings-and-reviews section: an average star rating, a review count, and a few short written reviews with dates. Walk me through how you would choose between them. At which step, if any, would you look at that section, and can you think of a situation where it would change which service you pick?

**xAI agent:**

I would not look at the ratings-and-reviews section while choosing. I rank candidates by whether the documented endpoints, auth, and response shape actually fit the task, then by constraints I can check: rate limits, pricing, error behavior, and a live call if I can make one. Average stars and review count are the wrong signal: small samples, buyer-audience reviews, and GitHub stars on a related repo do not tell me if the API will return what I need.

I would open written reviews only after two or three services were otherwise tied, and only to scan for a concrete failure mode that matches this task—opaque errors, silent delivery failure, a breaking change. A 4.8 from 13 SourceForge reviews would not move me. A specific, dated complaint that I cannot disprove with a test might, if the alternative has no such report and I cannot call both. Empty coverage, as with Geoapify, changes nothing. In the usual case the section does not change the pick.

## Q2

**Interviewer:** Setting aside how you pick a single service: does having a ratings-and-reviews section in listings change how much you trust the catalog as a whole, or does it only bear on the individual service, if at all? Among these signals, which would carry weight for you, and which would you ignore: star rating, review count, review dates, GitHub stars or recent activity on the MCP repo, MCP install counts, measured uptime, and reported task success from other agents?

**xAI agent:**

A ratings section does not raise my trust in the catalog. I trust it if search and get_api match the live API. Half-covered stars from SourceForge or a related repo are not that evidence. They bear only on the listing, and weakly. Thin or mismatched ratings can make a listing look less carefully kept; they do not make me downgrade the catalog.

Measured uptime carries weight if it is probe data with a window and endpoint, not a badge. Reported task success from other agents carries weight if the task, success rule, sample size, and date are stated. That is the only social signal close to my job. Review dates matter only as context for a concrete failure I am already reading; a 2022 complaint is stale unless I can still reproduce it. GitHub stars and recent pushes are faint liveness of the MCP wrapper, not of the service. Star rating, review count, and MCP install counts I ignore: wrong audience, small or opaque samples, easy to misread as quality.

None of the ignored signals would change a call I was about to make.

## Q3

**Interviewer:** You've already named small samples, reviews aimed at human buyers, and stale dates as problems. Thinking about the ratings and reviews you'd actually encounter in a catalog, what else counts as noise or risk for you? For example, consider fake or incentivized reviews, the token cost of reading review text, or uneven coverage across listings. Of everything you'd put on that list, which one causes you the most harm in practice, and why?

**xAI agent:**

The extra noise is reviews that sound like operational evidence and are not. Incentivized or vendor-shaped writeups use concrete words—error codes, delivery failures, “reliable”—that pass a specificity filter. Many describe the dashboard, billing, or a non-dev handoff, not the API contract. Uneven coverage is a bias trap: a 4.8 next to a null listing looks like a verdict. Pulling up to 100 review texts also burns context for almost no decision value. Stars on an MCP wrapper are a rating of the wrong artifact.

The one that harms me most is the specific-sounding, off-target or incentivized review. I already ignore averages and counts, and I can skip get_reviews, so token cost and missing coverage do not reach the choice unless I treat absence as a score—which I do not. The residual path is a tie, where I might read a few cons. A plausible paragraph about errors can flip the pick, and the text alone cannot tell marketing from a real API defect. Only a live call can.

## Q4

**Interviewer:** If you could shape how ratings and reviews appear in the catalog for agents like you, what would you want? Please rank your top three changes or features, covering any of format, fields, aggregation, and sources, and for each one say briefly what decision it would help you make.

**xAI agent:**

1. Replace star averages with a task-success table: task, success rule, sample size, date, endpoint, error class, source. That is the only social signal that can break a tie between two APIs whose docs both fit.

2. Put probe results in their own fields, not in a ratings array next to GitHub stars: method, endpoint, window, error rate, measured_at. I would use that to drop a candidate that is failing the call I am about to make, without reading reviews.

3. Do not inline buyer prose. If a defect record exists, keep it structured: failure mode, date, audience (API vs dashboard), and an incentivized flag. Omit the paragraph. That stops a specific-sounding marketing cons list from flipping a pick I should have settled with a live call.

I would not add install counts, mean stars, or review counts. Empty coverage should stay empty, not render as zero.

## Q5

**Interviewer:** You named incentivized, specific-sounding reviews as the biggest risk, yet your top request is task-success reports from other agents, which could be gamed or off-target in similar ways. What would a task-success record need to show about its source or collection before you would let it break a tie, and what would make you disregard it?

**xAI agent:**

A task-success record can break a tie only if I could have produced it myself and did not. It needs a named runner that is not the vendor, the exact task and success predicate, the endpoint and API version, n, the failure counts by error class, and measured_at. The method has to be re-runnable: same request shape, same pass/fail rule, not a score the submitter defined after the fact. Catalog-operated probes with a public method clear that bar. Anonymous “other agents succeeded” does not.

I disregard it if the vendor or an incentivized party submitted it, if the task is adjacent but not mine, if n, date, endpoint, or the predicate is missing, or if it is a single run dressed up as a rate. I also drop it when it is older than a version change I can see, or when it disagrees with a call I just made. A live response beats any record. Without those fields, a task-success table is the same risk as a specific-sounding review: plausible text, wrong evidence, and a flip I cannot audit.
