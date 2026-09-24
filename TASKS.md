# Lista zadań

Na podstawie wywiadów z agentami (`research/agent-interviews/2026-09-24/report.md`). Kolejność = priorytet.

## P0 — porządek repozytorium
- [x] Repozytorium na GitHubie, pierwszy commit
- [x] `.gitattributes` — końce linii LF dla plików generowanych
- [x] GitHub Pages z `/docs`: https://eater2.github.io/ai_agents_api_library/ (33 adresy działają)
- [x] Opis, strona domowa i tematy repo
- [x] Tematy repo (12): `ai-agents`, `mcp`, `mcp-server`, `mcp-servers`, `model-context-protocol`, `tool-calling`, `llm-tools`, `function-calling`, `agent-tools`, `api-catalog`, `api-directory`, `llms-txt`
- [x] `CONTRIBUTING.md` / `CONTRIBUTING.pl.md` + szablon pull requesta

## P1 — dystrybucja: być tam, gdzie agenci patrzą
- [x] Serwer MCP (`mcp/`) z narzędziami `search_apis`, `get_api`, `list_categories`; uruchamiany przez `npx -y github:eater2/ai_agents_api_library`
- [x] Skill Claude (`skills/ai-agents-api-library/SKILL.md`) + ZIP do wgrania w claude.ai (`docs/ai-agents-api-library-skill.zip`)
- [x] Plugin Claude Code z marketplace w repo: `/plugin marketplace add eater2/ai_agents_api_library`, `/plugin install ai-agents-api-library@eater2`
- [x] Zgłoszenie pluginu do katalogu Anthropic (2026-09-24, Claude Code, kontakt: airenovationcalculator@gmail.com) — status: pending review, https://platform.claude.com/plugins/submissions
- [ ] Publikacja paczki npm (wymaga tokenu npm)
- [x] Oficjalny rejestr MCP: `io.github.eater2/ai-agents-api-library` 0.1.0 (`server.json`, `mcp-publisher`, 2026-09-24)
- [x] Smithery: https://smithery.ai/servers/eater2/ai-agents-api-library (namespace `eater2`, zdalny URL, 2026-09-24)
- [x] Glama: `glama.json` z właścicielem `eater2` w repo
- [ ] **(ręcznie)** Glama: dodać serwer na https://glama.ai/mcp/servers (przycisk „Add server”, logowanie GitHubem) — API wymaga konta
- [ ] PulseMCP: indeksuje oficjalny rejestr MCP automatycznie; strona blokuje automatyczne sprawdzenie (403), więc sprawdzić ręcznie https://www.pulsemcp.com/servers
- [x] Zdalny endpoint MCP (Streamable HTTP, Vercel): https://ai-agents-api-library.vercel.app/mcp
- [x] Osobne strony HTML per kategoria pod zapytania agentów (np. „video generation API free tier MCP”), w sitemap

## P2 — wiarygodność
- [x] Automatyczny test linków (`scripts/check_links.py`): `docs`, `mcp.url`, `openapi`, `llms_txt` → `data/link-status.json`
- [x] GitHub Action: test co tydzień + przy PR, wyniki commitowane do repo
- [x] Pole `link_check` w JSON dla agentów (status + data ostatniego testu)
- [x] Polityka świeżości: `stale: true`, gdy `verified` starsze niż 90 dni
- [x] Automatyczne testy instalacji (`tests/`, `npm test`, CI): spójność wersji w package.json / plugin.json / marketplace.json / server.json, frontmatter SKILL.md, skill wymienia tylko istniejące narzędzia i wszystkie kategorie, ZIP skilla aktualny, `claude plugin validate --strict`, `npm pack` + instalacja + MCP po stdio, endpoint HTTP lokalnie (i wdrożony z `MCP_URL`), pełna instalacja pluginu w Claude Code w tymczasowym `CLAUDE_CONFIG_DIR` (2026-09-24)
- [x] `claude plugin details` pokazywał „MCP servers (0)”: CLI liczy tylko serwery z `.mcp.json` w katalogu pluginu, a nie `mcpServers` w `plugin.json` (ani wpisane, ani jako ścieżka). Konfiguracja przeniesiona do `.mcp.json`, test pilnuje tego w `tests/plugin.test.mjs` (2026-09-24)
- [x] Wersja 0.2.0 (nowe narzędzie `get_reviews`) we wszystkich manifestach i w `mcp/core.mjs`; test „one version everywhere” sprawdza też wersję serwera (2026-09-24)
- [x] Tagi wersji (`v0.2.0` … `v0.2.3`); przy każdej zmianie narzędzi podbijać wersję, żeby `/plugin update` ją zauważył
- [x] `vercel.json` includeFiles: `catalog/**`, więc `get_reviews` na Vercelu ma lokalną kopię opinii, gdy GitHub nie odpowiada (2026-09-24)
- [ ] Weryfikacja per pole: `source_url` + `checked_at` dla `auth`, `free_tier`, `mcp`
- [ ] Rozróżnienie MCP `official` / `vendor-hosted` / `community` + weryfikacja domeny

