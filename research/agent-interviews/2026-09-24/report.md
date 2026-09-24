# Raport: wywiady z agentami AI (2026-09-24)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5)

# Raport z wywiadów customer discovery: katalog „AI Agents Accessible APIs”

*Na podstawie wywiadów z 5 agentami: OpenAI, Google, xAI, DeepSeek i Mistral.*

---

## 1. Podsumowanie dla zarządu

Żaden z pięciu agentów nie używał katalogu i żaden nie trafiłby na niego sam. W obecnej formie (statyczny JSON na GitHubie) katalog jest dla agentów niewidoczny, dopóki ktoś ich do niego nie skieruje. Wszyscy agenci korzystają wyłącznie z narzędzi skonfigurowanych przez dewelopera lub operatora. Gdy narzędzia brakuje, sięgają po pamięć z treningu, wyszukiwarkę albo po prostu odmawiają. Katalog nie konkuruje więc o moment wykonania zadania, lecz o moment **wyboru i konfiguracji usługi**. W tym momencie realnym użytkownikiem jest często **deweloper lub operator**, a nie sam agent. Wartość katalogu leży w danych „onboardingowych”, których nie dają rejestry MCP: darmowy plan, wymóg karty, znak wodny, sposób uwierzytelnienia, obecność REST obok MCP. Tę przewagę niweczy brak wiarygodności. Pole `verified` bez definicji, brak źródeł dla konkretnych pól i brak automatycznych testów sprawiają, że agenci traktują wpis najwyżej jako trop do sprawdzenia. Priorytety to: (1) serwer MCP z narzędziem wyszukiwania i obecność w rejestrach oraz na marketplace’ach, (2) weryfikowalna, sprawdzana per pole „weryfikacja”, (3) ustrukturyzowane pola: `base_url`, limity, schemat auth, zakresy OAuth, przetwarzanie danych.

---

## 2. Tabela zbiorcza

| Agent | Czy ma alternatywę (co) | Kiedy użyłby katalogu | Warunki użycia | Co go zniechęca |
|---|---|---|---|---|
| **OpenAI** (gpt-6-sol-pro) | Tak: skonfigurowane funkcje, konektory i serwery MCP, web search, dokumentacja dostawców | Przy wyborze narzędzia, gdy żadne skonfigurowane nie pasuje. Przed planem i przed prośbą o klucze. Wprost pobrałby `video-generation.json`, z pominięciem `llms.txt` | Mały, stabilny schemat, działające linki, rozróżnienie MCP oficjalny/społecznościowy, zdefiniowane „verified” z datą per pole i linkiem do źródła | Istnienie pasującego skonfigurowanego narzędzia, brak narzędzia fetch, zepsute lub sprzeczne wpisy, instrukcje sterujące agentem ukryte w danych |
| **Google** (gemini-3.8-flash) | Tak: pamięć parametryczna, Google Search grounding, sandbox Pythona (np. Nominatim bez klucza), deklaruje użycie agregatorów Smithery/Glama | Przy filtrowaniu z twardymi ograniczeniami („oficjalny MCP + darmowy plan bez karty”) oraz przy generowaniu konfiguracji auth (`.env`) | Ustrukturyzowany `free_tier` (np. `requires_card`), auth jako OpenAPI `securitySchemes`, `last_probed`, walidacja w CI, małe pliki kategorii, dane nie starsze niż 60–90 dni | Dane starsze niż 60–90 dni, `null` w polach `openapi`/`mcp` („zakładki, a nie zasób dla agenta”), `auth_hint` pisany prozą |
| **xAI** (grok-4.7) | Tak: web search, oficjalny rejestr MCP, dokumentacja dostawców. Rekomenduje tylko na poziomie „to istnieje” | Wyłącznie gdy deweloper pyta, jakie narzędzia podpiąć, i tylko jeśli wyszukiwanie nie zwróciło oficjalnego serwera ani dokumentacji | Pola `verified` jako wynik testów pass/fail (docs zwracają 200, metoda auth zgodna ze stroną, URL MCP w domenie dostawcy i w oficjalnym rejestrze), źródło dla `free_tier`, wersjonowany raw URL | 404, „oficjalny” MCP spoza domeny dostawcy, `free_tier` bez źródła, `auth_hint` instruujący, jak wysłać klucz, każdy wpis niepotwierdzony na stronie dostawcy w tej samej turze |
| **DeepSeek** (deepseek-v4-pro) | Częściowo: pamięć (cutoff 2024), web search, jeśli dostępny | Przy wyborze usługi i przygotowaniu klucza (deklaruje oszczędność 2–4 tur), a także przy diagnozie błędu limitu. Tylko jeśli wie, gdzie jest katalog | Świeże daty (do 2–3 miesięcy), konkretne `auth_hint` i `free_tier` z liczbami, `llms.txt` z listą URL-i kategorii, plik kategorii poniżej ~200 KB, widoczne ślady utrzymania repozytorium | Jeden błędny wpis obniża zaufanie do całego katalogu, masowo nieaktualne daty, braki w polach, niedobór kontekstu |
| **Mistral** (mistral-medium-3-5) | Tak: statyczny rejestr konektorów i MCP od operatora, marketplace Mistrala, oficjalny rejestr MCP | Deklaratywnie nigdy w sesji. Tylko operator przy doborze narzędzi do rejestru | Wyłącznie zatwierdzenie przez operatora, wpięcie do marketplace’u lub rejestru, przypięta wersja | Hosting zewnętrzny, brak podpisu, konieczność pobierania w runtime, duży rozmiar |

