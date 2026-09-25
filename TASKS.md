# Lista zadań

Na podstawie wywiadów z agentami (`research/agent-interviews/2026-09-24/report.md`). Kolejność = priorytet.

## P0b — wyniki testu produktu z 7 agentami (2026-09-24)

Źródło: `research/agent-interviews/2026-09-24-product-test/report.md`, strona z wynikami: https://claude.ai/artifact/3gH1aWdZxZaJ9zvHugBorj.
Wniosek: skill dobrze wyzwala `search_apis`, ale agenci porzucają narzędzie po 1–2 chybionych wynikach. Plan na noc 2026-09-24/25, właściciel w nawiasie.

Wyszukiwanie (`mcp/core.mjs`)
- [x] Pusty wynik zamiast dopełniania listy: próg trafności, komunikat o luce w pokryciu („no catalogued text-to-video API with a free tier”) i podpowiedź (inna kategoria / bez filtra / web search) — 5/7 agentów (54)
- [x] Ranking po czynności: pole `operations` z wpisów, wynik `match: exact | adjacent` z krótkim powodem — blokada nr 1 dla 6/7 (54, po danych od bf; kod gotowy w 0.3.1, działa po dodaniu `operations`)
- [x] Ranking uwzględnia wolumen i limity (`rate_limits`, zakaz pracy wsadowej, np. Nominatim) (54)
- [x] Test regresyjny z 3 zadań testu: wideo bez Voyage/Mux/Gemini; geokodowanie z Geoapify/Mapbox/HERE, bez IP2Location; SMS z Twilio/Vonage na górze, bez LINE/Discord/WhatsApp (54; `tests/search.test.mjs`, pomijany do czasu `operations`)
- [x] Opisy narzędzi MCP: warunek pominięcia (podłączone narzędzie lub własny model), „once a human has provisioned credentials”, „ranking is not proof of fit”, `get_reviews` opcjonalne (54)

Dane (`data/catalog.json`)
- [x] `operations`: kontrolowany słownik czynności (np. `text-to-video`, `sms`, `street-geocoding`, `ip-geolocation`, `video-hosting`) dla wszystkich 323 wpisów + opis słownika w schemacie (bf)
- [x] `has_free_tier` / `has_trial` liczone z `free_plan.kind`, a nie z tekstu (dziś „free trial…” liczy się jako darmowy plan); dodać `no_card` do JSON dla agentów (bf)
- [x] Poprawki z testu: Esri → `maps-geo-weather`; `video-generation` bez usług hostingu (Mux) i szablonów, albo jawne `operations`; przegląd kategorii pod kątem podobnych pomyłek (bf)
- [x] Brakujący dostawcy wskazani przez agentów: SMS — Plivo, Sinch, Telnyx, AWS SNS (End User Messaging), Bird; geokodowanie — OpenCage, LocationIQ (bf)

Wywołanie i MCP (`get_api`)
- [x] Minimalny przykład żądania + ścieżka endpointu + metoda + kluczowe pola odpowiedzi dla ok. 30 najczęściej wybieranych usług — 7/7 agentów (3b): pole `call` dla 31 usług w `data/usage.json` (curl, metoda, URL, pola odpowiedzi, `source_url`)
- [x] Gotowy snippet konfiguracji MCP per wpis (transport, `url` lub `command`, zmienne środowiskowe), oznaczenie `docs-only`, gdy serwer tylko przeszukuje dokumentację (3b): `mcp.config` dla 251 wpisów (223 z researchu, 28 wyprowadzonych z URL, `derived: true`), 14 serwerów `docs_only`, `mcp.issue` dla zarchiwizowanych
- [x] Cena za jednostkę operacji (np. 1 geokod = 1 kredyt, SMS do PL), gdzie dostawca ją publikuje (3b): `unit_price` dla 25 usług (np. SMS do PL: Twilio $0.0457, Vonage $0.04843)

