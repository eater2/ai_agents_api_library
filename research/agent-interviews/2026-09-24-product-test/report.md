# Raport: test produktu z agentami AI (2026-09-24)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5), Alibaba (Qwen) (qwen/qwen3.8-max-0902), Moonshot AI (moonshotai/kimi-k3)

Materiał pokazany agentom: `material.txt` w tym katalogu.

# Raport z testów agentów: katalog API (MCP + skill)

## 1. Podsumowanie

W obecnej postaci żaden z 7 agentów nie potraktowałby wyników katalogu jako podstawy do działania bez samodzielnej weryfikacji. Czterech (Gemini, DeepSeek, Mistral, Qwen) wywołałoby `search_apis` jako pierwszy krok. Robią to jednak głównie dlatego, że skill im to nakazuje, a nie dlatego, że widzą w tym wartość. Gemini przyznaje wprost, że w nowej sesji zawoła narzędzie znowu, bo nie pamięta poprzednich rozczarowań. Główną blokadą, którą wskazało 6 z 7 agentów, jest brak zaufania do trafności wyników. W zadaniu 1 zero z pięciu wyników generuje wideo z tekstu. W zadaniu 3 na pierwszym miejscu jest LINE, a 3 z 5 wyników to nie SMS. W zadaniu 2 regułę skilla „prefer no_auth” przyciąga Nominatim, którego własny opis zakazuje pracy wsadowej. Drugą barierą jest to, że `get_api` nie zawiera informacji operacyjnych (base URL, endpoint, przykładowe żądanie, cena za operację, limity), więc każda ścieżka i tak kończy się w dokumentacji dostawcy. Kilku agentów (OpenAI, Grok, Kimi) zauważa, że słowo „verified” przy wynikach, które sprawdzono tylko pod kątem działania linków, pogarsza zaufanie zamiast je budować.

## 2. Tabela agentów

| Agent | Użyje? | W którym momencie | Główna blokada | Czego brakuje |
|---|---|---|---|---|
| **OpenAI** (gpt-6-sol-pro) | warunkowo | Tylko przy szukaniu dostawcy, gdy nie ma podłączonego narzędzia. Dla prostego klipu w zadaniu 1 nie woła wcale (robi animację SVG + FFmpeg). Nie poprosiłby użytkownika o podłączenie serwera dla jednego zadania. | Zaufanie do dopasowania wyniku do zadania | Egzekwowanie ograniczeń zadania (operacja, wolumen, budżet), oznaczanie wyników jako „ineligible” z powodem, pola operacyjne, rozróżnienie trial / free, link do konkretnej sekcji dokumentacji przy każdym twierdzeniu |
| **Google** (gemini-3.8-flash) | tak (z inercji skilla), ale szybko porzuca | Pierwszy krok, bo skill wymienia „make a 5-second video” dosłownie. Po 2 złych zapytaniach w sesji przechodzi na web search. | Zaufanie (trafność i metadane). Dziś uważa narzędzie za „negative utility”. | Twarde tagi funkcji, pusta lista zamiast szumu, `mcp_config` (transport, command, env), podział `has_permanent_free_tier` / `has_trial_credit` |
| **xAI** (grok-4.7) | nie (dziś) | Przyznaje, że treść skilla skłoniłaby go do wywołania przed web search, ale na podstawie tych wyników „would not use this one”. Wróciłby, gdyby ranking był wiarygodny. | Zaufanie. „Verified” oznacza sprawdzenie linku, a nie przydatności. | Filtrowanie po czynności, brak dopełniania listy przy pustym wyniku, limity obciążenia w polach strukturalnych (bulk, rps) |
| **DeepSeek** (deepseek-v4-pro) | warunkowo | Woła od razu po sprawdzeniu narzędzi. Gdy ma web search, uznaje go za szybszy („Path B”). | Nakładanie się z web search (w praktyce też zaufanie) | Kompletne `get_api` (base_url, endpoint, method, auth, przykład, cennik per kraj, rate limit). Oczekuje świeżości do 14 dni, co jest nierealistyczne. |
| **Mistral** (mistral-medium-3-5) | tak (deklaratywnie) | Pierwszy krok przed web search. Chce nawet mocniejszego „use FIRST”. | Zaufanie do danych | Endpoint, `batch_support`, `credit_cost`, pola pokrycia, `known_gaps`. **Uwaga:** najwięcej błędów merytorycznych w odpowiedziach (patrz sekcja 3), więc to „tak” ma niską wartość dowodową. |
| **Alibaba** (qwen3.8-max) | tak / warunkowo | Po sprawdzeniu narzędzi. Kolejność: ponowienie z `category`, potem plik JSON kategorii, na końcu web search. „Wciąż wołam, bo tanie”, ale po jednej takiej porażce jak w zadaniu 1 porzuca narzędzie dla danego zadania. | Zaufanie (trafność wyszukiwania) | Działające żądanie w `get_api`, poprawny format auth, rozdzielenie free tier i trial, flaga `no_card` |
| **Moonshot** (kimi-k3) | nie (do odkrywania) / warunkowo (do szczegółów) | Nie woła jako pierwszego. Najwyżej `get_api` po wybraniu kandydata z własnej wiedzy. Do wyboru serwera MCP woli rejestr platformy. | Zaufanie. „Katalog, który muszę weryfikować, jest przydatny tylko wtedy, gdy go nie potrzebuję.” | Pole `operations`, etykieta `match: exact/adjacent/none`, data sprawdzenia funkcji, free tier w jednostkach operacji, informacja o lukach w pokryciu |