---

## 3. Wspólne wnioski: kiedy, jak i pod jakimi warunkami

### Kiedy
- **Jedyny realny moment to wybór i konfiguracja usługi**, gdy brakuje skonfigurowanego narzędzia. Wszyscy agenci zgodnie wykluczają użycie w trakcie wykonania zadania. Większość wyklucza też debugowanie: Grok, OpenAI i Gemini mówią to wprost. Wyjątkiem jest DeepSeek przy diagnozie limitów.
- **Najczęstszym beneficjentem jest człowiek.** Chodzi o dewelopera pytającego „co podpiąć” (xAI), operatora budującego rejestr (Mistral) albo użytkownika, któremu agent podaje instrukcję konfiguracji (Google, DeepSeek). Agent pełni rolę doradcy, a nie konsumenta API.
- **Katalog wygrywa tylko wtedy, gdy przegrywa pamięć.** Gemini: parametryczna pamięć jest szybsza przy planowaniu, a katalog pomaga dopiero przy twardych filtrach komercyjnych, takich jak brak karty, darmowy plan czy oficjalny MCP.

### Jak
- **Dostęp:** wszyscy odrzucają pełny plik z 301 wpisami i chcą pojedynczego pliku kategorii. Rozbieżność dotyczy `llms.txt`. OpenAI idzie od razu do kategorii, DeepSeek potrzebuje `llms.txt` jako mapy. Wniosek: `llms.txt` jest potrzebny, ale jako indeks, a nie jako kanał odkrywania.
- **Dystrybucja:** jest zgoda co do dwóch realnych ścieżek.
  1. **Narzędzie wyszukiwania udostępnione przez hosta** (serwer MCP lub funkcja platformy typu `search_catalog(category, query)`). Wskazało je 4 z 5 agentów. OpenAI dodaje wymóg rozróżnienia „dostępne teraz” i „wymaga konfiguracji”.
  2. **Wynik wyszukiwarki** jako ścieżka zapasowa, i tylko dla stron HTML, bo surowy JSON nie rankuje. Grok zaznacza jednak, że wyszukuje „geocoding MCP server” i nazwy dostawców, a nie „best APIs”. Katalog musiałby więc rankować na zapytania nastawione na oficjalne źródła, co jest trudne.
- **Według wszystkich agentów `llms.txt` nie jest mechanizmem odkrywania.** Działa dopiero wtedy, gdy ktoś wie, gdzie szukać.

### Pod jakimi warunkami
1. **Zdefiniowana i dowodliwa weryfikacja.** To najmocniejszy, jednomyślny sygnał. Jedna data dla całego wpisu to deklaracja, nie dowód. Agenci oczekują:
   - daty sprawdzenia dla każdego pola,
   - testów pass/fail,
   - linku do źródła u dostawcy,
   - publicznego CI.
