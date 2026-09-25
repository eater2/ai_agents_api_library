# Raport: wywiady z agentami AI (2026-09-25)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5)

# Raport z wywiadów discovery: katalog „AI Agents Accessible APIs”

## 1. Podsumowanie dla zarządu

Żaden z pięciu agentów nie użyje katalogu spontanicznie. Każdy pracuje na narzędziach nadanych przez hosta: function calling, podłączone MCP, wyszukiwarka i wiedza z treningu. Katalog trafi do agenta tylko wtedy, gdy deweloper lub platforma skonfiguruje jego serwer MCP albo gdy strona katalogu wygra w wynikach wyszukiwania z nazwą konkretnego vendora, co agenci oceniają jako mało prawdopodobne. Tam, gdzie agenci już katalog mają, używają go wąsko: do shortlisty przy wyborze usługi i do przygotowania prośby o klucz. Nie traktują go jako źródła prawdy, a finalistę i tak sprawdzają w dokumentacji vendora. Nasza realna przewaga to metadane komercyjne i „tarciowe”, których nie mają rejestry MCP: wymóg karty, watermark, trial kontra darmowy tier, asynchroniczność oraz lista REST API bez uwierzytelnienia. Ta przewaga jest dziś podkopywana przez błędy w danych. Dwaj najbardziej wiarygodni rozmówcy (OpenAI, xAI) sami wskazali sprzeczność w Akool (`has_free_tier: true` przy „API access is paid only”) oraz „uptime”, który liczy odpowiedzi 401 i 404 jako „up”. Pojedynczy fałszywy flag free, `no_auth` lub `requires_card` jest według agentów powodem do porzucenia katalogu na stałe. Dlatego priorytetem nr 1 jest jakość i spójność danych, a dopiero potem dystrybucja: wpis w rejestrze MCP, strony per operacja oraz pozyskanie deweloperów i platform jako kanału.

## 2. Tabela zbiorcza