**Co agenci naprawdę zrobią, a co jest grzecznością:**
- Deklaracje „użyję jako pierwszego” (Gemini, Mistral, DeepSeek) wynikają z posłuszeństwa wobec instrukcji skilla, a nie z oceny wartości.
- Mocniejsze słowa skilla dadzą więcej wywołań, ale przy obecnej jakości także więcej złych rekomendacji. Nie ma w tym zysku.
- Najbardziej wiarygodne są odpowiedzi OpenAI, Grok, Kimi i Qwen. Są spójne z tym, co agenci faktycznie zrobili z wynikami.
- Gemini jest wewnętrznie sprzeczny: raz mówi „web search from step one”, raz „still call first”. Po dopytaniu rozstrzyga, że w nowej sesji zawoła znowu.

## 3. Błędy i słabości w wynikach wyszukiwania

### Zadanie 1: wideo 5 s z promptu, bez budżetu (`"generate video from text prompt"`, `free_tier: true`)

**Żaden z 5 wyników nie generuje wideo z tekstu.** Zauważyło to 7 z 7 agentów.

| Wynik | Czym jest naprawdę |
|---|---|
| Google Gemini API | Generuje tekst i obrazy. Według `get_api` jego MCP tylko przeszukuje dokumentację i nie uruchamia inferencji. |
| Mux | Enkodowanie i streaming istniejącego wideo |
| Akool | Awatary i face-swap |
| Creatomate | Renderowanie z szablonów. Jego „free trial, 50 credits” przeszedł filtr `free_tier: true` (zauważył Qwen). |
| Voyage AI | Embeddingi. Zupełny szum. |

- Wyników było 5 przy limicie 10, więc nic nie zostało ucięte poniżej (Grok). Poprawnych usług po prostu nie ma w odpowiedzi.
- Otwarte pytanie: czy brakuje ich w katalogu, czy wyciął je filtr `free_tier`? Kimi zakłada brak w katalogu, Grok zostawia to otwarte. **Do sprawdzenia po naszej stronie.**
- Oczekiwane pozycje: Runway, Luma, Kling, Pika, Veo, MiniMax/Hailuo, fal.ai, Replicate, a jako darmowe opcje społecznościowe Wan2.1 i CogVideoX na HF Spaces.
- Kategoria `video-generation` jest zanieczyszczona usługami do hostingu i szablonów (Kimi).

### Zadanie 2: geokodowanie 200 adresów w Polsce

