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
      // exact needs evidence (example call or MCP tool); listed = operation claimed without it, never adjacent noise.
      assert.ok(res.results.every((r) => ["exact", "listed"].includes(r.match)), `${JSON.stringify(args)}: adjacent results ${top}`);
      const firstListed = res.results.findIndex((r) => r.match === "listed");
      if (firstListed >= 0) assert.ok(res.results.slice(firstListed).every((r) => r.match === "listed" || r.volume_warning), "exact ranks above listed");
    } else {
      assert.match(res.message, /no catalogued service/i);
      assert.ok(res.hint, "empty result carries a hint");
    }
  }
});

test("task 2: geocoding 200 street addresses", { skip }, async () => {
  const res = await search({ query: "geocode 200 street addresses in Poland" });
  const top = names(res, 5);
  // GUGiK is the official Polish geocoder (added after the retest), so it counts as a right answer too.
  assert.ok(has(top, /geoapify|mapbox|here|gugik/i), `expected Geoapify/Mapbox/HERE/GUGiK in ${top}`);
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
  // Any dedicated SMS provider counts; the catalog has several since the product test.
  const smsProviders = /twilio|vonage|plivo|sinch|telnyx|aws end user messaging|bird|textbelt/i;
  assert.ok(top3.every((n) => smsProviders.test(n)), `expected only SMS providers in top 3: ${top3}`);
  const top5 = names(res, 5);
  assert.ok(!has(top5, /line messaging|discord|whatsapp/i), `chat apps in SMS results: ${top5}`);
});

test("direction and verb forms: transcribe, text to speech, translate", { skip }, async () => {
  const stt = await search({ query: "transcribe audio recording" });
  assert.ok(stt.results.slice(0, 5).every((r) => r.match === "exact" && /speech-to-text/.test(r.reason)), `transcribe: ${names(stt, 5)}`);
  const tts = await search({ query: "turn text to speech" });
  assert.ok(tts.results.slice(0, 5).every((r) => /text-to-speech/.test(r.reason)), `tts: ${tts.results.slice(0, 5).map((r) => r.reason)}`);
  const tr = await search({ query: "translate text" });
  assert.ok(names(tr, 3).every((n) => /translat|deepl/i.test(n)), `translate: ${names(tr, 3)}`);
});

test("evidence: example call for another operation is not exact; docs-only MCP flagged", { skip }, async () => {
  const video = await search({ query: "generate video from text prompt", limit: 30 });
  const freepik = video.results.find((r) => /freepik/i.test(r.name));
  if (freepik) assert.equal(freepik.match, "listed", "Freepik's example call is image-to-video");
  const sms = await search({ query: "send sms", limit: 30 });
  const twilio = sms.results.find((r) => /^twilio$/i.test(r.name));
  assert.match(twilio.mcp_fit, /docs-only/);
  const aws = sms.results.findIndex((r) => /end user messaging/i.test(r.name));
  assert.ok(aws === -1 || aws >= 3, `cloud IAM SMS ranked ${aws + 1}`);
});
