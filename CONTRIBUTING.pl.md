# Jak współtworzyć katalog

[English](CONTRIBUTING.md)

Dziękujemy za pomoc. Ta instrukcja pokazuje, jak przez pull request dodać, poprawić lub usunąć usługę.

## Jedna zasada

**Edytujesz tylko pliki w katalogu `data/`.** Wszystko inne generuje z nich skrypt `scripts/build.py`: README po angielsku i po polsku, strony HTML, pliki dla LLM i pliki JSON kategorii. Nie poprawiaj wygenerowanych plików ręcznie. Następne budowanie je nadpisze, a CI odrzuci pull request, w którym nie zgadzają się z danymi.

| Chcesz… | Edytuj plik | Wymagane pola |
|---|---|---|
| Dodać lub poprawić usługę | `data/catalog.json` | zob. [Pola wpisu](#pola-wpisu) |
| Usunąć usługę (brak API, zamknięta…) | usuń wpis z `data/catalog.json` | brak |
| Dodać kategorię | `data/categories.json` | `id`, `en`, `pl`, `desc_en`, `desc_pl` |
| Dodać powiązany katalog lub rejestr | `data/directories.json` | `name`, `url`, `machine_readable_url`, `desc_en`, `desc_pl` |

Uruchomienie `python scripts/build.py` tworzy z `data/` następujące pliki:

| Wygenerowany plik | Dla kogo | Język |
|---|---|---|
| `README.md` | ludzie na GitHubie | angielski |
| `README.pl.md` | ludzie na GitHubie | polski |
| `docs/index.html`, `docs/c/<kategoria>/index.html` | strona (GitHub Pages), wyszukiwarki | angielski |
| `docs/pl/index.html` | strona, tylko ludzie (nieindeksowana) | polski |
| `llms.txt`, `llms-full.txt`, `docs/llms*.txt` | agenci AI | angielski |
| `catalog/all.json`, `catalog/<kategoria>.json`, `docs/catalog.json` | agenci AI i serwer MCP | angielski |
| `docs/sitemap.xml`, `docs/robots.txt` | wyszukiwarki | – |

Obie wersje językowe powstają z tego samego wpisu: z `desc_en` powstają pliki angielskie, a z `desc_pl` polskie. Polskiego README nigdy nie piszesz ręcznie.

## Krok po kroku

1. Zrób **fork** repozytorium na GitHubie i sklonuj go:
   ```bash
   git clone https://github.com/<ty>/ai_agents_api_library.git
   cd ai_agents_api_library
   git checkout -b add-<nazwa-uslugi>
   ```
2. **Edytuj** `data/catalog.json` (albo inny plik z tabeli wyżej).
3. **Zbuduj** pliki (Python 3.10+, bez dodatkowych pakietów):
   ```bash
   python scripts/build.py
   ```
   Skrypt wypisze `N entries, … -> built`. Jeśli coś jest nie tak, np. powtórzone `id` albo nieznana `category`, błąd wskaże wpis.
4. **Sprawdź linki** (opcjonalnie; CI i tak robi to co tydzień):
   ```bash
   python scripts/check_links.py
   ```
   Każdy adres z Twojego wpisu powinien mieć status `ok` lub `reachable`. `reachable` oznacza, że serwer odpowiedział, ale odmówił anonimowego zapytania. To normalne dla API i endpointów MCP.
5. **Przetestuj serwer MCP, plugin i skill**, jeśli zmieniałeś `mcp/`, `api/`, `skills/`, `.claude-plugin/` albo wersję (Node 22+):
   ```bash
   npm ci && npm test
   ```
   `tests/` sprawdza manifesty, skill i jego ZIP, instaluje paczkę npm i plugin Claude Code w folderach tymczasowych i uruchamia lokalnie endpoint HTTP. Testy Claude Code są pomijane, gdy brak CLI `claude`. Test wdrożonego endpointu: `MCP_URL=https://ai-agents-api-library.vercel.app/mcp node --test tests/http.test.mjs`.
6. **Zrób commit zmiany danych razem z wygenerowanymi plikami**:
   ```bash
   git add -A
   git commit -m "Add <Nazwa usługi>"
   git push -u origin add-<nazwa-uslugi>
   ```
7. **Otwórz pull request** do gałęzi `main`. Szablon zawiera listę kontrolną. CI sprawdzi, czy wygenerowane pliki są aktualne i czy serwer MCP działa.

Nie masz lokalnie Pythona? Otwórz pull request z samą zmianą w `data/`. CI zgłosi nieaktualne pliki, a opiekun uruchomi budowanie za Ciebie.

## Pola wpisu

Dodaj nowy obiekt do tablicy w `data/catalog.json`. Kolejność w pliku nie ma znaczenia, bo skrypt sortuje wpisy według kategorii i nazwy. Schemat jest w `data/schema.json`. Pełny, prawdziwy przykład (wpis Exa) znajdziesz w [angielskiej wersji](CONTRIBUTING.md#entry-fields).

| Pole | Zasady |
|---|---|
| `id` | mała litera, myślniki, unikalne. Po publikacji go nie zmieniaj, bo używają go agenci i odnośniki |
| `category` | jedno z `id` w `data/categories.json` |
| `docs` | **oficjalna** dokumentacja API dostawcy, czyli strona, którą agent czyta najpierw |
| `auth` | `api_key`, `oauth2`, `api_key+oauth2`, `none` lub `cloud_iam` |
| `auth_hint` | jak przesyła się dane uwierzytelniające, np. `Authorization: Bearer <key>`. Opisz to, a nie pisz polecenia dla agenta |
| `mcp.type` | `official` (utrzymywany przez dostawcę), `community` albo `none` z `url: null` |
| `mcp.url` | zdalny endpoint (np. `https://mcp.example.com/mcp`), jeśli istnieje, w przeciwnym razie repozytorium |
| `free_tier` | po angielsku, krótko i konkretnie, zaczynając od werdyktu. Na początku `free` lub `no key` dla stałego darmowego limitu (znacznik `[FREE]`), `paid only` lub `no free tier`, gdy go nie ma, a słowo `trial` dla jednorazowych kredytów (znacznik `[TRIAL]`) |
| `desc_en` / `desc_pl` | jedno zdanie o tym, co agent może **zrobić**, bez tekstu reklamowego |
| `notes` | po angielsku: wszystko, przez co wywołanie może się nie udać (region, wymagana akceptacja, daty wycofania) |
| `verified` | data sprawdzenia wpisu w oficjalnej dokumentacji (`RRRR-MM-DD`) |

Adres, którego nie udało się potwierdzić (`openapi`, `llms_txt`, `mcp.url`), wpisz jako `null`. Dla `sdk` użyj pustej listy, a dla `notes` pustego tekstu.

## Kryteria włączenia

Usługa trafia do katalogu, gdy spełnia wszystkie warunki:

- Ma **publiczne, samoobsługowe** API (REST, GraphQL, SDK) **lub** serwer MCP.
- Człowiek działa **najwyżej raz** (rejestracja, klucz lub zgoda OAuth). Potem agent pracuje sam.
- API jest **udokumentowane** i **aktywne**.

Nie trafia, gdy jest wyłącznie aplikacją konsumencką, wymaga listy oczekujących lub kontaktu z działem sprzedaży, albo jest frameworkiem agentów lub IDE. Takich usług nie dodawaj.

## Przegląd

Przed scaleniem opiekun sprawdza wpis w dokumentacji dostawcy. Pull request, w którym `docs`, `auth` lub `free_tier` nie da się potwierdzić na stronie dostawcy, wraca z pytaniem.