- **Nominatim (pozycja 2, `no_auth: true`) to pułapka.** Opis wpisu mówi „bulk use prohibited, 1 rps”, a reguła skilla „prefer no_auth” kieruje właśnie do niego. Zauważyło to 6 agentów. Mistral mimo to wybrał Nominatim.
- **IP2Location (pozycja 4)** to geolokalizacja adresów IP, nie ulic. Zauważyło 7 z 7.
- **Esri** jest błędnie skategoryzowane jako `architecture-cad-bim`. Zauważyło 6.
- **Google Maps (pozycja 1):** wpis podaje „$200 monthly credit”. OpenAI zaleca weryfikację. Google zmieniło model darmowych limitów w 2025 roku, więc wpis może być nieaktualny. **Do sprawdzenia.**
- Brakuje: Mapbox, OpenCage, LocationIQ, HERE, Photon, Pelias/Geocode Earth.
- Wybory agentów: Geoapify (5 agentów), Google (DeepSeek), Nominatim (Mistral, błędnie).

### Zadanie 3: przypomnienie SMS

- **LINE jest na pozycji 1**, a LINE, WhatsApp i Discord to nie SMS. Zauważyło 7 z 7.
- **Niespójne metadane (4 agentów):** Twilio ma `has_free_tier: true`, choć tekst mówi o kredycie próbnym i `has_trial: false`. Vonage przy tym samym modelu ma `has_free_tier: false, has_trial: true`.
- **„Official MCP” Twilio** to repozytorium GitHub, a nie endpoint gotowy do podłączenia (OpenAI, Kimi, Qwen).
- **Auth Twilio** może być opisany jako `api_key`, podczas gdy w rzeczywistości to HTTP Basic (SID:Token). Qwen wywnioskował to ze schematu, nie widział wpisu. **Do weryfikacji.**
- Brakuje: Plivo, Sinch, Telnyx, AWS SNS, MessageBird.

### Uwagi przekrojowe

- Wyszukiwanie dopasowuje ogólną semantykę tematu („video”, „messaging”) zamiast konkretnej czynności („text-to-video”, „SMS”). Kimi: „results look plausible while being wrong”.
- Szczegółowy wpis Gemini ma `openapi: null`. Pola `openapi` i `llms_txt` to tylko linki, a nie specyfikacje (Grok).

**Ostrożnie z listami „brakujących” usług podawanymi przez agentów.** Pochodzą z ich pamięci i mogą być nieaktualne:
- Mistral podał Clockwork SMS i „darmowe API Pika”, po czym sam przyznał, że jego wiedza jest nieaktualna.
- Mistral polecał też LINE jako „truly free” opcję dla SMS.
- DeepSeek pominął Vonage jako drugiego dostawcę SMS.

## 4. Brakujące pola potrzebne do działającego wywołania

| Pole / informacja | Liczba agentów | Kto prosił |
|---|---|---|
| Base URL + ścieżka endpointu | 7/7 | wszyscy |
| Dokładny format auth (nagłówek vs parametr zapytania, Basic, nazwa parametru) | 7/7 | wszyscy (obecny `auth_hint` jest niewystarczający) |
| Minimalne przykładowe żądanie (parametry, body) | 7/7 | wszyscy |
| Rate limit (rps, dzienny) | 7/7 | wszyscy |
| Cena / kredyty za jedną operację (np. 1 geokod = 1 kredyt? SMS do PL) | 6 | OpenAI, Grok, DeepSeek, Mistral, Qwen, Kimi |
| Rozdzielenie stałego free tier od trialu, flaga „bez karty” | 6 | OpenAI, Gemini, Grok, DeepSeek, Mistral, Qwen |
| Pole funkcji / `operations` / etykieta dopasowania (po stronie wyszukiwania) | 6 | OpenAI, Gemini, Grok, Mistral, Qwen, Kimi |
| Konfiguracja MCP (transport, command/URL, zmienne środowiskowe) | 5 | OpenAI, Gemini, DeepSeek, Qwen, Kimi |
| Jawna informacja o luce w pokryciu / pusty wynik zamiast szumu | 5 | OpenAI, Gemini, Grok, Mistral, Kimi |
| Schemat odpowiedzi (gdzie jest lat/lon, status dostarczenia) | 4 | OpenAI, Gemini, Grok, Qwen |
| Ograniczenia trialu (np. tylko zweryfikowane numery, wymagany `From`) | 4 | OpenAI, Grok, DeepSeek, Qwen |
| Pokrycie krajowe / cennik per kraj (Polska) | 4 | OpenAI, Grok, DeepSeek, Mistral |
| Data i źródło dla każdego twierdzenia, sprawdzenie funkcji (nie linku) | 4 | OpenAI, DeepSeek, Mistral, Kimi |
| Strukturalne warunki użycia (np. `bulk_allowed`, dopuszczalny wolumen) | 2 | OpenAI, Grok |
| Obsługa batch | 2 | OpenAI, Mistral |
| Co faktycznie udostępnia MCP (np. oznaczenie „docs-only”) | 2 | OpenAI, Gemini |
| Gdzie zdobyć klucz (dashboard, rejestracja) | 2 | DeepSeek, Qwen |

