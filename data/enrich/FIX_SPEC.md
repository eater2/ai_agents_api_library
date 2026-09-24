# Fix spec: turn research corrections into field patches

Input: `data/enrich/<batch>.json`. Each entry may have a `corrections` list: text notes by the research
agent saying an existing field of `data/catalog.json` is wrong, with the vendor page it found.

Output: `data/enrich/fix_<batch>.json`, an object keyed by entry id:

```json
{
  "twilio": {
    "free_tier": "Trial: 100 SMS, 100 WhatsApp, 3,000 emails, 75 voice minutes; no card; expires after 30 days",
    "mcp": {"type": "official", "url": "https://mcp.twilio.com/docs"},
    "notes": "…",
    "sources": ["https://www.twilio.com/en-us/pricing", "https://www.twilio.com/docs/mcp"]
  }
}
```

Patchable fields, all in English, in the same style and length as the current values in `data/catalog.json`:
`docs`, `homepage`, `auth` (one of api_key | oauth2 | api_key+oauth2 | none | cloud_iam), `auth_hint`,
`mcp` (whole object: `type` official | community | none, `url` = hosted endpoint if one exists, else repo/docs of the server),
`free_tier`, `openapi`, `llms_txt`, `notes`, `desc_en`. Do not touch `desc_pl`, `id`, `name`, `category`.
`free_plan_kind` (free_tier | trial | none) corrects the researched `free_plan.kind` when the vendor page contradicts it.

Rules:
- Before patching, open the source page the correction cites (or the vendor's page) and confirm it. Skip a correction you cannot confirm.
- Only change what the correction is about. Keep existing wording otherwise.
- `free_tier` must start with how it works ("Free tier: …", "Free: …", "Trial: …", "Paid only …", "No key needed …"),
  because scripts classify it: lasting free quotas say per day/month; one-off credits say "one-time" or "on signup".
- When `mcp.type` changes to official, the MCP server must be published by the vendor (vendor domain or the vendor's GitHub org).
- `notes` may be extended with one short sentence (e.g. a deprecation date); keep it under ~300 characters.
- `sources`: the URLs you confirmed (kept for the record, not merged into the catalog).
- Valid JSON, no comments. Write the file; do not edit any other file; no git commands.
