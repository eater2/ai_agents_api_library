// Static checks of everything a user installs: Claude Code plugin + marketplace,
// the skill (folder and zip), the npm package and the MCP Registry entry.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { execFileSync, spawnSync } from "node:child_process";
import { inflateRawSync } from "node:zlib";
import { fileURLToPath } from "node:url";

const ROOT = new URL("../", import.meta.url);
const read = (p) => readFile(new URL(p, ROOT), "utf8");
const json = async (p) => JSON.parse(await read(p));

const pkg = await json("package.json");
const plugin = await json(".claude-plugin/plugin.json");
const market = await json(".claude-plugin/marketplace.json");
const registry = await json("server.json");
const coreSrc = await read("mcp/core.mjs");
const SKILL_DIR = "skills/ai-agents-api-library/";
const skill = await read(SKILL_DIR + "SKILL.md");

function frontmatter(md) {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  assert.ok(m, "SKILL.md starts with a --- frontmatter block");
  return Object.fromEntries(m[1].split(/\r?\n/).map((l) => l.match(/^([a-z_-]+):\s*(.*)$/)).filter(Boolean).map((x) => [x[1], x[2]]));
}

test("one version everywhere", () => {
  const entry = market.plugins.find((p) => p.name === plugin.name);
  const core = coreSrc.match(/name: "ai-agents-api-library", version: "([^"]+)"/)?.[1];
  const versions = { package: pkg.version, plugin: plugin.version, marketplace: entry?.version, registry: registry.version, server: core };
  assert.equal(new Set(Object.values(versions)).size, 1, JSON.stringify(versions));
});

test("names line up across manifests", () => {
  assert.equal(pkg.name, plugin.name);
  assert.equal(pkg.mcpName, registry.name, "package.json mcpName must equal server.json name (MCP Registry ownership check)");
  const entry = market.plugins.find((p) => p.name === plugin.name);
  assert.ok(entry, "marketplace lists the plugin");
  assert.equal(entry.source, "./");
  assert.ok(pkg.bin[pkg.name], "npm bin named like the package, so `npx -y github:...` runs it");
});