**Co i tak odsyła do dokumentacji, nawet przy pełnych polach:**
- aktualne ceny, stan konta, zgody i compliance SMS, ograniczenia trialu (OpenAI);
- każde twierdzenie starsze niż około 14 dni (DeepSeek) lub starsze niż około 90 dni dla sprawdzenia funkcji (Kimi).

Wniosek realistyczny: pola operacyjne skrócą drogę do pierwszego testowego wywołania. Nie wyeliminują jednak weryfikacji cen.

## 5. Uwagi do opisów narzędzi i skilla

| Obecny tekst | Problem | Proponowana zmiana | Kto zgłosił |
|---|---|---|---|
| „Returns verified services” / „verified catalog” | Sugeruje sprawdzenie funkcji, a jest tylko sprawdzeniem linków | „Returns catalog entries with a last-checked date; verify task fit, terms and pricing in official docs.” | OpenAI, Grok, Kimi |
| „Prefer, in this order: `no_auth: true` …” | Kieruje do Nominatim przy zadaniu wsadowym | „First require a fit for the exact operation and volume; only then compare setup, cost and access. Never prefer `no_auth` if the entry's limits rule out the workload.” | OpenAI, Grok |
| „`has_free_tier: true`: the user can try it without paying” | Zlewa trial z darmowym planem | „Distinguish ongoing free usage from trial credit; check whether billing setup is required.” | OpenAI (Qwen, Gemini pośrednio) |
| „`mcp.type: "official"`: the user connects it once, then you call it as a tool” | Repozytorium GitHub to nie endpoint, a MCP Gemini to tylko wyszukiwanie w dokumentacji | „Check what the MCP exposes and whether the URL is a connectable endpoint or a repository.” | OpenAI |
| „`get_reviews` … before recommending” | Wymusza wywołanie, które nie mówi, czy API wykonuje zadanie | Usunąć z kroków obowiązkowych, zostawić jako „gdy istotne” | OpenAI, Grok |
| Opis `search_apis`: „Use when a task needs an external capability you don't have” | Brak warunku pominięcia. Warunek „Skip if connected” jest tylko w treści skilla. | Dopisać: „…after checking built-in and connected tools, and your own model. Skip if they already do the job.” | DeepSeek, Qwen |
| Lista wyzwalaczy (translation, diagrams, web search, weather) | Fałszywe trafienia, bo model sam tłumaczy i rysuje Mermaid | Usunąć zadania wykonywane natywnie. Skip: „…or your own model already does the job”. Wyzwalać przy intencji integracji, a nie przy samym temacie. | Qwen, Kimi, Gemini |
| Brak wymogu konfiguracji po stronie człowieka w opisie narzędzia | Opis sugeruje natychmiastową dostępność funkcji | „…once a human has provisioned credentials.” | Gemini, Kimi |
| Brak instrukcji sprawdzenia dopasowania | Agent może wziąć pierwszy wynik (LINE dla SMS) | „Match each result's `what` to the requested verb; ranking is not proof of fit. If none match, retry with `category`, then web search.” | Grok, Kimi, OpenAI |
| Brak wyzwalacza „naprawczego” | Nie łapie sytuacji w trakcie zadania (403, rate limit) | Dodać: „when your own direct attempt failed and an external service would unblock the task.” | Qwen |
| Brak wyzwalacza dla ryzyka | Zadania wsadowe, zerowy budżet, akcje dotykające osób trzecich | „Check quotas, terms, real cost and authorization before recommending or calling.” | OpenAI |
| „when choosing which MCP server to connect” | Przegrywa z rejestrem MCP platformy | Określić, co katalog daje ponad rejestr (free tier, auth, weryfikacja) | Kimi |
| „list_categories when you are unsure” | Za słabe. Agent zgaduje ID kategorii. | Doprecyzować, kiedy używać kategorii (patrz sprzeczność niżej) | DeepSeek |

