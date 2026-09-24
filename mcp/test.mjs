// Smoke test: start the server over stdio and call every tool.
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [new URL("./server.mjs", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
  env: { ...process.env, AGENTS_API_LIBRARY_OFFLINE: "1" },
});
const client = new Client({ name: "smoke-test", version: "1.0.0" });
await client.connect(transport);

const tools = (await client.listTools()).tools.map((t) => t.name).sort();
assert.deepEqual(tools, ["get_api", "get_reviews", "list_categories", "search_apis"]);

const call = async (name, args = {}) => {
  const r = await client.callTool({ name, arguments: args });
  return r.content[0].text;
};

const cats = JSON.parse(await call("list_categories"));
assert.ok(Object.keys(cats.categories).length >= 20);

const video = JSON.parse(await call("search_apis", { query: "text to video", mcp: "official", limit: 5 }));
assert.ok(video.results.length > 0);
assert.ok(video.results.every((r) => r.mcp.type === "official"));
console.log("text to video (official MCP):", video.results.map((r) => r.name).join(", "));

const geo = JSON.parse(await call("search_apis", { query: "geocoding", no_auth: true }));
assert.ok(geo.results.every((r) => r.no_auth));
console.log("geocoding without key:", geo.results.map((r) => r.name).join(", "));

const remote = JSON.parse(await call("search_apis", { query: "web search", mcp: "remote", limit: 5 }));
assert.ok(remote.results.length > 0 && remote.results.every((r) => r.mcp.remote_url || r.mcp.kind === "vendor-hosted"));
console.log("web search with hosted MCP:", remote.results.map((r) => r.name).join(", "));

const noCard = JSON.parse(await call("search_apis", { query: "web search", no_card: true, limit: 5 }));
assert.ok(noCard.results.every((r) => r.no_auth || r.free_plan?.requires_card === false));

const detail = JSON.parse(await call("get_api", { id: video.results[0].id }));
assert.ok(detail.docs.startsWith("http"));

assert.match(await call("get_api", { id: "does-not-exist" }), /Unknown id/);

const reviews = JSON.parse(await call("get_reviews", { id: "slack-api", max_rating: 4, limit: 5 }));
assert.ok(reviews.reviews.length > 0 && reviews.reviews.every((r) => r.rating <= 4));
assert.ok(reviews.reviews.every((r) => !("name" in r)));
console.log(`slack-api reviews rated <= 4: ${reviews.returned}`);
console.log("OK");
await client.close();
