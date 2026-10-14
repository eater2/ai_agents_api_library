// search_apis filters, sorts and summarizes by user reviews (SourceForge), all opt-in.
import { test } from "node:test";
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const ROOT = new URL("../", import.meta.url);

async function call(name, args) {
  const client = new Client({ name: "opinions-test", version: "1.0.0" });
  await client.connect(new StdioClientTransport({
    command: process.execPath,
    args: [new URL("mcp/server.mjs", ROOT).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
    env: { ...process.env, AGENTS_API_LIBRARY_OFFLINE: "1" },
  }));
  const r = await client.callTool({ name, arguments: args });
  await client.close();
  return JSON.parse(r.content[0].text);
}
// "4.7/5 from 97 (sourceforge)" -> [4.7, 97]; "unavailable" -> null
const parse = (s) => { const m = /^([\d.]+)\/5 from (\d+)/.exec(s); return m ? [Number(m[1]), Number(m[2])] : null; };
const QUERY = "project management tasks";

test("min_rating and min_reviews keep only services with enough good reviews", async () => {
  const res = await call("search_apis", { query: QUERY, min_rating: 4.5, min_reviews: 10, limit: 50 });
  assert.ok(res.results.length, "some services pass");
  for (const r of res.results) {
    const p = parse(r.ratings.reviews);
    assert.ok(p && p[0] >= 4.5 && p[1] >= 10, `${r.id}: ${r.ratings.reviews}`);
  }
});

test("sort=rating weights by review count; unrated services go last", async () => {
  const res = await call("search_apis", { query: QUERY, sort: "rating", limit: 50 });
  assert.equal(res.sort, "rating");
  assert.match(res.note, /Sorted by user rating/);
  const w = res.results.map((r) => { const p = parse(r.ratings.reviews); return p ? (p[0] * p[1] + 3.5 * 5) / (p[1] + 5) : -1; });
  for (let i = 1; i < w.length; i++) assert.ok(w[i - 1] >= w[i] - 1e-9, `order broken at ${res.results[i].id}`);
  const fewReviews = res.results.findIndex((r) => (parse(r.ratings.reviews) || [0, 0])[1] < 3);
  if (fewReviews >= 0) assert.ok(fewReviews > 0, "a service with under 3 reviews does not lead");
});

test("sort=reviews puts the most reviewed first", async () => {
  const res = await call("search_apis", { query: QUERY, sort: "reviews", limit: 50 });
  const n = res.results.map((r) => (parse(r.ratings.reviews) || [0, -1])[1]);
  for (let i = 1; i < n.length; i++) assert.ok(n[i - 1] >= n[i], `order broken at ${res.results[i].id}`);
});

test("results with stored review texts carry reviews_summary; default order unchanged", async () => {
  const res = await call("search_apis", { query: QUERY, limit: 50 });
  assert.equal(res.sort, undefined);
  const withSummary = res.results.filter((r) => r.reviews_summary);
  assert.ok(withSummary.length, "at least one summary");
  for (const r of withSummary) {
    const s = r.reviews_summary;
    assert.ok(s.sampled > 0 && Array.isArray(s.praised) && Array.isArray(s.complaints), r.id);
    assert.equal(s.texts, "get_reviews");
  }
  const api = await call("get_api", { id: withSummary[0].id });
  assert.ok(Array.isArray(api.product_reviews.complaints), "get_api product_reviews has the summary");
});

test("a rating filter nobody passes gives an explicit gap", async () => {
  const res = await call("search_apis", { query: "send sms", min_rating: 4.9, min_reviews: 500 });
  assert.equal(res.results.length, 0);
  assert.match(res.message, /min_rating=4\.9/);
});

test("usage: sort=usage orders by monthly SDK downloads; get_api has the usage signals", async () => {
  const res = await call("search_apis", { query: "text to speech", sort: "usage", limit: 20 });
  // "SDK 1.2M downloads/month (...)" -> 1200000
  const dl = (r) => { const m = /SDK ([\d.]+)([kM]?) downloads/.exec(r.ratings.usage); return m ? Number(m[1]) * ({ k: 1e3, M: 1e6 }[m[2]] || 1) : -1; };
  const n = res.results.map(dl);
  assert.ok(n[0] > 0, "the first result has SDK downloads");
  for (let i = 1; i < n.length; i++) assert.ok(n[i] < 0 || n[i - 1] >= n[i] * 0.95, `order broken at ${res.results[i].id}`);
  const filtered = await call("search_apis", { query: "text to speech", min_downloads: 100000, limit: 50 });
  assert.ok(filtered.results.every((r) => dl(r) >= 100000 * 0.95), "min_downloads keeps only popular SDKs");
  const api = await call("get_api", { id: "twilio" });
  assert.ok(api.sdk_downloads.per_month > 0 && api.sdk_downloads.packages.length, "sdk_downloads");
  assert.ok(api.stackoverflow.questions > 0, "stackoverflow");
  assert.ok("app_store" in api, "app_store signal present (may be unavailable)");
});

test("issues: sort=issues orders by issue_health; min_issue_health filters; get_api has github_issues", async () => {
  const res = await call("search_apis", { query: "send sms", sort: "issues", limit: 20 });
  // "sdk twilio/twilio-node: 95% resolved (...), median 4 d to fix, health 81" -> 81
  const h = (r) => { const m = /health (\d+)/.exec(r.ratings.issues); return m ? Number(m[1]) : -1; };
  const n = res.results.map(h);
  assert.ok(n[0] > 0, "the first result has issue stats");
  for (let i = 1; i < n.length; i++) assert.ok(n[i] < 0 || n[i - 1] >= n[i], `order broken at ${res.results[i].id}`);
  const filtered = await call("search_apis", { query: "send sms", min_issue_health: 60, limit: 50 });
  assert.ok(filtered.results.length && filtered.results.every((r) => h(r) >= 60), "min_issue_health keeps only healthy repos");
  const api = await call("get_api", { id: "twilio" });
  const gi = api.github_issues;
  assert.ok(gi.issue_health >= 0 && gi.issue_health <= 100 && gi.repos.length, "github_issues");
  const main = gi.repos.find((r) => r.repo === gi.based_on);
  assert.ok(main && main.resolved_pct === Math.round(100 * main.resolved / (main.resolved + main.open)), "resolved_pct = fixed / (fixed + open)");
});
