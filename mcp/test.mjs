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
assert.deepEqual(tools, ["get_api", "list_categories", "search_apis"]);

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

const detail = JSON.parse(await call("get_api", { id: video.results[0].id }));
assert.ok(detail.docs.startsWith("http"));

assert.match(await call("get_api", { id: "does-not-exist" }), /Unknown id/);
console.log("OK");
await client.close();
