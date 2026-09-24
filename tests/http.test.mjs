// Remote MCP endpoint (api/mcp.mjs). By default runs the Vercel handler on a local port
// with a minimal shim for Vercel's req.body / res.status / res.json helpers.
// MCP_URL=https://ai-agents-api-library.vercel.app/mcp tests the deployed endpoint instead.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

let url = process.env.MCP_URL;
let http;

before(async () => {
  if (url) return;
  process.env.AGENTS_API_LIBRARY_OFFLINE = "1";
  const { default: handler } = await import("../api/mcp.mjs");
  http = createServer(async (req, res) => {
    let raw = "";
    for await (const chunk of req) raw += chunk;
    req.body = raw ? JSON.parse(raw) : undefined;
    res.status = (code) => { res.statusCode = code; return res; };
    res.json = (obj) => { res.setHeader("Content-Type", "application/json"); res.end(JSON.stringify(obj)); return res; };
    await handler(req, res);
  });
  await new Promise((ok) => http.listen(0, "127.0.0.1", ok));
  url = `http://127.0.0.1:${http.address().port}/mcp`;
});
after(() => http?.close());

test("MCP client: list tools and call each one", async () => {
  const client = new Client({ name: "http-test", version: "1.0.0" });
  await client.connect(new StreamableHTTPClientTransport(new URL(url)));
  try {
    const tools = (await client.listTools()).tools.map((t) => t.name).sort();
    assert.deepEqual(tools, ["get_api", "get_reviews", "list_categories", "search_apis"]);

    const text = async (name, args = {}) => (await client.callTool({ name, arguments: args })).content[0].text;
    assert.ok(Object.keys(JSON.parse(await text("list_categories")).categories).length >= 20);
    const found = JSON.parse(await text("search_apis", { query: "send email", limit: 3 }));
    assert.ok(found.results.length > 0);
    assert.ok(JSON.parse(await text("get_api", { id: found.results[0].id })).docs.startsWith("https://"));
    assert.ok(JSON.parse(await text("get_reviews", { id: "slack-api", limit: 1 })).reviews.length === 1);
  } finally {
    await client.close();
  }
});

test("CORS preflight and non-POST methods", async () => {
  const pre = await fetch(url, { method: "OPTIONS" });
  assert.equal(pre.status, 204);
  assert.equal(pre.headers.get("access-control-allow-origin"), "*");
  const get = await fetch(url);
  assert.equal(get.status, 405);
  assert.equal((await get.json()).jsonrpc, "2.0");
});
