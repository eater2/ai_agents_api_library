# Enrichment spec: structured fields for catalog entries

Agents researching entries write one JSON file `data/enrich/<batch>.json`: an object keyed by entry `id`.
`scripts/merge_enrich.py` merges it into `data/catalog.json`. Do not edit any other file.

## Rules

- Use only the vendor's own pages: docs, pricing page, API reference, OpenAPI spec, official GitHub org,
  terms or privacy/data-usage pages. No blogs, no aggregators, no memory.
- Every non-null value must be backed by a `source_url` you actually opened today.
- If you cannot confirm a value, use `null`. A wrong value is worse than a missing one.
- If you find that an existing field in the entry is wrong (auth, free_tier, mcp, docs), report it in `corrections`.
- Keep strings short and factual (under ~160 chars). English only.

## Record per entry

```json
{
  "free_plan": {
    "kind": "free_tier | trial | no_key | none",   // free_tier = lasting free quota; trial = one-off credits or time-limited; no_key = usable without any account
    "requires_card": true | false | null,           // card needed to get the free quota
    "quota": "1,000 searches" | null,               // amount per period, as the vendor states it
    "period": "day | month | year | one_time | null",
    "watermark": true | false | null,               // only for media generation (image/video/audio/3D/slides): free output watermarked?
    "source_url": "https://vendor.com/pricing",
    "checked_at": "2026-09-24"
  },
  "auth_scheme": {
    "type": "apiKey | http | oauth2 | none | cloud_iam",   // OpenAPI securitySchemes types; cloud_iam for AWS SigV4 / GCP / Azure AD
    "in": "header | query | cookie | null",                // for apiKey
    "name": "x-api-key" | null,                            // header or query parameter name for apiKey
    "scheme": "bearer | basic | null",                     // for http
    "format": "Authorization: Bearer <API_KEY>",           // literal example of what goes on the wire
    "source_url": "https://docs.vendor.com/authentication",
    "checked_at": "2026-09-24"
  },
  "base_url": "https://api.vendor.com/v1" | null,
  "rate_limits": { "summary": "60 requests/min on free plan" , "source_url": "...", "checked_at": "2026-09-24" } | null,
  "oauth_scopes": { "scopes": ["read", "write"], "source_url": "...", "checked_at": "2026-09-24" } | null,   // only when auth uses OAuth; the scopes an agent typically needs
  "async_jobs": { "value": true | false, "how": "poll GET /jobs/{id} or webhook", "source_url": "..." } | null,  // long-running work returns a job id instead of the result
  "data_policy": { "summary": "API inputs not used for training; deleted after 30 days", "source_url": "...", "checked_at": "2026-09-24" } | null,
  "mcp": {
    "maintainer": "vendor | community | none",     // who publishes the MCP server (vendor = the API's company or its official GitHub org)
    "remote_url": "https://mcp.vendor.com/mcp" | null,   // hosted endpoint (Streamable HTTP / SSE), if any
    "repo": "https://github.com/vendor/vendor-mcp" | null, // source or package of a local (stdio) server, if any
    "tools": ["search", "get_contents"] | null,    // tool names the server exposes, from its README/docs
    "covers_full_api": true | false | null,        // does the MCP server cover (almost) all of the REST API?
    "source_url": "...",
    "checked_at": "2026-09-24"
  },
  "corrections": [ "free_tier: pricing page now says 500 searches/month, not 1,000" ]   // optional
}
```

For entries whose `auth` is `none`, set `auth_scheme.type` to `none` and `free_plan.kind` to `no_key`.
For entries without an MCP server, set `mcp` to `{ "maintainer": "none", "remote_url": null, "repo": null, "tools": null, "covers_full_api": null, "source_url": null, "checked_at": "<today>" }` unless you find one (then report it).