Teksty (skill, llms.txt, README)
- [x] Skill: najpierw dopasowanie do czynności i wolumenu, dopiero potem `no_auth` / free tier; trial ≠ free tier; sprawdzić, czy `mcp` to endpoint czy repozytorium; `get_reviews` opcjonalne; wyzwalacz „naprawczy” (403, limit, nieobsługiwany format); pominąć zadania, które model robi sam (tłumaczenie, diagramy) (3b)
- [x] „verified” → „last checked” wszędzie, gdzie sprawdzamy tylko linki; osobno data sprawdzenia linku i danych (3b): etykiety w README/llms/stronach/manifestach/skillu; pole `verified` zostaje, dane mają własne `checked_at`, linki `link_check.checked_at`. Opisy narzędzi w `mcp/core.mjs` — 54

- [x] Poprawki z `research/p0b-3b/corrections-2026-09-24.md` (69 wpisów: MCP tylko do dokumentacji → `none` z notatką, zarchiwizowane repo, martwe URL-e, hostowane endpointy) przez `data/enrich/fix_p0b.json` + `b_p0b.json` (bf)
- [x] Podział kategorii przekraczających 60 KB: `sms-messaging` wydzielone z `communication-email-chat`, `databases` z `databases-vector-memory` (bf)

Na koniec
- [ ] Powtórzyć test produktu (`python scripts/interview_product_test.py`) i porównać z 2026-09-24 (bf)
  - Porównanie mechaniczne zrobione: `research/agent-interviews/2026-09-24-product-test-retest/comparison.md` (szum w wynikach zniknął we wszystkich 3 zadaniach). Wywiady zablokowane: OpenRouter 402 (brak środków); po doładowaniu `--suffix=retest --missing`.
- [x] `call` (przykładowe wywołanie) ma tylko 31/330 wpisów, `unit_price` 25/330 — uzupełnić przynajmniej dla wpisów z `free_plan` (3b): teraz `call` 251/330, `unit_price` 140/330; brak `call` tylko tam, gdzie dostawca nie publikuje odwołania HTTP (SDK/WebSocket/za logowaniem) lub strona blokuje dostęp; korekty: `research/p0b-3b/corrections-2026-09-24-round2.md`
- [x] Korekty rundy 2 od 3b (39 wpisów) i wątpliwości `free_plan` (You.com → `no_key`, Zendesk bez karty, Reducto: karta niepotwierdzona, Textract + AnalyzeLending, Kling → `none`) przez `fix_p0b2.json` + `b_p0b2.json`; ModernMT usunięty (rejestracja zamknięta, wygaszany w 2026), dodany następca Lara Translate (bf)
- [x] Pliki kategorii w zwartym JSON (wpis na linię): wszystkie < 60 KB po dodaniu `call` (bf)
- [x] `call` dla pozostałych 78 wpisów tylko z oficjalnej specyfikacji/dokumentacji: +64, razem 316/328 (2026-09-25, bf). Bez `call` (brak oficjalnego źródła albo brak REST): serper, framer, tencent-edgeone-pages, deepgram-voice-agent-api, mermaid-chart-api, playwright-mcp-microsoft, soundraw-api, modal, cloudflare-sandbox-sdk, piston, ebay-apis, zapier-mcp-ai-actions. Przy okazji: usunięte structurizr (chmura wyłączona) i csm (domena nie działa); poprawione zoo (brak REST text-to-CAD), piston (publiczna instancja za tokenem), base_url etsy/trimble, auth anthropic

## P0d — retest z 7 agentami (2026-09-25)

Źródło: `research/agent-interviews/2026-09-25-product-test-retest/report.md`. Wynik: 0× tak, 7× warunkowo. Jedyna wspólna blokada: zaufanie do pól decyzyjnych (`match`, `free_tier`, MCP). Wydatki OpenRouter: limit 20 USD (`OPENROUTER_BUDGET_USD`).