**Sprzeczne sugestie (wymagają decyzji produktowej, najlepiej na podstawie testów A/B):**
- **Kategoria:** DeepSeek chce szukać najpierw bez kategorii. Qwen, OpenAI i Grok zawężają przez `category`.
- **Fallback do statycznych plików:** Gemini chce go usunąć (strata kontekstu). Qwen i DeepSeek cenią go jako tani krok.
- **„Use FIRST, before web search”:** Mistral chce mocniejszego nacisku. **Nie rekomendujemy tego przed poprawą trafności.** Gemini pokazał, że skill i tak wymusza wywołanie, więc mocniejszy nacisk przy obecnej jakości tylko pogłębi straty zaufania.

## 6. Rekomendacje (top 10 według wpływu)

1. **Dopasowanie po funkcji, a nie po temacie.**
   - Co zrobić: pole `operations` przy każdym wpisie (np. `text-to-video`, `sms`, `street-geocoding`), ranking po zgodności z czynnością i etykieta `match: exact/adjacent` z powodem (np. „Mux: hosting, not generation”).
   - Uzasadnienie: to blokada numer jeden dla 6 z 7 agentów, a wszystkie trzy testowe wyszukiwania zawiodły tutaj.
   - Dodatkowo: zbudować zestaw testów regresyjnych z tych trzech zapytań, z kryteriami zaliczenia zaproponowanymi przez Gemini i Grok (np. brak Voyage/Mux dla wideo, brak LINE/Discord dla SMS).
   - **Nakład: duży.**

2. **Brak dopełniania listy; jawne luki w pokryciu.**
   - Co zrobić: gdy nic nie pasuje, zwracać pustą listę z komunikatem (np. „brak darmowego text-to-video w katalogu”), a nie pięć pozycji z sąsiednich dziedzin. Dodać notę o pokryciu dla każdej kategorii.
   - Uzasadnienie: agenci wolą przewidywalną porażkę niż szum („unpredictability is worse than absence”). Pusty wynik pozwala im przejść do web search jednym krokiem.
   - **Nakład: mały do średniego.**

3. **Uzupełnienie inwentarza w kategoriach, o które najczęściej pytają.**
   - Text-to-video: Runway, Luma, Kling, Veo, MiniMax, fal.ai, Replicate.
   - SMS: Plivo, Sinch, Telnyx, AWS SNS.
   - Geokodowanie: Mapbox, OpenCage, LocationIQ, HERE.
   - Najpierw ustalić, czy w zadaniu 1 brakuje wpisów, czy odciął je filtr `free_tier`.
   - Uzasadnienie: nawet idealny ranking nie pomoże, gdy właściwej usługi nie ma w katalogu.
   - **Nakład: średni.**

4. **Strukturalne limity obciążenia i poprawka reguły „prefer no_auth”.**
   - Co zrobić: pola `bulk_allowed`, `rate_limit_rps`, dopuszczalny wolumen. Ranking i skill mają je respektować.
   - Uzasadnienie: obecna reguła skilla aktywnie kieruje agentów do usługi zakazanej dla danego zadania. To błąd, który nasz własny tekst wzmacnia.
   - **Nakład: mały** dla tekstu skilla, **średni** dla danych.

5. **Audyt i rozdzielenie „free tier” od „trial” oraz flaga `no_card`.**
   - Co zrobić: dwa pola boolowskie i ujednolicenie wpisów (Twilio vs Vonage, Creatomate).
   - Uzasadnienie: filtr `free_tier` jest dziś niewiarygodny, a „no budget” to częsty warunek użytkowników. Niespójność zauważyło 4 agentów i podważa ona zaufanie do wszystkich metadanych.
   - **Nakład: mały do średniego.**

