# AI Agents API Library (Claude Code plugin)

Find a third-party API or MCP server for a capability Claude doesn't have: image, video, music and 3D generation, web search and scraping, maps and weather, email and SMS, OCR, translation, payments, CAD/BIM, diagrams and more.

The catalog holds 300+ services. Each entry gives the official docs, the auth method and header, whether an official MCP server exists (with its endpoint), the free tier, and the date it was last checked. Links are re-checked every week.

## What the plugin adds

- **Skill `ai-agents-api-library`**: tells Claude when to consult the catalog and how to choose (no-key services first, then official MCP servers, then free tiers), and to ask you for credentials instead of inventing them.
- **MCP server** (remote, `https://ai-agents-api-library.vercel.app/mcp`): tools `search_apis`, `get_api` and `list_categories`. No API key needed.

## Network access and data

- The MCP server above receives the tool arguments (search text, service id, filters). It logs only the method, the tool name and the category filter; search text is not stored.
- When the MCP tools are not connected, the skill tells Claude to fetch the static catalog files instead, from `raw.githubusercontent.com/eater2/ai_agents_api_library` and `ai-agents-api-library.vercel.app`. These are plain GET requests with no user data.
- No API keys are sent to this project. Privacy policy: https://ai-agents-api-library.vercel.app/privacy.html

## Install

```
/plugin marketplace add eater2/ai_agents_api_library
/plugin install ai-agents-api-library@eater2
```

## Example prompts

- "Find an API that generates a short video from a text prompt and has a free tier."
- "Which service can geocode addresses without an API key?"
- "I need to send SMS to Polish numbers from my agent. What do I set up?"
- "Connect an MCP server for web scraping."

Full catalog, data files and contribution guide: https://github.com/eater2/ai_agents_api_library · Website: https://ai-agents-api-library.vercel.app/

License: MIT