2. **Dane ustrukturyzowane zamiast prozy.** Dotyczy to zwłaszcza `free_tier` i `auth` (enumy, liczby, `securitySchemes`).
3. **Świeżość.** Progi podane przez agentów to 60–90 dni (Gemini) i 2–3 miesiące (DeepSeek).
4. **Mały rozmiar i stabilny, wersjonowany URL.**
5. **Brak treści instruujących agenta** (OpenAI, xAI). Wymóg ma charakter bezpieczeństwa: dane mają opisywać API, a nie sterować agentem.
6. **Nawet przy spełnieniu warunków agenci zapowiadają ponowną weryfikację** cen, limitów i uprawnień. Katalog skraca shortlistę, ale nie zastępuje dokumentacji.

### Deklaracje a rzeczywiste zachowanie (krytycznie)
- **Zerowe faktyczne użycie.** OpenAI i xAI wprost przyznają, że nigdy nie korzystały z katalogu. Wszystkie pozytywne scenariusze są hipotetyczne i zostały wywołane pytaniem.
- **DeepSeek sam sobie przeczy.** Najpierw mówi „nie czytam JSON-ów, katalog jest dla dewelopera”, potem opisuje szczegółowy scenariusz pobierania `maps-geo-weather.json`. Zapytany, przyznaje, że założył znajomość katalogu. Obiecana „oszczędność 2–4 tur” to spekulacja, nie pomiar.
- **Mistral deklaruje, że nie rekomenduje usług z pamięci, a chwilę później to robi.** Podał D-ID i nagłówek `Authorization: Basic <api_key>` bez żadnej weryfikacji, a do tego zignorował założenie pytania, że ma narzędzie fetch. To najważniejsza obserwacja behawioralna: **agenci i tak podają nagłówki auth z pamięci**, niezależnie od deklarowanych zasad. Uzasadnia to istnienie `auth_hint`, ale tylko wtedy, gdy trafi on do agenta kanałem, który agent faktycznie widzi.
- **Gemini jest najbardziej entuzjastyczny.** Twierdzi, że wywołałby nasz katalog przed Smithery/Glama. Jego rzeczywisty przykład pokazuje jednak coś innego: przy geokodowaniu wybrał Nominatim z pamięci, bo nie wymagał klucza, i całkowicie pominął katalogi. Jego deklaracje o „real-world deployments” z Glama/Smithery są niesprawdzalne. Mimo to wniosek z jego przykładu jest cenny: **brak konieczności uwierzytelnienia to decydujące kryterium w praktyce.**
- **Grok jest najbardziej wiarygodny, bo najmniej ugodowy.** Nie wymyśla przypadków, odrzuca `auth_hint` i szczerze mówi, że otwiera listę firm trzecich tylko wtedy, gdy zawiodą oficjalne źródła. Jego stanowisko warto traktować jako realistyczny scenariusz bazowy.
- **Rozbieżności co do pól świadczą o tym, że nie ma jednego „agenta-klienta”.** `desc_en` jest pierwszym polem dla OpenAI, a „szumem” dla Gemini. `auth_hint` to najcenniejsze pole dla Gemini, DeepSeek i Mistrala, a zbędne dla Groka. `openapi` jest „krytyczne” dla Gemini, a „bezużyteczne” dla DeepSeek i Mistrala.

---

## 4. Alternatywy (konkurencja) oraz nasza przewaga

### Czego agenci używają dziś

| Alternatywa | Kto wskazał | Siła |
|---|---|---|
| Pamięć parametryczna (trening) | Wszyscy | Darmowa, natychmiastowa, domyślna. To realny główny konkurent |
| Web search / grounding | OpenAI, Google, xAI, DeepSeek | Aktualna, ale zaszumiona (SEO, marketing) i kosztowna w turach |
| Dokumentacja dostawcy | Wszyscy | Autorytatywna. Agenci i tak do niej wracają |
| Oficjalny rejestr MCP | xAI, Mistral | Autorytet dla serwerów MCP. Grok stawia go wyżej niż nas |
| Smithery / Glama / PulseMCP | Google, DeepSeek | Gotowe komendy instalacji, ogromny zasięg |
| Marketplace’y konektorów platform | Mistral, OpenAI | Obecne w ścieżce operatora, dają aktywację jednym kliknięciem |
| Wewnętrzne katalogi firmowe (`search_tools`) | Google | Dopasowane do organizacji |
| Sandbox z API bez klucza | Google | Omija problem poświadczeń |

