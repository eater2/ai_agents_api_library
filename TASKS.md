# Lista zadań

Na podstawie wywiadów z agentami (`research/agent-interviews/2026-09-24/report.md`). Kolejność = priorytet.

## P0 — porządek repozytorium
- [x] Repozytorium na GitHubie, pierwszy commit
- [x] `.gitattributes` — końce linii LF dla plików generowanych
- [x] GitHub Pages z `/docs`: https://eater2.github.io/ai_agents_api_library/ (33 adresy działają)
- [x] Opis, strona domowa i tematy repo
- [ ] **(ręcznie)** Dopisać tematy: `model-context-protocol`, `mcp-server`, `tool-calling`, `llm-tools`, `function-calling`, `agent-tools`
- [x] `CONTRIBUTING.md` / `CONTRIBUTING.pl.md` + szablon pull requesta

## P1 — dystrybucja: być tam, gdzie agenci patrzą
- [x] Serwer MCP (`mcp/`) z narzędziami `search_apis`, `get_api`, `list_categories`; uruchamiany przez `npx -y github:eater2/ai_agents_api_library`
- [x] Skill Claude (`skills/ai-agents-api-library/SKILL.md`) + ZIP do wgrania w claude.ai (`docs/ai-agents-api-library-skill.zip`)
- [x] Plugin Claude Code z marketplace w repo: `/plugin marketplace add eater2/ai_agents_api_library`, `/plugin install ai-agents-api-library@eater2`
- [ ] **(ręcznie, przez przeglądarkę)** Zgłoszenie pluginu do katalogu Anthropic: https://platform.claude.com/plugins/submit
- [ ] Publikacja paczki npm (wymaga tokenu npm)
- [ ] Zgłoszenie do oficjalnego rejestru MCP (`mcp-publisher`, przestrzeń nazw `io.github.eater2`), Smithery, Glama, PulseMCP
- [ ] Zdalny endpoint MCP (HTTP) — np. Vercel/Cloudflare, żeby działał bez instalacji
- [x] Osobne strony HTML per kategoria pod zapytania agentów (np. „video generation API free tier MCP”), w sitemap

## P2 — wiarygodność
- [x] Automatyczny test linków (`scripts/check_links.py`): `docs`, `mcp.url`, `openapi`, `llms_txt` → `data/link-status.json`
- [x] GitHub Action: test co tydzień + przy PR, wyniki commitowane do repo
- [x] Pole `link_check` w JSON dla agentów (status + data ostatniego testu)
- [x] Polityka świeżości: `stale: true`, gdy `verified` starsze niż 90 dni
- [ ] Weryfikacja per pole: `source_url` + `checked_at` dla `auth`, `free_tier`, `mcp`
- [ ] Rozróżnienie MCP `official` / `vendor-hosted` / `community` + weryfikacja domeny

## P3 — pola danych
- [x] `no_auth: true` dla usług działających bez klucza (agenci wybierają je w praktyce)
- [ ] `free_tier` jako struktura: `requires_card`, `quota`, `period`, `watermark`, `source_url`
- [ ] `auth` jako OpenAPI `securitySchemes` (nazwa nagłówka, format) zamiast prozy
- [ ] `base_url`, `rate_limits`, `oauth_scopes`, `async_jobs`, `data_policy`
- [ ] `mcp.tools` — lista narzędzi serwera MCP i czy pokrywa całe REST API

## P4 — format i bezpieczeństwo
- [x] Pliki kategorii < 30 KB (kontrola w build)
- [ ] Podpisane wydania / sumy kontrolne (`SHA256SUMS`)
- [ ] Przegląd `auth_hint` pod kątem trybu rozkazującego

## P5 — pomiar
- [ ] Statystyki ruchu (GitHub Traffic API, pobrania npm, wywołania MCP)
- [ ] Powtórzyć wywiady po wdrożeniu P1–P2 (`python scripts/interview_agents.py`)
