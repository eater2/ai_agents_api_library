// Regression test from the 2026-09-24 product test with 7 agents
// (research/agent-interviews/2026-09-24-product-test/report.md): the three tasks where search failed.
// Skipped until catalog entries carry `operations`, which the operation ranking needs.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const ROOT = new URL("../", import.meta.url);
const catalog = JSON.parse(await readFile(new URL("catalog/all.json", ROOT), "utf8"));
const skip = catalog.some((e) => e.operations?.length) ? false : "catalog entries have no `operations` yet";

async function search(args) {
  const client = new Client({ name: "search-test", version: "1.0.0" });
  await client.connect(new StdioClientTransport({
    command: process.execPath,
    args: [new URL("mcp/server.mjs", ROOT).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
    env: { ...process.env, AGENTS_API_LIBRARY_OFFLINE: "1" },
  }));
  const r = await client.callTool({ name: "search_apis", arguments: args });
  await client.close();
  return JSON.parse(r.content[0].text);
}
const names = (res, n) => res.results.slice(0, n).map((r) => r.name);
const has = (list, re) => list.some((x) => re.test(x));

test("task 1: text-to-video returns generators only, or an explicit gap", { skip }, async () => {
  for (const args of [{ query: "generate video from text prompt" }, { query: "generate video from text prompt", free_tier: true }]) {
    const res = await search(args);
    const top = names(res, 5);
    assert.ok(!has(top, /voyage|mux|gemini api$|akool|creatomate/i), `${JSON.stringify(args)}: noise in ${top}`);
    if (res.results.length) {
      assert.ok(res.results.every((r) => r.match === "exact"), `${JSON.stringify(args)}: non-exact results ${top}`);
    } else {
      assert.match(res.message, /no catalogued service/i);
      assert.ok(res.hint, "empty result carries a hint");
    }
  }
});

test("task 2: geocoding 200 street addresses", { skip }, async () => {
  const res = await search({ query: "geocode 200 street addresses in Poland" });
  const top = names(res, 5);
  assert.ok(has(top, /geoapify|mapbox|here/i), `expected Geoapify/Mapbox/HERE in ${top}`);
  assert.ok(!has(top, /ip2location/i), `IP geolocation in street geocoding results: ${top}`);
  const nominatim = res.results.findIndex((r) => /nominatim/i.test(r.name));
  if (nominatim >= 0) {
    assert.ok(res.results[nominatim].volume_warning, "Nominatim flagged for bulk use");
    assert.ok(nominatim >= 3, `Nominatim ranked ${nominatim + 1} for a bulk job`);
  }
});

test("task 3: SMS reminder", { skip }, async () => {
  const res = await search({ query: "send an SMS reminder" });
  const top3 = names(res, 3);
  assert.ok(has(top3, /twilio/i) || has(top3, /vonage/i), `expected Twilio or Vonage in top 3: ${top3}`);
  const top5 = names(res, 5);
  assert.ok(!has(top5, /line messaging|discord|whatsapp/i), `chat apps in SMS results: ${top5}`);
});