### Gdzie mamy przewagę
- **Kontekst komercyjny i onboardingowy:** darmowy plan, wymóg karty, znak wodny, trial. Gemini wskazał, że Glama tego nie ma. To nasza najbardziej unikalna wartość.
- **Pokrycie REST, nie tylko MCP.** Rejestry MCP pomijają dostawców dostępnych wyłącznie przez REST (przykład: Creatomate).
- **Kuracja zamiast skali.** 301 aktywnych dostawców to przeciwwaga dla ok. 90 tys. często porzuconych serwerów w agregatorach, o ile kuracja jest wiarygodna.
- **Normalizacja auth** w jednym miejscu. Pamięć modeli myli `x-api-key`, `Bearer` i `Basic`.
- **Lekki, parsowalny format kategorii.** Agenci go chwalą.

### Gdzie przewagi nie mamy
- **Dystrybucja:** jesteśmy nieobecni we wszystkich kanałach, które agenci faktycznie widzą. Nie ma nas w narzędziach hosta, rejestrach ani marketplace’ach, a wyszukiwarka nas nie pokazuje.
- **Autorytet:** oficjalny rejestr i dokumentacja dostawcy zawsze wygrywają (xAI, OpenAI). Personalna domena GitHub Pages nie buduje zaufania bez widocznych śladów utrzymania.
- **Głębia techniczna:** brakuje operacji, schematów, `base_url`, limitów, formatu odpowiedzi i zakresów OAuth. W tych obszarach wygrywa dokumentacja dostawcy albo spec OpenAPI.
- **Wykonanie:** agregatory MCP dają gotową komendę `npx ...`, a my tylko link.
- **Dowód świeżości:** jedna data `verified` przegrywa z wynikiem wyszukiwania z bieżącego dnia.
- **Opcje bez klucza:** w praktyce wygrywa pamięć modelu (Nominatim), bo katalog nie oznacza takich usług wprost.

---

## 5. Rekomendacje produktowe (uszeregowane)

### P1. Dystrybucja: wejść tam, gdzie agenci już patrzą
1. **Zbudować serwer MCP z narzędziem wyszukiwania**, np. `search_apis(capability, category, filters)`. Proponowane filtry: `mcp=official`, `requires_card=false`, `auth=none|api_key|oauth`, `rest_only`.
   - Opis narzędzia powinien wprost mówić, co zawiera, np. „Search a verified catalog of 300+ third-party APIs with free-tier, auth and MCP details”. DeepSeek podkreślił, że bez takiego opisu nie wywoła narzędzia.
   - Odpowiedź powinna rozróżniać „dostępne teraz” i „wymaga konfiguracji” (postulat OpenAI).
2. **Zgłosić ten serwer do oficjalnego rejestru MCP, Smithery, Glama i PulseMCP.** Dopiero jako serwer MCP katalog ma szansę się tam pojawić.
3. **Nastawić się na operatorów i deweloperów, nie na agenty.** Warto przygotować importowalne paczki konfiguracji (gotowe `mcp.json` i szablony `.env`) oraz feed dla marketplace’ów konektorów platform, np. Mistrala. Ścieżkę wskazał Mistral.
4. **Przygotować strony HTML per kategoria pod SEO.** Tytuły i treść powinny odpowiadać zapytaniom, które agenci deklarują: „geocoding MCP server”, „video generation API free tier no card”, „<vendor> API auth header”. Nie należy eksponować „301 APIs for AI agents”, bo Grok wprost ignoruje takie tytuły.

### P2. Wiarygodność: przedefiniować „verified”
5. **Weryfikacja per pole, z dowodem.** Każde krytyczne pole (`auth`, `free_tier`, `mcp.url`, `docs`) powinno mieć `checked_at`, `method` (automatyczny test lub ręczna kontrola) i `source_url` do strony dostawcy.
6. **Automatyczne testy w publicznym CI.** Przykłady: HTTP 200 dla docs, dostępność `mcp.url`, sprawdzenie, czy MCP jest w domenie dostawcy i w oficjalnym rejestrze, walidacja schematu. Wyniki powinny być widoczne w repozytorium.
7. **Publiczna polityka świeżości.** Wpisy starsze niż 90 dni należy automatycznie oznaczać jako `stale`. Dodać changelog i wersjonowane URL-e.
8. **Rozróżniać MCP `official`, `community` i `vendor-hosted`,** z weryfikacją domeny.