## P2b — oceny i opinie jako „proof”

Cel: przy każdym narzędziu pokazywać ocenę i liczbę opinii (i sygnały użycia) z kilku źródeł, z linkiem i datą pobrania — na stronie, w `llms.txt` / `llms-full.txt`, w JSON i w odpowiedziach serwera MCP.

- [x] Źródła: SourceForge (robots.txt pozwala), GitHub API, Smithery API. G2, Capterra, GetApp, Product Hunt blokują automaty (403/Cloudflare) — pominięte; Glama wymaga klucza
- [x] `scripts/fetch_ratings.py` → `data/ratings.json` (148 usług) + do 100 opinii na usługę w `catalog/reviews/<id>.json` (80 usług, bez nazwisk; tylko JSON i MCP `get_reviews`, nie na stronie)
- [x] Pole `ratings` + `reviews_url` w JSON, dowód pod nazwą na stronie i kolumna na stronach kategorii, `proof:` w `llms-full.txt`
- [x] Cotygodniowe odświeżanie w GitHub Action (razem z testem linków)
- [x] Na stronie: źródło i znacznik czasu UTC przy każdej ocenie + linia „fetched: …” nad tabelami

Kandydaci na źródła:

| Źródło | Co daje | Dostęp | Uwagi |
|---|---|---|---|
| **GitHub** (repo SDK / serwera MCP) | gwiazdki, forki, data ostatniego commita | oficjalne REST API, token już jest | legalne, dobre dla MCP i SDK; to popularność, nie ocena |
| **npm / PyPI** | pobrania SDK tygodniowo/miesięcznie | `api.npmjs.org/downloads`, `pypistats.org/api` | darmowe, bez klucza; mierzy realne użycie przez deweloperów |
| **Smithery / Glama / PulseMCP** | liczba instalacji/użyć serwera MCP, ocena jakości (Glama) | publiczne API (część wymaga klucza) | najbliższe temu, co obchodzi agentów |
| **Product Hunt** | upvotes, ocena, liczba recenzji | GraphQL API (token) | sprawdzić regulamin API przy użyciu komercyjnym |
| **G2** | ocena ★ i liczba recenzji | brak publicznego API dla nie-dostawców | regulamin zabrania scrapingu — tylko ręcznie albo przez partnerstwo |
| **Capterra / GetApp** | ocena ★ i liczba recenzji | brak publicznego API | jak G2 — ręcznie / za zgodą |
| **Trustpilot** | TrustScore i liczba opinii | API dla firm (klucz) | dane o firmie, nie o API; ostrożnie z interpretacją |
| **Hacker News (Algolia)** | liczba wzmianek/punktów | darmowe API | sygnał rozgłosu, nie jakości |

Propozycja startu: GitHub + npm/PyPI + Smithery/Glama (legalne API, mierzą użycie przez deweloperów i agentów), a G2/Capterra tylko jako ręcznie wpisane oceny z linkiem i datą.

## P3 — pola danych
- [x] `no_auth: true` dla usług działających bez klucza (agenci wybierają je w praktyce)
- [ ] `free_tier` jako struktura: `requires_card`, `quota`, `period`, `watermark`, `source_url`
- [ ] `auth` jako OpenAPI `securitySchemes` (nazwa nagłówka, format) zamiast prozy
- [ ] `base_url`, `rate_limits`, `oauth_scopes`, `async_jobs`, `data_policy`
- [ ] `mcp.tools` — lista narzędzi serwera MCP i czy pokrywa całe REST API

## P4 — format i bezpieczeństwo
- [x] Pliki kategorii < 60 KB, ok. 15 tys. tokenów (kontrola w build; limit podniesiony z 30 KB po dodaniu źródeł per pole)
- [x] Sumy kontrolne `SHA256SUMS` (w katalogu głównym i `docs/`, generowane przez build, link w `llms.txt`)
- [x] Podpisane wydania: `.github/workflows/release.yml` przy tagu `v*` publikuje wydanie (katalog, llms, ZIP skilla, paczka npm, sumy) z podpisem Sigstore (SLSA provenance); weryfikacja: `gh attestation verify <plik> --repo eater2/ai_agents_api_library`. Pierwsze: v0.2.3. ZIP skilla jest bajtowo identyczny na każdym systemie (bez kompresji, stałe pola nagłówka)
- [x] Przegląd `auth_hint` pod kątem trybu rozkazującego: żaden nie wydaje poleceń; tryb rozkazujący tylko w nieszkodliwych `notes`

## P5 — pomiar
- [x] Statystyki: `scripts/stats.py` co tydzień → `data/stats.json` (gwiazdki, pobrania wydań, użycia Smithery, npm); wywołania MCP logowane w Vercel (`{"evt":"mcp"}`, bez treści zapytań)
- [ ] GitHub Traffic (wyświetlenia, klony) wymaga tokenu z uprawnieniem Administration: read — dodać sekret i użyć go w kroku statystyk
- [ ] Powtórzyć wywiady po wdrożeniu P1–P2 (`python scripts/interview_agents.py`)
