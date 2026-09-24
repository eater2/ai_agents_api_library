// Ranking benchmark: for typical agent queries, the top results should come from
// the expected category. Prints a score table; exits 1 below the threshold.
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// [query, expected category, how many of the top 3 must be in it]
const CASES = [
  ["text to video", "video-generation", 3],
  ["generate an image from a prompt", "image-generation", 3],
  ["remove background from photo", "image-generation", 1],
  ["text to speech voice", "audio-speech", 3],
  ["transcribe audio", "audio-speech", 3],
  ["generate music", "music-generation", 3],
  ["3d model from image", "3d-generation", 3],
  ["web search", "web-search", 3],
  ["scrape a website to markdown", "web-scraping-browser", 2],
  ["headless browser automation", "web-scraping-browser", 3],
  ["run python code in a sandbox", "code-execution-sandbox", 3],
  ["send sms", "sms-messaging", 2],
  ["send email", "communication-email-chat", 3],
  ["phone call voice agent", "voice-agents-telephony", 2],
  ["geocoding", "maps-geo-weather", 2], // Esri ArcGIS (architecture-cad-bim) is a valid geocoder too
  ["weather forecast", "maps-geo-weather", 3],
  ["stock prices", "finance-payments", 2],
  ["accept payments", "finance-payments", 3],
  ["translate text", "translation-language", 3],
  ["ocr pdf", "presentations-documents", 3],
  ["create slides presentation", "presentations-documents", 2],
  ["bim model", "architecture-cad-bim", 3],
  ["cad", "architecture-cad-bim", 2],
  ["render mermaid diagram", "diagrams-software-architecture", 2],
  ["vector database", "databases-vector-memory", 3],
  ["long term memory for agents", "databases-vector-memory", 2],
  ["post to social media", "social-media", 2],
  ["shopify store orders", "ecommerce", 1],
  ["calendar events", "productivity-workspace", 2],
  ["crm contacts", "crm-support-marketing", 2],
  ["connect thousands of apps", "automation-integration", 2],
  ["llm inference api", "model-inference", 2],
  ["academic papers", "knowledge-research", 3],
];

const client = new Client({ name: "ranking-test", version: "1" });
await client.connect(new StdioClientTransport({
  command: process.execPath,
  args: [new URL("./server.mjs", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
  env: { ...process.env, AGENTS_API_LIBRARY_OFFLINE: "1" },
}));

let passed = 0;
for (const [query, cat, need] of CASES) {
  const r = await client.callTool({ name: "search_apis", arguments: { query, limit: 3 } });
  const text = r.content[0].text;
  const top = text.startsWith("{") ? JSON.parse(text).results : [];
  const hits = top.filter((x) => x.category === cat).length;
  const ok = hits >= need;
  passed += ok;
  if (!ok || process.argv.includes("-v")) {
    console.log(`${ok ? "ok  " : "FAIL"} ${query.padEnd(34)} ${hits}/${need} in ${cat}: ${top.map((x) => x.name).join(" | ")}`);
  }
}
await client.close();
const pct = Math.round((100 * passed) / CASES.length);
console.log(`ranking: ${passed}/${CASES.length} (${pct}%)`);
process.exit(pct >= 90 ? 0 : 1);
