# Retest produktu po poprawkach P0b/P0c (2026-09-24, wieczór)

Porównanie z `../2026-09-24-product-test/` (rano, MCP 0.2.x) na tych samych trzech zadaniach. Materiał pobrany z żywego
serwera MCP 0.3.3 (`material.txt`), tym samym skryptem (`python scripts/interview_product_test.py --suffix=retest`).

**Wywiady z agentami nie odbyły się:** OpenRouter zwrócił `HTTP 402 Payment Required` dla wszystkich 7 modeli (wyczerpane
środki na koncie). Poniżej tylko porównanie mechaniczne tego, co agent dostaje od katalogu. Po doładowaniu:
`python scripts/interview_product_test.py --suffix=retest --missing`.

## search_apis: top 5

| Zadanie | Rano | Wieczorem (0.3.3) |
|---|---|---|
| 1. Wideo 5 s z promptu, bez budżetu (`free_tier`) | Google Gemini API, Mux, Akool, Creatomate, Voyage AI (4 z 5 nie generuje wideo z tekstu) | Freepik API, Hugging Face Inference Providers (tylko 2, oba `match: exact`) |
| 2. Geokodowanie 200 adresów w Polsce | Google Maps, Nominatim (2. mimo limitu 1 req/s), Esri, **IP2Location.io** (geolokalizacja IP), Geoapify | Esri, Google Maps, LocationIQ, OpenCage, Nominatim (5., z `volume_warning`); wszystkie `exact` |
| 3. SMS z przypomnieniem | **LINE**, Twilio, Vonage, **WhatsApp**, **Discord** | AWS End User Messaging SMS, Bird, Sinch, Twilio, Plivo; wszystkie `exact` |

Szum z porannego testu zniknął we wszystkich trzech zadaniach. Wyniki mają `match` z uzasadnieniem, a pusty wynik daje
komunikat o luce i podpowiedź (test regresyjny: `tests/search.test.mjs`).

## get_api: pola

Rano 20 pól, wieczorem 30. Nowe: `operations`, `base_url`, `auth_scheme`, `rate_limits`, `async_jobs`, `no_card`,
`uptime` (sonda dzienna, pierwsza na liście sygnałów), `mcp_repo` (archived, pushed_at, stars), `mcp_registry`,
`product_reviews` (bez zagregowanej oceny). MCP „tylko dokumentacja” nie jest już pokazywany jako `official`
(np. Gemini: rano `official` → `gemini-api-docs-mcp.dev`, teraz `none` z notatką).

## Czego nadal brakuje

- **Przykładowe wywołanie (`call`) ma 31 z 330 wpisów, cena jednostkowa (`unit_price`) 25.** To była druga najczęstsza
  uwaga agentów („get_api nie mówi, jak wywołać”). Freepik, pierwszy wynik zadania 1, nie ma `call`.
- Uptime ma 1 pomiar (od dziś); wartość sygnału rośnie z oknem 30 dni.
- Wątpliwości `free_plan` bez decyzji: x-twitter-api (teraz tylko pay-per-use), you-com (trwały limit 100/dzień?),
  reducto i zendesk (karta niepotwierdzona), modernmt (brak triala), aws-textract (pula 2000 stron AnalyzeLending).
