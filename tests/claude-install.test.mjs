// End-to-end install in Claude Code, in a throwaway config dir (CLAUDE_CONFIG_DIR) so the
// user's own setup is untouched: add this repo as a marketplace, install the plugin, check
// that the skill is registered and the MCP server connects. Skipped without the claude CLI.
// The MCP server is started as `npx -y ai-agents-api-library`, so the last check covers the published npm version.
import { test, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("../", import.meta.url))); // no trailing slash: it would escape the closing quote on Windows
const hasClaude = spawnSync("claude --version", { shell: true }).status === 0;
const skip = !hasClaude && "claude CLI not installed";

const config = await mkdtemp(join(tmpdir(), "aal-claude-"));
// The local marketplace copies the working tree (including untracked files) into the config dir.
after(() => rm(config, { recursive: true, force: true }));

const claude = (args, timeout = 60_000) => {
  const r = spawnSync(`claude ${args}`, {
    cwd: ROOT, shell: true, encoding: "utf8", timeout, env: { ...process.env, CLAUDE_CONFIG_DIR: config },
  });
  return { ok: r.status === 0, out: `${r.stdout}${r.stderr}` };
};

test("marketplace add + plugin install", { skip }, () => {
  let r = claude(`plugin marketplace add "${ROOT}"`, 240_000);
  assert.ok(r.ok, r.out);
  r = claude("plugin install ai-agents-api-library@eater2", 240_000); // copies the working tree, node_modules included
  assert.ok(r.ok, r.out);
  r = claude("plugin list");
  assert.match(r.out, /ai-agents-api-library@eater2[\s\S]*enabled/);
});

test("skill is registered", { skip }, () => {
  const r = claude("plugin details ai-agents-api-library");
  assert.ok(r.ok, r.out);
  assert.match(r.out, /Skills \(1\)\s+ai-agents-api-library/);
});

test("MCP server connects", { skip: skip || (process.env.SKIP_NETWORK === "1" && "SKIP_NETWORK=1") }, () => {
  const r = claude("mcp list", 180_000);
  assert.match(r.out, /plugin:ai-agents-api-library:ai-agents-api-library: npx -y ai-agents-api-library - ✔ Connected/, r.out);
});