| Agent | Czy już ma alternatywę (co) | Kiedy użyłby katalogu | Warunki użycia | Co go zniechęca |
|---|---|---|---|---|
| **OpenAI** (gpt-6-sol-pro) | Narzędzia sesji, konektory, skonfigurowane MCP, web search (jeśli włączony). Uczciwie zaznacza, że w tej rozmowie nie ma żadnych narzędzi. | Planowanie (shortlista po `operations`), wybór spośród kilku kandydatów, sprawdzenie typu poświadczeń/scope przed prośbą o klucz, generowanie hipotez przy debugowaniu | Musi mieć dostęp w sesji. Mały wynik per zadanie zamiast 328 wpisów. Stabilne ID, daty sprawdzenia per pole, jasna tożsamość wydawcy, niezawodne HTTPS | Stare pola cenowe/auth. Katalog wolniejszy od wyszukiwarki. Uptime liczący 401/404 jako „up”. Sprzeczności free-tier. **Stop na całe zadanie:** prośba o przesłanie klucza użytkownika do wydawcy |
| **Google** (gemini-3.8-flash) | Statyczne deklaracje narzędzi, sandbox Pythona, Google Search grounding, pamięć parametryczna (Nominatim „z głowy”) | Wybór usługi (filtr `no_auth`/free, żeby wykonać zadanie „po cichu” w sandboxie). Pisanie wywołania i instrukcji dla użytkownika (`auth_scheme`, `call.example`, `call.async`) | Granularne zapytania (300–500 tokenów), MCP `search_apis`/`get_api`. Dokładny kontrakt auth. Zsyntetyzowany status zdrowia (operational/degraded/failing) lub filtr po stronie serwera | Fałszywy `no_auth` (jeden wystarczy). Niedziałający `call.example`. Błędnie podany `requires_card`. Surowe logi probe w kontekście |
| **xAI** (grok-4.7) | Web search + page fetch, wiedza własna, zbindowane funkcje/MCP. Rejestry (Smithery, oficjalny MCP) tylko gdy zadanie brzmi „znajdź serwer MCP” | Wyłącznie planowanie i wybór, gdy brak zbindowanego narzędzia i znanego dopasowania. Przy prośbie o klucz tylko nazwa nagłówka i info o karcie | Każde twierdzenie z source URL i datą. Booleany wyliczalne z cytowanego źródła. Świeżość pól w tygodniach. Kilkaset usług. Raw JSON z GitHuba z sumami kontrolnymi | **Nie zainstaluje naszego MCP** i nie wyśle klucza przez bramkę strony trzeciej. Porzuca na stałe po jednej klasie błędu: źródło mówi co innego, płatne sprzedane jako darmowe, community MCP podane jako vendor-hosted. Porzuca też, gdy jedyny dostęp prowadzi przez nasz serwer |
| **DeepSeek** (deepseek-v4-pro) | Deklaruje: function calling, MCP, „plugin stores”, oficjalny rejestr MCP, Smithery/Glama, web search. Później przyznaje, że nie podłączy MCP bez użytkownika | Wybór narzędzia (category JSON + filtry), krok z poświadczeniami, debugowanie (`call`, `async_jobs`, `uptime`) | Świeżość per pole, jawna głębokość weryfikacji (czy ktoś wykonał curl), pliki per kategoria, ustrukturyzowane auth (typ/nagłówek/prefiks) | 401 po zastosowaniu `auth_hint` (dwa w sesji = koniec na sesję, trzy łącznie = koniec na stałe). Pola niesprawdzane dłużej niż 14 dni |
| **Mistral** (mistral-medium-3-5) | Deklaruje zapytania do oficjalnego rejestru MCP, Smithery, APIs.guru, prekonfigurowane MCP. Twierdzi, że nie robi web search | Wybór narzędzia, gdy rejestr zwraca mało wyników (niszowe `operations`). Debugowanie 401/403/429 | Wyłącznie przez MCP (wpis w rejestrze z trafnymi słowami kluczowymi). Świeżość ≤30 dni. `source_url`/`checked_at`. Publiczny stabilny URL. ≤5 MB | Brak ekspozycji przez MCP („I'd ignore it”). Dedykowany serwer zawsze wygrywa, katalog to „last resort”. Brak pól debugowych |

## 3. Wspólne wnioski: kiedy i jak agenci użyją bazy

### 3.1. Najpierw wiarygodność samych wypowiedzi

Część odpowiedzi to uprzejmość albo konfabulacja, a nie opis realnego zachowania. Rozróżniamy to wprost.

- **OpenAI i xAI: najbardziej wiarygodni.** Odmówili wymyślenia „ostatniego razu”, bo nie mają pamięci między sesjami. Wskazali konkretne błędy w naszych danych i opisali ograniczenia uprawnień. Ich opinie ważymy najwyżej.
- **Google: mieszany.** Analiza pól i dystrybucji jest trafna, ale dwa elementy są niewiarygodne:
  - anegdota „Recently, a user needed coordinates…” (model nie ma takiej pamięci),
  - statystyka „20–30%” nieaktualnych wyników wyszukiwania, która wygląda na zmyśloną.
- **DeepSeek: najbardziej „przytakujący”.** Opisał „ostatnie zadanie” z dostępem do „plugin stores” i rejestrów, a potem przyznał, że nie może sam podłączyć MCP. Mówi „the catalog has this” o per-field freshness, a w następnej odpowiedzi chce usunąć `source_url`/`checked_at`, bo „ufa booleanom”. Reguły „2 błędy = koniec sesji, 3 = koniec na zawsze” to deklaracja, nie mechanizm.
- **Mistral: najsłabsza wiarygodność.** „Ostatnie wyszukiwanie w rejestrze” zwróciło D-ID i Creatomate z detalami (3 minuty z watermarkiem, 50 kredytów jednorazowo), które pochodzą z naszej próbki, a nie z rejestru MCP. Sam sobie przeczy w sprawie `operations`: najpierw „lets me match the task precisely”, potem „not actionable”. Wycofał się z zapytania o nazwę katalogu, gdy wskazano mu nielogiczność.

**Wniosek:** entuzjazm DeepSeeka i Mistrala („would have replaced most of that verification step”) nie jest dowodem popytu. Realne zachowanie opisują OpenAI i xAI: katalog to co najwyżej lista kandydatów, a weryfikacja zostaje po stronie vendora.

### 3.2. Kiedy katalog jest używany

1. **Tylko gdy brak już podłączonego narzędzia.** To zgodne stanowisko 5 na 5. Jeśli host zbindował geocoder lub generator wideo, katalog nie jest pobierany.
2. **Tylko dla nieoczywistych zdolności.** Znane API (GitHub, Stripe, Wikipedia, arXiv, Nominatim) agenci obsługują z pamięci. Katalog ma wartość w „długim ogonie”: text-to-video, avatar video, niszowe operacje.
3. **Etap: shortlista i wybór.** Wszyscy wskazują ten etap. Drugi, słabszy etap to przygotowanie prośby o poświadczenia: jaki nagłówek, jaki scope, czy wymagana karta.
4. **Debugowanie: raczej nie.** Google i xAI mówią wprost „nie”, OpenAI tylko do hipotez. Deklaracje DeepSeeka i Mistrala są słabo wiarygodne. Przy błędzie wygrywają treść odpowiedzi i aktualna dokumentacja.
5. **Weryfikacja zawsze na końcu.** OpenAI i xAI sprawdzą dokumentację vendora przed prośbą o klucz. Katalog skraca research, ale go nie zamyka.

### 3.3. Jak katalog jest pobierany

- **Nikt nie pobierze `all.json`.** Zgodnie 5 na 5 agenci chcą wąskich zapytań: per operacja, per kategoria albo `get_api(id)`.
- **Kanał zależy od architektury agenta:**
  - OpenAI i Google: skonfigurowane przez dewelopera lub platformę MCP (najbardziej realne), dalej wyszukiwarka.
  - xAI: wyłącznie wyszukiwarka i raw JSON. Nasz MCP odrzuca.
  - Mistral: wyłącznie MCP lub rejestr.
  - DeepSeek: rejestr albo znany URL.
- **Konsekwencja:** potrzebujemy obu kanałów jednocześnie: statycznych plików i MCP. Żaden sam nie wystarczy.
- **`llms.txt` nie jest kanałem odkrycia.** Nikt nie odpytuje go proaktywnie. Działa co najwyżej jako mapa po tym, jak agent już trafił na stronę.

### 3.4. Przy jakich warunkach

- **Spójność danych.** Booleany muszą wynikać z prozy i cytowanego źródła (xAI, OpenAI).
- **Świeżość per pole**, szczególnie cen, free tieru, auth, scope i endpointów. Horyzont to tygodnie, nie „last checked” dla całego katalogu.
- **Jawny poziom weryfikacji.** Agenci chcą wiedzieć, czy ktoś faktycznie wykonał wywołanie, czy tylko sprawdził link (DeepSeek, Google, OpenAI).
- **Bezpieczeństwo.** Zero proszenia o klucze i zero proxy/bramki. Dla xAI i OpenAI to warunek brzegowy.
- **Jasna tożsamość wydawcy**: vendor czy niezależna kuracja (OpenAI).

### 3.5. Co zabija zaufanie

Agenci wskazali progi jednorazowe, czyli jeden przypadek wystarczy:

- fałszywy `no_auth`,
- fałszywe „free” (płatne sprzedane jako darmowe),
- błędny `requires_card`,
- niedziałający `call.example`,
- zły nagłówek auth,
- community MCP opisany jako vendor-hosted,
- źródło, które nie mówi tego, co wpis,
- **prośba o klucz użytkownika** (OpenAI: natychmiastowe porzucenie na całe zadanie).

## 4. Alternatywy (co agenci już mają) i nasza przewaga

### 4.1. Co już mają

- **Narzędzia nadane przez hosta:** function calling, konektory, prekonfigurowane MCP. To zawsze pierwszy wybór.
- **Web search + dokumentacja vendora.** Domyślna ścieżka dla OpenAI, Google i xAI. Zapytanie z nazwą vendora („D-ID talking avatar API”) wyprzedza w rankingu katalogi stron trzecich.
- **Pamięć parametryczna.** Pokrywa popularne, stabilne API.
- **Oficjalny rejestr MCP, Smithery, Glama, APIs.guru.** Deklarują je Mistral i DeepSeek. xAI sięga po nie tylko na wyraźne polecenie.
- **Sandbox z kodem** (Google). Pozwala wywołać REST bez żadnej infrastruktury MCP.

### 4.2. Gdzie mamy przewagę

| Przewaga | Kto to potwierdza |
|---|---|
| **Ograniczenia komercyjne i „tarcie”:** `requires_card`, watermark, trial jednorazowy kontra stały free tier, cena jednostkowa. Rejestry MCP są na to „completely blind” | Google (najmocniej), DeepSeek, Mistral |
| **REST API, nie tylko serwery MCP.** Zwłaszcza 21 endpointów `no_auth`, które agent z sandboxem wywoła od razu bez konfiguracji | Google |
| **Mechanika wywołania:** `auth_scheme` (nagłówek), `base_url`, `call.async` (polling, statusy), `response_fields` | Wszyscy |
| **Słownik `operations`:** dopasowanie zadania do usługi precyzyjniej niż słowa kluczowe w rejestrze | OpenAI, xAI, Mistral (niekonsekwentnie) |
| **Rozmiar kuracji.** Kilkaset usług to według xAI „the right size”. Dziesiątki tysięcy to szum, który agent i tak ma w wyszukiwarce | xAI |

### 4.3. Gdzie przewagi nie mamy

- **Świeżość.** Aktualna dokumentacja vendora zawsze wygrywa. Nasze `checked_at` to „leads, not proof”.
- **Wykonanie.** Katalog nie daje narzędzia, uprawnień ani poświadczeń. Podłączony konektor wygrywa zawsze.
- **Popularne API.** Pamięć modelu wystarcza.
- **Dedykowany serwer MCP.** Gdy obok siebie w rejestrze pojawią się katalog i `nominatim-mcp`, agent wybierze ten drugi (Mistral).
- **Pola potrzebne do realnego wywołania.** Wszyscy i tak idą po nie do dokumentacji: schematy requestów (np. klucze `modifications`, ID szablonów), formaty błędów 400/422/429, paginacja, schematy webhooków i ich podpisywanie, granularne scope OAuth, limity wejścia, retencja danych.
- **Dystrybucja.** Nie jesteśmy wbudowani w żadną platformę ani wpisani do rejestru. W wyszukiwarce przegrywamy z nazwą vendora.
- **Liveness.** Obecny „uptime” (2 próbki w „30-dniowym” oknie, 401/404 liczone jako „up”) jest przez agentów oceniany jako bezwartościowy, a nawet szkodliwy dla wiarygodności.

## 5. Rekomendacje produktowe (uszeregowane)

### P1. Jakość danych, bo bez niej reszta nie ma sensu

1. **Walidator spójności w CI.** Booleany (`has_free_tier`, `has_trial`, `no_card`, `no_auth`) mają być wyliczane z ustrukturyzowanego źródła, a nie ustawiane ręcznie. Build ma się wywalić przy sprzeczności z prozą. Najpierw naprawić Akool.
2. **Rozbić „free” na rozłączne pola:**
   - `api_access_free` (czy darmowy plan obejmuje API),
   - `trial_type: one_time_credits | time_limited | none`,
   - `recurring_free_quota`,
   - `requires_card`,
   - `watermark`.
   To dokładnie te miejsca, w których agenci złapali błędy.
3. **Uczciwy poziom weryfikacji per wpis i per pole:** `verification_level: link_reachable | docs_read | example_executed_unauthenticated | authenticated_call_ok`, plus kto weryfikował (bot lub człowiek) i kiedy. Dziś `verified` sugeruje więcej, niż faktycznie sprawdzamy.
4. **Weryfikowalny status MCP:** `vendor-hosted` tylko z dowodem (link z domeny vendora), w pozostałych przypadkach `community`. Pomyłka tu to według xAI powód do porzucenia katalogu na stałe.

### P2. Liveness: zredefiniować albo ukryć

5. **Przestać liczyć 401/404 jako „up”.** Wprowadzić rozróżnienie: `reachable_auth_required`, `not_found`, `ok`, `error`.
6. **Wyeksponować jeden zsyntetyzowany status:** `health: operational | degraded | failing | unknown`, wraz z liczbą próbek. Surowe logi przenieść do osobnego widoku.
7. **Nie nazywać 2 próbek „30-day uptime”.** Albo zwiększyć częstotliwość, albo zmienić etykietę.
8. **Docelowo:** syntetyczny probe z testowym kluczem dla kluczowych operacji. To realnie odróżniłoby nas od wyszukiwarki.

### P3. Format i granularność pobierania

9. **Pliki i endpointy per `operation`,** nie tylko per kategoria. `all.json` zostawić dla hurtowych odbiorców, ale nie promować go agentom.
10. **Dwa widoki wpisu:**
    - „selection view” (~300 tokenów: opis, `operations`, flagi komercyjne, health, typ auth),
    - „call view” (`base_url`, auth w strukturze typ/nagłówek/prefiks, `call`, `async`, `rate_limits`, błędy).
    Pola, które agenci wskazali jako szum dla wyboru (`sdk: []`, `llms_txt: null`, `homepage`, surowy `link_check`, pusty blob MCP), pomijać, gdy są puste, albo przenieść do widoku pełnego.
11. **Filtry po stronie serwera w `search_apis`:** `no_auth`, `api_access_free`, `requires_card=false`, `health=operational`, `mcp.kind`. Google chce, żeby filtrowanie odbywało się „before tokens hit my context window”.
12. **Stabilne ID, wersjonowane wydania, sumy kontrolne i changelog** dla raw JSON na GitHubie. To warunek xAI dla odczytu bez naszego MCP.

### P4. Nowe pola danych, w kolejności częstości wskazań

13. **Format błędów** (400/422/429/5xx: przykładowe body). Wskazało go 4 na 5 agentów.
14. **`rate_limits` jako obowiązkowe pole**, z informacją „vendor nie publikuje”, gdy brak danych. Brakowało go w Akool i D-ID.
15. **`unit_price` w strukturze** (waluta, jednostka, kwota, np. za sekundę lub za render) zamiast prozy.
16. **Wskaźnik do schematu requestu** (OpenAPI/sekcja docs dla kluczowej operacji), limity wejścia, schemat i podpisywanie webhooków.
17. **Scope OAuth per operacja, paginacja, `data_policy`** (retencja, trening na danych). To ostatnie jest ważne przy wideo z twarzą i głosem.
18. **`mcp.tools` kompletne** dla każdego serwera MCP. Brakowało ich w D-ID.

### P5. Bezpieczeństwo i tożsamość

19. **Jawna, maszynowo czytelna deklaracja:** katalog nigdy nie przyjmuje, nie proxuje i nie prosi o klucze użytkownika, a MCP katalogu jest read-only. Umieścić ją w `llms.txt`, w opisie MCP i w README.
20. **Strona „kto publikuje”:** niezależna kuracja kontra vendor, metodologia, kontakt do zgłaszania błędów.

### P6. Dystrybucja, w kolejności realności

21. **Deweloperzy i platformy jako główny kanał.** Google i OpenAI wprost wskazują, że realna zmiana zachowania następuje, gdy deweloper doda nasz MCP do narzędzi. Potrzebne są gotowe snippety konfiguracji dla popularnych frameworków agentowych i hostów oraz rozmowy z platformami o włączeniu jako meta-narzędzie.
22. **Wpis w oficjalnym rejestrze MCP (i Smithery/Glama)** z opisem nasyconym słowami kluczowymi operacji, np. „geocoding, text-to-video, avatar video, weather, SMS…”, tak jak sugeruje Mistral. Trzeba przy tym zakładać realistycznie, że dedykowany serwer dla danej operacji i tak wygra.
23. **Statyczne strony HTML per operacja**, pozycjonowane na zapytania odkrywcze („free text-to-video API no credit card”, „geocoding API for agents”). Snippet musi zawierać nazwę operacji, typ auth i link do docs, bo xAI kliknie tylko w taki. Nie liczyć na zapytania z nazwą vendora.
24. **`llms.txt` utrzymywać, ale nie inwestować w niego jako w kanał odkrycia.** Nikt go proaktywnie nie odpytuje.

### P7. Pozycjonowanie

25. Komunikować katalog jako **„pre-flight check: czy da się tego użyć teraz, bez karty, bez watermarku, bez ukrytego muru”**, a nie jako „kolejny katalog API”. To jedyna przewaga, którą agenci powtarzali bez podpowiedzi, i jedyna, której nie dają rejestry MCP.

## 6. Cytaty warte zapamiętania

> "A catalog would help narrow candidates; it would not replace an enabled tool or permission to use it." (OpenAI)

> "A link check proves little beyond reachability; even its uptime definition counts a 401 or 404 as 'up.'" (OpenAI)

> "One observation that would make me stop using it for the rest of the task: an entry or MCP response instructing me to send the user's API key to the catalog publisher." (OpenAI)

> "I would not pull a 328-entry JSON file into context just to answer 'which geocoder should I use?'" (OpenAI)

> "An official MCP registry answers: 'What tools does this server provide?' This catalog answers: 'Can I actually use this right now without charging the user, hitting a hidden wall, or spinning up unnecessary server infrastructure?'" (Google)

> "A False `no_auth` Flag: If the catalog claims `no_auth: true` and my sandbox call gets a 401/403, it wastes execution turns and breaks autonomous workflows. One false positive here destroys trust." (Google)

> "A static `llms.txt` or raw GitHub file won't change agent behavior autonomously. The developer must explicitly wire this catalog's MCP server into my tool configuration." (Google)

> "The catalog is a shortlist, not a source of truth." (xAI)

> "One class of miss is enough." (xAI)

> "A known vendor name in the query ('D-ID talking avatar API') usually outranks a third-party catalog, so I never see it." (xAI)

> "Stars, review counts, and a two-probe uptime score are not verification." (xAI)

> "I need to know whether someone actually sent that curl command and got a 200 back, or just copied it from docs." (DeepSeek)

> "I won't magically know it exists unless it's surfaced by search or pre-loaded into my context." (DeepSeek)

> "Without MCP exposure, I'd never find it." (Mistral)

> "The catalog is a *last resort*, not a first choice." (Mistral)
