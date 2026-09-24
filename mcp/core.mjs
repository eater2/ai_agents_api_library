// Shared core of the MCP server: catalog loading, search ranking and tool definitions.
// Used by the stdio entry point (mcp/server.mjs) and the HTTP endpoint (api/mcp.mjs).
//
// Data: the bundled catalog/all.json, refreshed from GitHub by load() unless
// AGENTS_API_LIBRARY_OFFLINE=1 is set.
import { readFile } from "node:fs/promises";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const RAW = "https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/all.json";
const BUNDLED = new URL("../catalog/all.json", import.meta.url);
const MIN_RELATIVE_SCORE = 0.1; // results scoring below this share of the best one are dropped

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

const STOP = new Set(["a", "an", "the", "to", "of", "for", "and", "or", "in", "on", "with", "via", "from", "api", "apis",
  "i", "my", "need", "want", "prompt", "prompts", "plan", "plans", "free", "paid", "pricing", "tier", "service", "tool", "tools"]);
const words = (s) => (s || "").toLowerCase().split(/[^a-z0-9+#]+/).filter((w) => w.length > 1 && !STOP.has(w));

// Query-side synonyms for words the catalog descriptions phrase differently.
const SYNONYMS = {
  academic: ["scholarly", "research"],
  paper: ["scholarly", "preprint", "literature", "publication"],
  papers: ["scholarly", "preprint", "literature", "publication"],
  photo: ["image"],
  picture: ["image"],
  tts: ["speech"],
  stt: ["transcription", "transcribe"],
  sms: ["messaging", "text"],
  llm: ["model", "inference"],
  website: ["site"],
  memory: ["memories"],
};
// One group per query word: the word itself plus its synonyms, all stemmed.
const groups = (terms) => [...new Set(terms)].map((t) => [...new Set([t, ...(SYNONYMS[t] || [])].map(stem))]);

// Crude English stemming so "geocoding" matches "geocode", "videos" matches "video".
const stem = (w) => (w.length > 4 ? w.replace(/(ments?|ings?|ers?|ed|es|s|e)$/, "") : w);
const stems = (s) => new Set(words(s).map(stem));

// Per-entry stem sets plus inverse document frequency, so rare terms ("3d", "sms")
// outweigh common ones ("image", "send").
let index = new Map();
let idf = new Map();
// catShare[category][stem] = share of the category's entries whose name/description contain the stem.
// "video" is in most video-generation entries, so a query about video leans towards that category.
let catShare = new Map();
function buildIndex() {
  index = new Map(catalog.map((e) => [e.id, {
    name: stems(`${e.name} ${e.id}`),
    cat: stems(e.category.replace(/-/g, " ")),
    desc: stems(e.desc_en),
    notes: stems(e.notes || ""),
  }]));
  const df = new Map();
  for (const x of index.values()) for (const t of new Set([...x.name, ...x.cat, ...x.desc])) df.set(t, (df.get(t) || 0) + 1);
  idf = new Map([...df].map(([t, n]) => [t, Math.log(1 + catalog.length / n)]));

  const byCat = new Map();
  for (const e of catalog) {
    const x = index.get(e.id);
    const c = byCat.get(e.category) || { n: 0, counts: new Map() };
    c.n++;
    for (const t of new Set([...x.name, ...x.cat, ...x.desc])) c.counts.set(t, (c.counts.get(t) || 0) + 1);
    byCat.set(e.category, c);
  }
  catShare = new Map([...byCat].map(([cat, { n, counts }]) => [cat, new Map([...counts].map(([t, k]) => [t, k / n]))]));
}

function termScore(x, share, t) {
  const w = idf.get(t) || 0;
  let hit = 0;
  if (x.name.has(t)) hit += 3 * w;
  if (x.cat.has(t)) hit += 3 * w;
  if (x.desc.has(t)) hit += 3 * w;
  if (x.notes.has(t)) hit += 0.5 * w;
  return { hit, prior: 2 * w * (share.get(t) || 0) }; // prior: how typical the word is for the entry's category
}

function score(e, terms) {
  if (!terms.length) return 1;
  const x = index.get(e.id);
  const share = catShare.get(e.category);
  // Words the catalog never uses ("kubernetes") can't be matched by anything; leave them out so
  // they don't turn the query into a search for its remaining generic word.
  const gs = groups(terms).filter((g) => g.some((t) => idf.has(t)));
  if (!gs.length) return 0;
  const known = gs.length / groups(terms).length;
  let s = 0;
  let matched = 0;
  for (const g of gs) {
    // Best member of the group counts; synonyms count a little less than the word itself.
    let best = { hit: 0, prior: 0 };
    g.forEach((t, i) => {
      const r = termScore(x, share, t);
      const k = i === 0 ? 1 : 0.8;
      if (r.hit * k + r.prior * k > best.hit + best.prior) best = { hit: r.hit * k, prior: r.prior * k };
    });
    if (best.hit) matched++;
    s += best.hit + best.prior;
  }
  // Entries that match every query word beat entries that match one word many times.
  return s * (matched / gs.length) ** 2 * known;
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
  has_free_tier: e.has_free_tier,
  has_trial: e.has_trial,
  docs: e.docs,
  ratings: e.ratings, // proof of use: SourceForge rating/reviews, GitHub stars, Smithery uses (with url, fetched_at)
});


// Load the freshest catalog available and build the search index. Call once before createServer().
export async function load() {
  await refresh();
  buildIndex();
}

// One McpServer per connection (stdio) or per request (stateless HTTP).
export function createServer() {
  const server = new McpServer(
    { name: "ai-agents-api-library", version: "0.2.0" },
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
        .sort((a, b) => b[0] - a[0]);
      const top = hits[0]?.[0] || 0;
      const results = hits
        .filter(([s]) => s >= top * MIN_RELATIVE_SCORE) // drop weak tail matches
        .slice(0, limit)
        .map(([, e]) => summary(e));
      const text = results.length
        ? JSON.stringify({ source, results }, null, 1)
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
        "free tier, SDKs, OpenAPI and llms.txt links, notes, verification date, last link check and ratings " +
        "(public review scores and usage counts, each with source url and fetch date).",
      inputSchema: { id: z.string().describe("Service id from search_apis") },
    },
    async ({ id }) => {
      const e = catalog.find((x) => x.id === id);
      const text = e ? JSON.stringify(e, null, 1) : `Unknown id '${id}'. Use search_apis to find ids.`;
      return { content: [{ type: "text", text }], isError: !e };
    },
  );

  server.registerTool(
    "get_reviews",
    {
      title: "Get user reviews",
      description:
        "Public user reviews of one service (up to 100, from SourceForge): rating, title, pros, cons, overall, " +
        "reviewer role, company size, date and link to the original. Reviewer names are not included. " +
        "Use to judge real-world quality before recommending a service.",
      inputSchema: {
        id: z.string().describe("Service id from search_apis"),
        min_rating: z.number().int().min(1).max(5).optional().describe("Only reviews rated at least this"),
        max_rating: z.number().int().min(1).max(5).optional().describe("Only reviews rated at most this, e.g. 2 for complaints"),
        limit: z.number().int().min(1).max(100).optional().describe("Max reviews, default 20"),
      },
    },
    async ({ id, min_rating = 1, max_rating = 5, limit = 20 }) => {
      const data = await loadReviews(id);
      if (!data) {
        return { content: [{ type: "text", text: `No reviews stored for '${id}'. Check get_api ratings for other signals.` }] };
      }
      const reviews = data.reviews.filter((r) => (r.rating ?? 0) >= min_rating && (r.rating ?? 5) <= max_rating);
      const text = JSON.stringify({ ...data, returned: Math.min(limit, reviews.length), reviews: reviews.slice(0, limit) }, null, 1);
      return { content: [{ type: "text", text }] };
    },
  );
  return server;
}

// Review texts live in catalog/reviews/<id>.json: GitHub copy first, bundled copy as fallback.
async function loadReviews(id) {
  if (!/^[a-z0-9-]+$/.test(id)) return null;
  if (process.env.AGENTS_API_LIBRARY_OFFLINE !== "1") {
    try {
      const res = await fetch(RAW.replace("all.json", `reviews/${id}.json`), { signal: AbortSignal.timeout(8000) });
      if (res.ok) return await res.json();
    } catch {
      // fall through to the bundled copy
    }
  }
  try {
    return JSON.parse(await readFile(new URL(`../catalog/reviews/${id}.json`, import.meta.url), "utf8"));
  } catch {
    return null;
  }
}