Wyszukiwanie i skill (54)
- [x] `match: exact` tylko gdy `call.operation` lub narzędzie MCP realizuje żądaną czynność (Freepik: przykład image-to-video przy text-to-video; Google Maps MCP bez narzędzia geokodowania; HF bez generowania wideo); MCP `docs_only` bez narzędzia dla czynności → niżej / oznaczone
- [x] Ranking pod zadanie: `requires_card` przy `no_card`, trial ≠ free (`include_trials`), wolumen/bulk, uwierzytelnianie `cloud_iam` niżej (AWS SMS był 1., Esri z kartą 1. przy geokodowaniu); Vonage/Telnyx/HERE/Geoapify/Mapbox są w katalogu, a nie trafiły do top 5
- [x] Skill i opisy narzędzi według sekcji 5 raportu: „currently connected tools”, zawężona klauzula 403, nowa definicja `exact`, wyzwalacz `get_api`, gdy użytkownik sam wskazuje usługę („znany dostawca to nie sprawdzony dostawca”), zawężone „confirm in docs”, bez „web search or scraping” we frontmatterze

Dane (bf)
- [x] Konfiguracje MCP `derived` (37): handshake `initialize`; zostają tylko odpowiadające jak serwer MCP, z informacją o wymaganym logowaniu (OAuth/klucz); strony dokumentacji usunięte — `scripts/probe_mcp.py` → `data/mcp-handshake.json` (174 endpointy: 42 ok, 100 OAuth, 22 klucz, 7 strona WWW, 2 zablokowane, 1 nie działa), pole `mcp.handshake`; zostały 34 z 37 wyprowadzonych, z polem `auth`
- [x] `free_plan` ze źródłem dla 28 wpisów, gdzie darmowy plan/trial pochodzi tylko z tekstu (m.in. Freepik: jednorazowe ~5 EUR = trial) — 25 potwierdzonych (7 z błędnym tekstem: DeepL, Microsoft Graph, Pinterest, Shopify, HERE, Trello, Synthflow); niepotwierdzone: Freepik, MiniMax, eBay (strony blokują); `free_plan` 313/331. Plivo: SMS nie jest już samoobsługowy → telefonia; triale SMS Telnyx/Twilio doprecyzowane
- [x] Uptime: definicja „reachable” (host odpowiada, HTTP < 500) jawnie w JSON, żeby 404 nie wyglądało na „API działa” — pole `uptime.up_means`
- [x] Brakujący dostawcy: GUGiK (oficjalny polski geokoder), Photon, Textbelt — jeśli spełniają kryteria: dodane wszystkie trzy z `call` (GUGiK: bez klucza, tylko Polska; Photon: bez klucza, nie do pracy wsadowej; Textbelt: 1 SMS/dzień za darmo)

Wywołania i MCP (3b)
- [x] Freepik: `call` dla czynności z `operations` (text-to-image albo potwierdzone text-to-video), nie image-to-video: text-to-video LTX Video 2.0 Pro (tylko prompt), host api.magnific.com
- [x] Twilio: `mcp.config` wskazuje serwer tylko z dokumentacją, a `mcp.url` działający twilio-labs/mcp — uzgodnić: config = stdio `npx -y @twilio-alpha/mcp`, serwer dokumentacji w `mcp.config.note`
- [x] Pola SMS: rejestracja nadawcy (10DLC), ograniczenia trialu (np. Twilio tylko zweryfikowane numery), kraje; cena SMS do PL tam, gdzie publikowana: pole `sms` dla 7 dostawców (Twilio, Vonage, Plivo, Telnyx, Sinch, AWS, Bird); cena do PL u 6 (bez Sinch)

## P0c — oceny i opinie: wywiady z 7 agentami (2026-09-24)

Źródło: `research/agent-interviews/2026-09-24-ratings/report.md`. Wniosek: średnia gwiazdek i liczba opinii to dla 6/7 agentów szum, zaufania do katalogu nie zwiększają (0/7 wyraźnie). Liczą się: niezależny uptime (7/7), aktywność repo MCP (`archived`, `pushed_at`; 5/7) i opinie o konkretnych awariach API (tylko przy remisie).