6. **Zmiana słownictwa „verified” i rozdzielenie `link_check` od `capability_check`.**
   - Co zrobić: w opisach narzędzia i skilla używać „last checked”. Dodać osobną datę sprawdzenia, czy usługa wykonuje operację.
   - Uzasadnienie: obecne słowo wprost psuje zaufanie (Kimi: „launders link-checks into implied capability checks”).
   - **Nakład: mały** dla tekstu, **średni** dla nowego procesu weryfikacji.

7. **Pola operacyjne w `get_api` dla najczęściej wybieranych usług.**
   - Co zrobić: `base_url`, `endpoint`, `method`, dokładny format auth, minimalny przykład żądania, kluczowe pola odpowiedzi. Zacząć od około 30 najpopularniejszych wpisów.
   - Uzasadnienie: prosiło o to 7 z 7 agentów. To zamienia katalog z zakładki do dokumentacji w ostatni krok przed testowym wywołaniem.
   - Uwaga: to nie usunie weryfikacji cen, więc wpływ jest niższy niż punkty 1–5.
   - **Nakład: duży.**

8. **Poprawka tekstu opisu `search_apis` i skilla.**
   - Co zrobić: warunek pominięcia (podłączone narzędzie lub własny model), wymóg konfiguracji po stronie człowieka, instrukcja sprawdzenia dopasowania, usunięcie obowiązkowego `get_reviews`, zawężenie listy wyzwalaczy, dodanie wyzwalacza „naprawczego”.
   - Uzasadnienie: tanie, szybko ogranicza fałszywe wywołania i złe rekomendacje.
   - **Nakład: mały.**

9. **Dokładny opis MCP.**
   - Co zrobić: typ wpisu (endpoint zdalny / repozytorium do instalacji / tylko dokumentacja), gotowy snippet konfiguracji, wymagane zmienne środowiskowe, lista udostępnianych narzędzi.
   - Uzasadnienie: prosiło 5 agentów. Obecne „official MCP” dla Twilio i Gemini wprowadza w błąd.
   - **Nakład: średni.**

10. **Cena i limity w jednostkach operacji oraz źródło dla każdego twierdzenia.**
    - Co zrobić: np. „1 geokod = 1 kredyt”, „SMS do PL: X USD”, z linkiem do konkretnej sekcji dokumentacji i datą.
    - Przy okazji poprawić wykryte błędy danych: kategoria Esri, auth Twilio, kredyt Google $200.
    - Uzasadnienie: pozwala ocenić wykonalność zadania wsadowego bez opuszczania katalogu (OpenAI, Kimi).
    - **Nakład: średni do dużego**, bo wymaga ciągłego utrzymania.

**Czego nie robić teraz:** nie wzmacniać nacisku „use first before web search” (sugestia Mistral), dopóki punkty 1–4 nie są wdrożone. Nie obiecywać świeżości „do 7 lub 14 dni” (DeepSeek), bo to zobowiązanie nie do utrzymania.

## 7. Cytaty warte zapamiętania

> "a catalog I have to verify against my own knowledge is only useful to me when I don't need it." (Kimi)

> "The "verified" label makes this worse, not better: it launders link-checks into implied capability checks." (Kimi)

> "That makes results look plausible while being wrong — the worst failure mode for a tool aimed at agents." (Kimi)

> "“Verified” describes a link check, not fitness for the query." (Grok)

> "so `no_auth` is a trap here." (Grok)

> "As it stands, a wrong top hit costs more than the lookup saves, so I search the web and read the docs myself." (Grok)

> "If a specialized discovery tool requires me to cross-reference general web search just to verify whether its recommendations can actually perform the query, the tool provides negative utility." (Gemini)

> "In a brand-new session, I would still call `search_apis` first." (Gemini)

> "For an agent, unpredictability is worse than absence" (Gemini)

> "I’d use these results as leads, not as permission to act or proof that a service fits." (OpenAI)

> "Search finds candidates; it does not perform the task." (OpenAI)

> "A relevance failure gives me zero usable shortlist, so I fall back to web search anyway — meaning the tool added a step and then nothing." (Qwen)

> "No number of extra fields replaces recency" (DeepSeek)