test("plugin MCP server points at this repo and a file that exists", async () => {
  // Kept in .mcp.json, not inline in plugin.json: `claude plugin details` only counts servers from .mcp.json.
  assert.equal(plugin.mcpServers, undefined, "declare MCP servers in .mcp.json, not plugin.json");
  const [srv] = Object.values((await json(".mcp.json")).mcpServers);
  assert.equal(srv.command, "npx");
  const repo = new URL(plugin.repository).pathname.slice(1);
  assert.deepEqual(srv.args, ["-y", `github:${repo}`]);
  const bin = await read(pkg.bin[pkg.name]);
  assert.match(bin, /^#!\/usr\/bin\/env node/, "bin has a node shebang");
});

test("skill: folder, frontmatter and limits", async () => {
  assert.equal(plugin.skills, "./skills/");
  const fm = frontmatter(skill);
  assert.equal(fm.name, "ai-agents-api-library", "name equals folder name");
  assert.match(fm.name, /^[a-z0-9-]{1,64}$/);
  assert.ok(fm.description && fm.description.length <= 1024, `description ${fm.description?.length} chars (max 1024)`);
  assert.doesNotMatch(fm.description, /[<>]/, "no angle brackets in description");
  assert.ok(skill.length < 20000, "skill body stays small");
});

test("skill names only tools the MCP server really has", async () => {
  const core = await read("mcp/core.mjs");
  const tools = [...core.matchAll(/registerTool\(\s*"([a-z_]+)"/g)].map((m) => m[1]);
  const mentioned = [...new Set([...skill.matchAll(/`([a-z]+_[a-z_]+)`/g)].map((m) => m[1]))]
    .filter((t) => /^(search|get|list)_/.test(t));
  assert.ok(mentioned.length >= 3);
  for (const t of mentioned) assert.ok(tools.includes(t), `SKILL.md mentions ${t}, server has ${tools}`);
});

test("skill lists exactly the catalog categories", async () => {
  const cats = (await json("data/categories.json")).map((c) => c.id).sort();
  const line = skill.split("\n").find((l) => l.startsWith("Category ids:"));
  const listed = [...line.matchAll(/`([a-z0-9-]+)`/g)].map((m) => m[1]).sort();
  assert.deepEqual(listed, cats);
  for (const c of cats) await read(`catalog/${c}.json`); // the URLs the skill tells agents to fetch
});

test("skill zip for claude.ai holds the current SKILL.md", async () => {
  const zip = await readFile(new URL("docs/ai-agents-api-library-skill.zip", ROOT));
  // Walk local file headers (PK\x03\x04) without a zip library.
  const files = {};
  for (let i = 0; zip.readUInt32LE(i) === 0x04034b50;) {
    const method = zip.readUInt16LE(i + 8), size = zip.readUInt32LE(i + 18);
    const nameLen = zip.readUInt16LE(i + 26), extra = zip.readUInt16LE(i + 28);
    const name = zip.toString("utf8", i + 30, i + 30 + nameLen);
    const data = zip.subarray(i + 30 + nameLen + extra, i + 30 + nameLen + extra + size);
    files[name] = (method === 8 ? inflateRawSync(data) : data).toString("utf8");
    i += 30 + nameLen + extra + size;
  }
  assert.deepEqual(Object.keys(files), ["ai-agents-api-library/SKILL.md"], "one top-level folder with SKILL.md");
  assert.equal(files["ai-agents-api-library/SKILL.md"].replace(/\r\n/g, "\n"), skill.replace(/\r\n/g, "\n"),
    "zip is stale: run python scripts/build.py");
});

test("files needed by `npx github:` and Vercel are committed", () => {
  const tracked = new Set(execFileSync("git", ["ls-files"], { cwd: fileURLToPath(ROOT), encoding: "utf8" }).split("\n"));
  for (const f of ["package.json", "package-lock.json", "mcp/server.mjs", "mcp/core.mjs", "catalog/all.json",
    "api/mcp.mjs", "vercel.json", SKILL_DIR + "SKILL.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".mcp.json"]) {
    assert.ok(tracked.has(f), `${f} is not tracked by git`);
  }
});

test("MCP Registry entry", () => {
  assert.match(registry.name, /^io\.github\.eater2\//);
  const [remote] = registry.remotes;
  assert.equal(remote.type, "streamable-http");
  assert.match(remote.url, /^https:\/\/.+\/mcp$/);
  assert.ok(registry.description.length <= 100, "registry description max 100 chars");
});

test("Vercel bundles the files the HTTP endpoint reads", async () => {
  const vercel = await json("vercel.json");
  const fn = vercel.functions["api/mcp.mjs"];
  assert.ok(fn, "function config for api/mcp.mjs");
  assert.match(fn.includeFiles, /catalog\/all\.json|catalog\/\*\*/);
  assert.ok(vercel.rewrites.some((r) => r.source === "/mcp" && r.destination === "/api/mcp"));
});

// The official validator, when Claude Code is installed (skipped in plain CI).
const hasClaude = spawnSync("claude --version", { shell: true }).status === 0;
test("claude plugin validate --strict", { skip: !hasClaude && "claude CLI not installed" }, () => {
  for (const target of [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "skills"]) {
    const r = spawnSync(`claude plugin validate "${target}" --strict`, { cwd: fileURLToPath(ROOT), shell: true, encoding: "utf8" });
    assert.equal(r.status, 0, `${target}:\n${r.stdout}${r.stderr}`);
  }
});

test("usage data: examples are safe and match the entry", async () => {
  const all = await json("catalog/all.json");
  const withCall = all.filter((e) => e.call);
  for (const e of withCall) {
    const { example, url, method } = e.call;
    assert.match(example, /^curl /, `${e.id}: example is a curl command`);
    // Per-tenant hosts are written as {placeholder}; otherwise the example must call the documented URL.
    if (!url.startsWith("{")) {
      assert.ok(example.includes(url.split("{")[0].split("?")[0].replace(/\/$/, "")) || example.includes(new URL(url).host), `${e.id}: example calls ${url}`);
    }
    assert.match(method, /^(GET|POST|PUT|PATCH|DELETE)$/);
    // Secrets only as placeholders: no long opaque tokens in examples.
    assert.doesNotMatch(example, /\b(sk|pk|rk|xox[bp]|ghp|key)[-_][A-Za-z0-9]{16,}/, `${e.id}: example contains a real-looking key`);
    // The shell does not expand $VARS inside single quotes; those must be <PLACEHOLDERS>.
    for (const [, quoted] of example.matchAll(/'([^']*)'/g)) {
      assert.doesNotMatch(quoted, /\$[A-Z][A-Z0-9_]{2,}/, `${e.id}: $VAR inside single quotes is not expanded`);
    }
  }
  for (const e of all.filter((x) => x.mcp.config && !x.mcp.config.derived)) {
    const c = e.mcp.config;
    assert.ok(c.source_url?.startsWith("http"), `${e.id}: mcp.config.source_url`);
    // Header values are placeholders ($ENV_VAR, {id}) or plain settings, never a real-looking secret.
    for (const v of Object.values(c.headers || {})) assert.doesNotMatch(v.replace(/\$[A-Z_]+/g, ""), /[A-Za-z0-9_-]{24,}/, `${e.id}: header ${v}`);
  }
});

test("wording: the catalog is not presented as 'verified'", async () => {
  for (const f of [SKILL_DIR + "SKILL.md", "server.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "llms.txt"]) {
    assert.doesNotMatch(await read(f), /verified (catalog|services|APIs)|Verified catalog/i, f);
  }
});