- [x] `search_apis`: kompaktowe pole ocen z jawnym brakiem danych (`status: unavailable`), brak danych nie obniża pozycji; średniej gwiazdek i instalacji nie używać w rankingu (54)
- [x] `get_api`: osobno `product_reviews` (źródło, ocena, liczba, zakres dat, `fetched_at`) i `mcp_repo` (`archived`, `pushed_at`, gwiazdki), bez jednego zbiorczego wyniku (54)
- [x] `get_reviews`: filtry (świeże, nisko ocenione, dotyczące API), tagi aspektów (błędy, auth, limity, breaking changes vs dashboard/billing), krótkie podsumowanie tematów z linkami; tekst opinii oznaczony jako niezaufany (54)
- [x] Sondy katalogu: `scripts/probe_uptime.py` + `.github/workflows/uptime.yml` (codziennie), `data/uptime.json` (30 dni) → pole `uptime` (`probes`, `up`, `median_ms`, ostatni wynik); szablony URL (`<region>`, `{subdomain}`) pomijane (bf, 2026-09-24)
- [ ] Później: wyniki agentów (telemetria) per operacja — tylko z mianownikiem, definicją sukcesu, minimalną próbą i pochodzeniem; najpierw sondy
- Nie robić: jednego `health_score`, rankingowania po gwiazdkach, poszerzania scrapowania opinii ludzkich

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
- [x] Publikacja paczki npm: https://www.npmjs.com/package/ai-agents-api-library (0.3.6, 2026-09-25, z podpisem provenance); kolejne wersje publikuje `release.yml` przy tagu `v*` (sekret `NPM_TOKEN`)
- [x] Oficjalny rejestr MCP: `io.github.eater2/ai-agents-api-library` 0.1.0 (`server.json`, `mcp-publisher`, 2026-09-24)
- [x] Rejestr MCP aktualizowany automatycznie przy każdym tagu `v*` (krok w `release.yml`, GitHub OIDC, bez przechowywanego tokenu); rejestr pokazywał 0.1.0 przy wersji 0.3.3
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
- [x] Weryfikacja per pole: `source_url` + `checked_at` dla `auth`, `free_tier`, `mcp` (auth_scheme 327/330, free_plan 284, mcp 286; v0.3.0–0.3.3)
- [x] Rozróżnienie MCP `official` / `vendor-hosted` / `community` + weryfikacja domeny (`mcp.kind`, `mcp.domain_verified`, v0.3.0)

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
- [x] `free_tier` jako struktura: `requires_card`, `quota`, `period`, `watermark`, `source_url` (`free_plan`, 284/330)
- [x] `auth` jako OpenAPI `securitySchemes` (nazwa nagłówka, format) zamiast prozy (`auth_scheme`, 327/330)
- [x] `base_url`, `rate_limits`, `oauth_scopes`, `async_jobs`, `data_policy` (296 / 223 / 45 / 100 / 54 wpisów; brak = dostawca nie publikuje albo nie potwierdzono)
- [x] `mcp.tools` — lista narzędzi serwera MCP i czy pokrywa całe REST API (tools 191, covers_full_api 227 z 271 serwerów)

## P4 — format i bezpieczeństwo
- [x] Pliki kategorii < 60 KB, ok. 15 tys. tokenów (kontrola w build; limit podniesiony z 30 KB po dodaniu źródeł per pole)
- [x] Sumy kontrolne `SHA256SUMS` (w katalogu głównym i `docs/`, generowane przez build, link w `llms.txt`)
- [x] Podpisane wydania: `.github/workflows/release.yml` przy tagu `v*` publikuje wydanie (katalog, llms, ZIP skilla, paczka npm, sumy) z podpisem Sigstore (SLSA provenance); weryfikacja: `gh attestation verify <plik> --repo eater2/ai_agents_api_library`. Pierwsze: v0.2.3. ZIP skilla jest bajtowo identyczny na każdym systemie (bez kompresji, stałe pola nagłówka)
- [x] Przegląd `auth_hint` pod kątem trybu rozkazującego: żaden nie wydaje poleceń; tryb rozkazujący tylko w nieszkodliwych `notes`

## P5 — pomiar
- [x] Statystyki: `scripts/stats.py` co tydzień → `data/stats.json` (gwiazdki, pobrania wydań, użycia Smithery, npm); wywołania MCP logowane w Vercel (`{"evt":"mcp"}`, bez treści zapytań)
- [ ] GitHub Traffic (wyświetlenia, klony) wymaga tokenu z uprawnieniem Administration: read — dodać sekret i użyć go w kroku statystyk
- [ ] Powtórzyć wywiady po wdrożeniu P1–P2 (`python scripts/interview_agents.py`)