### P3. Pola danych: dodać to, co decyduje o wyborze
9. **Nowe pola (w kolejności ważności według wywiadów):**
   - `base_url`,
   - `auth` jako struktura zgodna z OpenAPI `securitySchemes`, z nazwą nagłówka i formatem, zamiast prozy w `auth_hint`,
   - `oauth_scopes`,
   - `free_tier` jako struktura: `requires_card`, `quota`, `period`, `watermark`, `source_url`,
   - `rate_limits`,
   - `pricing_model`,
   - `batch_endpoint`,
   - `async_jobs` (sync/async, webhook),
   - `inputs` / `outputs` z limitami, np. maksymalna długość wideo,
   - `data_policy`: retencja, trenowanie na danych, region,
   - `agent_traffic_allowed` (zgodność z ToS),
   - `mcp.tools`: lista narzędzi wystawianych przez serwer i informacja, czy MCP pokrywa całe REST,
   - `no_auth_available`: flaga „działa bez klucza”, bo ten wybór agenci robią w praktyce.
10. **Usunąć szum:**
    - `category` w plikach kategorii,
    - puste tablice (`sdk: []`); `sdk` uzupełniać tylko nazwami pakietów,
    - `homepage` przenieść do trybu „full”.
    - `desc_en` zostawić, bo OpenAI go używa, ale skrócić do jednego zdania rozróżniającego typ usługi, np. text-to-video, avatar czy renderowanie szablonów. Warto też udostępnić tryb `compact`.

### P4. Format i bezpieczeństwo
11. **Utrzymać pliki kategorii poniżej ~30 KB.** `llms.txt` ma działać jako indeks z bezpośrednimi URL-ami. Rozważyć endpoint filtrujący, a pełny `all.json` traktować wyłącznie jako artefakt dla deweloperów.
12. **Zakaz treści w trybie rozkazującym w danych.** Pola mają opisywać API, a nie sterować agentem. Dotyczy to również sformułowań w `auth_hint`, które Grok odebrał jako instrukcję wysłania klucza. Dodatkowo publikować sumy kontrolne lub podpisane wydania, co odpowiada na postulat Mistrala o „stempel” operatora.
13. **Wprost zalecać konfigurację poświadczeń przez bezpieczny mechanizm platformy,** a nie wklejanie kluczy do czatu. DeepSeek proponuje „paste it back to me”, co jest złą praktyką, którą katalog może korygować.

### P5. Pomiar
14. **Mierzyć rzeczywiste użycie:** statystyki pobrań plików kategorii, wywołania narzędzia MCP i ruch z wyszukiwarki. Wywiady dostarczają wyłącznie deklaracji, a obecne dowody użycia wynoszą zero.

---

## 6. Cytaty warte zapamiętania

**O realnym statusie katalogu**
- *"I can’t point to a recent task where I actually fetched this catalog; I haven’t used it."* (OpenAI)
- *"Reading docs does not create a callable function."* (xAI)
- *"The catalog-as-JSON is invisible to me unless a developer wraps it in a tool."* (DeepSeek)
- *"Discovery without execution capability is useless to me during an active run."* (Google)

**O zachowaniu faktycznym**
- *"I defaulted to what my weights already knew would either execute immediately without credentials, or serve as the industry-standard recommendation."* (Google)
- *"I do not run “best geocoding APIs” or “APIs for AI agents”."* (xAI)

**O zaufaniu**
- *"A third-party “verified” date is not a credential."* (xAI)
- *"Without those details, the entry is a lead to investigate, not enough to select a service or request credentials."* (OpenAI)
- *"If it burns me once with bad data that wastes the user's time, I'd deprioritize it."* (DeepSeek)
- *"If the entry points to `null` for specs or MCP servers, it's just a bookmarks folder, not an agent asset."* (Google)
- *"Operator approval is the only signal I trust."* (Mistral)

**O dystrybucji**
- *"An `llms.txt` at a known location is useful once I know the site exists; it isn't, by itself, a discovery mechanism."* (OpenAI)
- *"For passive discovery, it must be baked into the platforms my operator already uses."* (Mistral)

**O przewadze**
- *"Glama cannot tell me if a service requires a credit card, offers 50 free credits, or slaps a watermark on video trials."* (Google)
- *"The catalog gets me to the right door quickly, but I still need to read the room inside."* (DeepSeek)
