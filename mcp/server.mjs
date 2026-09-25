#!/usr/bin/env node
// MCP server for the AI Agents API Library over stdio (npx -y ai-agents-api-library).
// Tools and ranking live in core.mjs, shared with the HTTP endpoint in api/mcp.mjs.
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer, load } from "./core.mjs";

await load();
await createServer().connect(new StdioServerTransport());
