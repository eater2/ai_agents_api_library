// Install test for the stdio MCP server: pack the repo the way `npx -y github:...` does,
// install the tarball into an empty folder and talk MCP to the installed bin.
import { test, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, readdir, stat } from "node:fs/promises";
import { execSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const ROOT = fileURLToPath(new URL("../", import.meta.url));
const dir = await mkdtemp(join(tmpdir(), "aal-pkg-"));
after(() => rm(dir, { recursive: true, force: true }));

const sh = (cmd, cwd) => execSync(cmd, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });

test("npm pack contains only what the server needs", () => {
  const [info] = JSON.parse(sh(`npm pack --json --pack-destination "${dir}"`, ROOT));
  const files = info.files.map((f) => f.path);
  for (const f of ["package.json", "mcp/server.mjs", "mcp/core.mjs", "catalog/all.json"]) {
    assert.ok(files.includes(f), `${f} missing from package`);
  }
  assert.ok(files.some((f) => f.startsWith("catalog/reviews/")), "review files are bundled (get_reviews fallback)");
  assert.ok(!files.some((f) => /(^|\/)\.env/.test(f)), "no .env files in the package");
  assert.ok(info.size < 5_000_000, `package is ${info.size} bytes`);
});

test("installed bin speaks MCP over stdio", async () => {
  const [tgz] = (await readdir(dir)).filter((f) => f.endsWith(".tgz"));
  assert.ok(tgz, "tarball from previous test");
  const app = join(dir, "app");
  await mkdir(app);
  sh(`npm init -y && npm install --no-audit --no-fund "${join(dir, tgz)}"`, app);
  const bin = join(app, "node_modules", "ai-agents-api-library", "mcp", "server.mjs");
  await stat(join(app, "node_modules", ".bin", process.platform === "win32" ? "ai-agents-api-library.cmd" : "ai-agents-api-library"));

  const client = new Client({ name: "install-test", version: "1.0.0" });
  await client.connect(new StdioClientTransport({
    command: process.execPath,
    args: [bin],
    cwd: app,
    env: { ...process.env, AGENTS_API_LIBRARY_OFFLINE: "1" },
  }));
  try {
    const tools = (await client.listTools()).tools.map((t) => t.name).sort();
    assert.deepEqual(tools, ["get_api", "get_reviews", "list_categories", "search_apis"]);
    const r = await client.callTool({ name: "search_apis", arguments: { query: "geocoding", limit: 3 } });
    const body = JSON.parse(r.content[0].text);
    assert.equal(body.source, "bundled");
    assert.ok(body.results.length > 0);
  } finally {
    await client.close();
  }
});
