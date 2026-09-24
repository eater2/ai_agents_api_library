#!/usr/bin/env node
// MCP server for the AI Agents API Library: lets an agent find third-party APIs and
// MCP servers it can use, with auth method, free tier, MCP endpoint and docs link.
//
// Data: the bundled catalog/all.json, refreshed at startup from GitHub unless
// AGENTS_API_LIBRARY_OFFLINE=1 is set.
import { readFile } from "node:fs/promises";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const RAW = "https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/all.json";
const BUNDLED = new URL("../catalog/all.json", import.meta.url);

let catalog = JSON.parse(await readFile(BUNDLED, "utf8"));
let source = "bundled";

async function refresh() {
  if (process.env.AGENTS_API_LIBRARY_OFFLINE === "1") return;
  try {
    const res = await fetch(RAW, { signal: AbortSignal.timeout(8000) });
    if (res.ok) {
      const fresh = await res.json();
      if (Array.isArray(fresh) && fresh.length) {
        catalog = fresh;
        source = "github";
      }
    }
  } catch {
    // keep the bundled copy
  }
}

const STOP = new Set(["a", "an", "the", "to", "of", "for", "and", "or", "in", "on", "with", "via", "from", "api", "apis", "i", "my", "need", "want"]);
const words = (s) => (s || "").toLowerCase().split(/[^a-z0-9+#]+/).filter((w) => w.length > 1 && !STOP.has(w));

// Crude English stemming so "geocoding" matches "geocode", "videos" matches "video".
const stem = (w) => (w.length > 4 ? w.replace(/(ings?|ers?|ed|es|s|e)$/, "") : w);
const stems = (s) => new Set(words(s).map(stem));

// Per-entry stem sets plus inverse document frequency, so rare terms ("3d", "sms")
// outweigh common ones ("image", "send").
let index = new Map();
let idf = new Map();
function buildIndex() {
  index = new Map(catalog.map((e) => [e.id, {
    name: stems(`${e.name} ${e.id}`),
    cat: stems(e.category.replace(/-/g, " ")),
    desc: stems(`${e.desc_en} ${e.notes || ""}`),
  }]));
  const df = new Map();
  for (const x of index.values()) for (const t of new Set([...x.name, ...x.cat, ...x.desc])) df.set(t, (df.get(t) || 0) + 1);
  idf = new Map([...df].map(([t, n]) => [t, Math.log(1 + catalog.length / n)]));
}

function score(e, terms) {
  if (!terms.length) return 1;
  const x = index.get(e.id);
  let s = 0;
  for (const t of terms.map(stem)) {
    const w = idf.get(t) || 0;
    if (x.name.has(t)) s += 5 * w;
    if (x.cat.has(t)) s += 3 * w;
    if (x.desc.has(t)) s += 2 * w;
  }
  return s;
}

const summary = (e) => ({
  id: e.id,
  name: e.name,
  category: e.category,
  what: e.desc_en,
  auth: e.auth,
  no_auth: e.no_auth,
  mcp: e.mcp,
  free_tier: e.free_tier,
  docs: e.docs,
});

const server = new McpServer(
  { name: "ai-agents-api-library", version: "0.1.0" },
  {
    instructions:
      "Catalog of verified third-party APIs and MCP servers an agent can call after a one-time human setup " +
      "(API key, OAuth or MCP connection). Use search_apis when the user needs a capability you do not have " +
      "(e.g. generate video, geocode, send SMS), then get_api for auth details. Always confirm pricing and limits " +
      "in the vendor docs; ask the user to configure credentials through their platform's secret store.",
  },
);

server.registerTool(
  "list_categories",
  {
    title: "List API categories",
    description: "List all categories in the catalog with the number of services in each.",
    inputSchema: {},
  },
  async () => {
    const counts = {};
    for (const e of catalog) counts[e.category] = (counts[e.category] || 0) + 1;
    return { content: [{ type: "text", text: JSON.stringify({ source, categories: counts }, null, 1) }] };
  },
);

server.registerTool(
  "search_apis",
  {
    title: "Search APIs and MCP servers",
    description:
      "Search a verified catalog of 300+ third-party APIs and MCP servers for AI agents, with auth method, " +
      "free tier, MCP endpoint and docs link. Use when a task needs an external capability you don't have.",
    inputSchema: {
      query: z.string().optional().describe("What you need, e.g. 'text to video', 'geocoding', 'send sms'"),
      category: z.string().optional().describe("Category id from list_categories, e.g. 'video-generation'"),
      mcp: z.enum(["official", "any"]).optional().describe("Only services with an official MCP server, or any MCP server"),
      no_auth: z.boolean().optional().describe("Only services usable without any key"),
      free_tier: z.boolean().optional().describe("Only services with a free tier or free usage"),
      auth: z.enum(["api_key", "oauth2", "api_key+oauth2", "none", "cloud_iam"]).optional(),
      limit: z.number().int().min(1).max(50).optional().describe("Max results, default 10"),
    },
  },
  async ({ query, category, mcp, no_auth, free_tier, auth, limit = 10 }) => {
    const terms = words(query);
    const hits = catalog
      .filter((e) => !category || e.category === category)
      .filter((e) => !mcp || (mcp === "official" ? e.mcp?.type === "official" : e.mcp?.type !== "none"))
      .filter((e) => no_auth === undefined || e.no_auth === no_auth)
      .filter((e) => !free_tier || e.has_free_tier)
      .filter((e) => !auth || e.auth === auth)
      .map((e) => [score(e, terms), e])
      .filter(([s]) => s > 0)
      .sort((a, b) => b[0] - a[0])
      .slice(0, limit)
      .map(([, e]) => summary(e));
    const text = hits.length
      ? JSON.stringify({ source, results: hits }, null, 1)
      : "No match. Try a broader query or call list_categories and search by category.";
    return { content: [{ type: "text", text }] };
  },
);

server.registerTool(
  "get_api",
  {
    title: "Get API details",
    description:
      "Full entry for one service: docs, auth method and how the credential is sent, MCP endpoint, " +
      "free tier, SDKs, OpenAPI and llms.txt links, notes, verification date and last link check.",
    inputSchema: { id: z.string().describe("Service id from search_apis") },
  },
  async ({ id }) => {
    const e = catalog.find((x) => x.id === id);
    const text = e ? JSON.stringify(e, null, 1) : `Unknown id '${id}'. Use search_apis to find ids.`;
    return { content: [{ type: "text", text }], isError: !e };
  },
);

await refresh();
buildIndex();
await server.connect(new StdioServerTransport());
