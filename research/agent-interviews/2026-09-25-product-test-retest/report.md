# Raport: test produktu z agentami AI (2026-09-25)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5), Alibaba (Qwen) (qwen/qwen3.8-max-0902), Moonshot AI (moonshotai/kimi-k3)

Materiał pokazany agentom: `material.txt` w tym katalogu.

# Raport z testów agentów: katalog API/MCP (search_apis, get_api, get_reviews, list_categories) i skill

## 1. Podsumowanie

Żaden z siedmiu agentów nie użyłby katalogu bezwarunkowo, ale też żaden go nie odrzucił. Wszyscy wywołaliby `search_apis` raz i wcześnie, dopiero po sprawdzeniu, że żadne wbudowane ani podłączone narzędzie nie wykona zadania. Traktują katalog wyłącznie jako **źródło shortlisty**, nie jako podstawę do wykonania wywołania. **Wszyscy siedmiu zgodnie wskazali tę samą blokadę: brak zaufania do danych.** Latencja, koszt tokenów i instalacja okazały się drugorzędne.

Zaufanie podkopały konkretne błędy w polach decyzyjnych:
- `match: exact` dla Freepika, którego przykład to image-to-video;
- `match: exact` dla Google Maps, którego MCP nie ma narzędzia do geokodowania;
- `free_tier: true` dla jednorazowego kredytu;
- `docs_only` MCP Twilio promowany dla zadania „wyślij SMS”;
- „wyprowadzone” (`derived`) adresy MCP.

Deklaracje trzeba oddzielić od faktycznego zachowania. Trzech agentów (DeepSeek, Mistral, Google) najpierw chwaliło katalog jako pierwszy krok, a pytani o blokady przyznali, że w praktyce poszliby prosto do web searcha albo do własnej pamięci. Sam dopisek w skillu „confirm limits and pricing in docs” agenci (DeepSeek, Mistral, Qwen, xAI) cytują jako **argument za pominięciem katalogu**. Żaden agent nie przeszedłby od wyniku do działającego wywołania bez otwarcia dokumentacji dostawcy. Warunkiem zmiany tego zachowania są semantycznie zweryfikowane dopasowania i przykłady wywołań przetestowane na żywym API.

## 2. Tabela agentów

| Agent | Użyje? | W którym momencie | Główna blokada | Czego brakuje |
|---|---|---|---|---|
| **OpenAI** (gpt-6-sol-pro) | warunkowo | Po sprawdzeniu podłączonych narzędzi, tylko do shortlisty. Wywołanie robi przez podłączony konektor lub dokumentację dostawcy. | Zaufanie do danych wykonawczych (endpoint, MCP, cena) | Przetestowany przykład dla konkretnej operacji, rozróżnienie „hostowany” vs „podłączony w tej sesji”, ranking pod realne zadanie |
| **Google** (gemini-3.8-flash) | warunkowo, w praktyce skłonny pominąć | Wywołał w zadaniu 1, ale uważa, że Google Search daje to samo szybciej | Zaufanie; katalog „dodaje latencję i tokeny, nie oszczędzając kroku” | Walidacja `match` i `free_tier` (flaga `trial_only`), schemat parametrów, `can_execute` dla MCP |
| **xAI** (grok-4.7) | warunkowo | Raz, wcześnie, jako pierwszy lookup przed web searchem. Ignoruje ranking. | Zaufanie: `match`, ranking, URL MCP i `covers_full_api` wymagają weryfikacji | Dopasowanie liczone, a nie etykietowane; wycena konkretnego zadania (`covers_job`); zakaz adresów `derived` |
| **DeepSeek** (v4-pro) | warunkowo, w praktyce często nie | Deklarował użycie „przed web searchem”, potem przyznał, że znane API (Twilio) obsłuży z pamięci | Zaufanie; każdy wynik i tak weryfikuje w dokumentacji | Przykład z `tested_at`, przykład dla każdej operacji, działający (nie docs-only) MCP |
| **Mistral** (medium-3-5) | warunkowo, skłania się ku nie | Po sprawdzeniu możliwości, ale uznał: „might as well start with web search” | Zaufanie: brak `unit_price`, niejasne „testing use”, docs-only MCP | `unit_price` dla każdej operacji, flaga „nadaje się do bulku”, przetestowany MCP |
| **Qwen** (qwen3.8-max) | warunkowo | Shortlista i przekazanie credentiali. W zadaniu 1 poszedłby od razu do web searcha. | Zaufanie: pola decydujące o go/no-go są błędne albo sprzeczne | Nagrana para request/response z żywego wywołania, `verified_by: live_call`, zwięzłe podsumowanie decyzyjne |
| **Kimi** (k3) | warunkowo | Raz, po sprawdzeniu własnych narzędzi, przed web searchem; potem przechodzi do dokumentacji | Zaufanie: pola są, ale wartości błędne lub mylące | `free_tier` bez triali, `match` pokrywające wolumen, osobny typ `docs_only` MCP, poziom pewności dla każdego pola |

**Wynik: 0 × „tak”, 7 × „warunkowo” (z czego 3 w praktyce bliżej „nie”), 0 × „nie”.**

### Co agenci naprawdę zrobią, a co jest grzeczną zgodą

- **Realne zachowanie** (spójne u wszystkich): jedno wywołanie `search_apis`, odrzucenie rankingu, wybór LocationIQ i Birda na podstawie własnej analizy pól, a potem dokumentacja dostawcy przed pierwszym requestem.
- **Deklaracje, które nie przetrwały dopytania:**
  - DeepSeek: „catalog first” zmienił się w „lean toward web search” i „Twilio z pamięci”.
  - Google: priorytet schematów parametrów zmienił się, po wskazaniu sprzeczności, w priorytet walidacji.
  - Mistral: zadeklarowane zaufanie przy „tiny JSON”, podczas gdy Qwen opisuje „multi-KB JSON”.
- **Halucynacje i pamięć przedstawiana jako dane z katalogu:**
  - Google opisał pola `get_api` dla OpenCage (`auth_scheme` w query, `rate_limits`), których nie widział. OpenAI i xAI wprost zaznaczyły, że widziały `get_api` tylko dla Freepika.
  - Mistral wymyślił `auth_hint`, ścieżkę `/search.php` i „statyczny endpoint `catalog/video-generation.json`”.
  - Kimi sam przyznał, że `key=` i `eu1` wziął z pamięci.

  **Wniosek:** gdy katalog nie podaje pola, agent wypełnia lukę zgadywaniem. Brakujące `auth_scheme` i `call` to ryzyko błędnych wywołań, a nie tylko niewygoda.
- **Merytoryczne błędy agentów** (nie traktować jako feedbacku o produkcie):
  - Mistral odrzucił OpenCage, bo 2 500/dzień to rzekomo „za mało na 200”; po dopytaniu się poprawił.
  - Mistral wybrał Twilio mimo MCP `docs_only`.
  - DeepSeek uznał wyniki SMS za „correct and all relevant”.

## 3. Błędy i słabości w wynikach wyszukiwania

### Zadanie 1: wideo z tekstu (5 s, zerowy budżet)

- **Freepik/Magnific: fałszywe `match: exact`.** Ma `operations` zawierające text-to-video, ale `call.example` to image-to-video (Kling `/kling-v2-1-pro`, wymaga obrazu wejściowego). Zauważyło to **6/7 agentów** (wszyscy poza Mistralem). Dodatkowo:
  - kategoria to *images*, a nie *video-generation*;
  - `no_card: false` przy zapytaniu z `no_card`;
  - „~5 EUR credits” to jednorazowy trial oznaczony jako `has_free_tier: true` (Google, DeepSeek, Kimi, Qwen);
  - brak `unit_price`, więc nie da się ustalić, czy jeden 5-sekundowy klip się zmieści (Mistral, xAI, Qwen, Kimi);
  - notatka o trwającej migracji (DeepSeek).
- **Hugging Face Inference Providers: nietrafione.** 0,10 USD/mies. nie pokryje generowania wideo, a narzędzia MCP służą do przeszukiwania huba, nie do generacji (`covers_full_api: false`). Mimo to wynik ma `match: exact`. Zauważyło to 7/7.
- **Zapytanie z przykładu jest za luźne.** `generate video from text prompt` z samym `free_tier` (xAI) nie wymusza kategorii `video-generation`. Z drugiej strony Kimi uważa, że filtr `free_tier` jest tu *zbyt ostry*, bo jednorazowy kredyt wystarcza na jeden klip.
- **Luka pokrycia.** Katalog strukturalnie nie obejmuje darmowych opcji (Spaces na HF, UI konsumenckie). 4 agentów (Google, DeepSeek, Mistral, Kimi) poszłoby po nie do web searcha.

### Zadanie 2: geokodowanie 200 adresów w Polsce

- **Ranking nie odpowiada zadaniu.** Według Kimi Esri jest na 1. miejscu (wymaga karty), Google na 2., Nominatim na 5. Według xAI LocationIQ, jedyny realny wybór, jest dopiero 3. Mistral twierdzi, że Nominatim był pierwszy. **Relacje są niespójne; kolejność trzeba zweryfikować w logach.** LocationIQ wybrało 7/7 agentów (Google alternatywnie OpenCage).
- **Google Maps MCP: `match: exact` bez narzędzia do geokodowania.** Narzędzia to `search_places`, `lookup_weather`, `compute_routes`, `resolve_names`, `resolve_maps_urls`. Dodatkowo `domain_verified: false`, a według DeepSeek brak pola `requires_card`. Wskazali to OpenAI, Google, xAI, Qwen i Kimi (5/7).
- **Nominatim.** Regulamin publicznego serwera zniechęca do bulku, a wynik podaje go jako opcję bez klucza dla 200 adresów. MCP pochodzi od społeczności i działa na niezweryfikowanym hoście. Wskazało to 7/7 agentów. Ranking powinien karać ten wynik przy wolumenie bulk.
- **Esri.**
  - Wymaga karty, a mimo to jest wysoko w rankingu (Google, Qwen, Kimi).
  - „URL MCP” to ścieżka do dokumentacji z `derived: true` (OpenAI, xAI).
- **OpenCage.** Opis „testing use” jest dwuznaczny: jedni agenci odczytali go jako zakaz produkcji, a Mistral przez niego źle ocenił przydatność usługi. Pole `notes` nie rozstrzyga, czy to ograniczenie licencyjne, czy tylko rekomendacja.
- **LocationIQ.**
  - Sprzeczne limity „2 requests/s, 60 requests/min”; wiążący jest limit ok. 1 req/s (Qwen, OpenAI).
  - Podany jest tylko shard `us1`, bez informacji o `eu1` (Qwen, Kimi).
  - Brak ścieżki endpointu, parametrów i schematu odpowiedzi.
- **Brakujące usługi:**
  - Mapbox (Google, DeepSeek, Kimi);
  - HERE (DeepSeek, xAI, Kimi);
  - Geoapify (xAI, Kimi);
  - **GUGiK/PRG**, oficjalny polski geokoder (xAI, Kimi);
  - Photon i BigDataCloud (Mistral).

  Brak usług krajowych i lokalnych szkodzi jakości wyników dla adresów w Polsce.
- **Brak pól prawnych i danych.** Nie ma informacji o RODO/DPA ani o tym, czy adresy klientów można wysłać do strony trzeciej (Qwen, OpenAI).

### Zadanie 3: wysłanie przypomnienia SMS

- **AWS End User Messaging jest za wysoko (1. miejsce)** według 6/7 agentów (wszyscy poza DeepSeekiem). Powody:
  - tylko płatny plan, uwierzytelnianie `cloud_iam`/SigV4, rejestracja 10DLC;
  - ceny tylko dla USA;
  - narzędzia MCP to dokumentacja i ogólne `aws___run_script`, a nie dedykowane wysyłanie SMS;
  - flaga `covers_full_api: true` jest „niewiarygodna” (xAI).
- **Twilio: MCP `docs_only`** (`mcp.twilio.com/docs`) prezentowany przy zadaniu „wyślij SMS”. Ma przy tym `mcp.type: "official"`, co wygląda na równorzędne z Birdem (Kimi). Trial pozwala wysyłać tylko na 5 zweryfikowanych numerów, więc SMS do dowolnego klienta nie przejdzie. Zauważyło to 7/7 agentów (Mistral mimo to wybrał Twilio).
- **Bird**, jedyny wynik z hostowanym MCP i narzędziem `sms_send`, jest wybierany najczęściej (OpenAI, xAI, Kimi, warunkowo Google i DeepSeek). Ma jednak słabości:
  - `config.derived: true`;
  - brak bloku uwierzytelniania (w przeciwieństwie do wpisu Google Maps, który ma `headers`);
  - brak schematu wejścia `sms_send`;
  - brak ceny dla kraju docelowego.
- **Sinch i Plivo** mają tylko repozytoria do instalacji, bez hostowanego endpointu (`remote_url: null`).
- **Uptime.** Status „unavailable” dla 4 z 5 wpisów SMS; Kimi wskazuje, że sygnał jest niespójny tam, gdzie doręczalność jest kluczowa.
- **Brak informacji operacyjnych:** rejestracja nadawcy (10DLC/origination), opt-out i zgody, ograniczenia triali, webhooki statusu doręczenia (OpenAI, Qwen, Kimi, Google, DeepSeek).
- **Brakujące usługi:** Vonage (xAI, DeepSeek, Mistral, Kimi = 4), Telnyx (xAI, Kimi), Textbelt (Mistral, Kimi).

### Problemy przekrojowe

- Uptime probe policzył odpowiedź `detail: 404` z base URL jako „up” (Qwen).
- `link_check.docs: ok` dowodzi tylko, że strona się ładuje (Qwen, Mistral).
- Pozytyw: wpis Freepika z nagłówkiem `x-magnific-api-key` i notatką o rebrandingu był **aktualniejszy niż pamięć modelu** (Kimi). Pola z `source_url` i `checked_at` budują zaufanie, bo wygrywają ze starą wiedzą modelu.

## 4. Brakujące pola potrzebne, by od wyniku przejść do działającego wywołania

| Brakujące pole / informacja | Liczba agentów | Kto |
|---|---|---|
| Konkretny endpoint (metoda, ścieżka, parametry) i przykład wywołania dla **tej** operacji | **7** | wszyscy |
| MCP: flaga „wykonawczy vs docs-only”, schematy narzędzi, wykluczenie `docs_only` z zapytań operacyjnych | **7** | wszyscy |
| Dokładne miejsce i format klucza (nagłówek/query, nazwa, składnia) | 6 | OpenAI, xAI, DeepSeek, Mistral, Qwen, Kimi |
| Przykład zgodny z operacją z zapytania (text-to-video, nie image-to-video) | 6 | OpenAI, Google, xAI, DeepSeek, Qwen, Kimi |
| Rozróżnienie stałego darmowego planu i jednorazowego trialu | 5 | Google, xAI, DeepSeek, Qwen, Kimi |
| `unit_price` dla danej operacji (i kraju docelowego) | 5 | OpenAI, xAI, Mistral, Qwen, Kimi |
| Dopasowanie do wolumenu: zgoda na bulk, czy darmowy limit pokrywa N operacji (`covers_job`) | 5 | OpenAI, xAI, Mistral, Qwen, Kimi |
| Wymogi operacyjne SMS: rejestracja nadawcy, opt-in, webhooki doręczeń | 5 | OpenAI, Google, DeepSeek, Qwen, Kimi |
| Przykład przetestowany na żywym API (`tested_at`, nagrana odpowiedź) | 4 | OpenAI, DeepSeek, Qwen, Kimi |
| Pochodzenie weryfikacji: `live_call` vs `docs_read`, pewność dla każdego pola | 4 | OpenAI, Mistral, Qwen, Kimi |
| Konfiguracja MCP z uwierzytelnianiem, bez adresów `derived` (albo z potwierdzonym handshake) | 4 | OpenAI, xAI, Mistral, Kimi |
| Cena dla kraju docelowego (nie tylko USA) | 4 | OpenAI, xAI, Qwen, Kimi |
| Schemat odpowiedzi (np. lat/lon jako stringi) | 3 | OpenAI, Qwen, Kimi (DeepSeek: „truncated body”) |
| Region/endpoint EU (`eu1`, US/EU dla Birda) | 3 | xAI, Qwen, Kimi |
| Uzgodniony, wiążący limit rate | 2 | OpenAI, Qwen |
| Warunki prawne: RODO/DPA, atrybucja, użycie komercyjne | 2 | OpenAI, Qwen |
| Zwięzły blok decyzyjny („czy mogę teraz wykonać 1 / N operacji?”) | 2 | OpenAI, Qwen |
| Status „podłączony i uwierzytelniony w tej sesji” | 1 | OpenAI |
| Data ostatniego pusha repozytorium MCP | 1 | DeepSeek |

**Obszar, którego nie zamknie żaden katalog.** Wysyłka SMS, płatności i przekroczenie darmowego limitu zawsze wymagają zgody użytkownika i weryfikacji u dostawcy (OpenAI, DeepSeek, Qwen). Qwen nazywa to „correct behavior, not a catalog failure”. Celem powinno być pominięcie dokumentacji przy **pierwszym, tanim, odczytowym** wywołaniu, a nie wszędzie.

## 5. Uwagi do opisów narzędzi i skilla

### Frazy do zmiany

| Obecne sformułowanie | Problem | Proponowana zmiana | Kto |
|---|---|---|---|
| „The task needs an external service: ‘make a 5-second video’…” | Podłączone narzędzie też jest „external service”. Fraza jest cykliczna i wyzwala wyszukiwanie, zanim agent sprawdzi, co ma podłączone. | „…needs a capability unavailable through the model, built-in tools **or currently connected tools**.” | OpenAI, Google, Mistral, Qwen |
| „when your own attempt at a call failed (403, rate limit, unsupported format)” | Skłania do zmiany dostawcy po każdym błędzie, także po własnym źle zbudowanym requeście lub brakującym uprawnieniu. | „when a call failed for a service-side reason you can’t fix (auth rejected after checking permissions, quota, billing required, unsupported format or region) — not a malformed request of your own.” xAI proponuje wręcz usunięcie. | OpenAI, xAI, Mistral, Qwen (DeepSeek i Kimi chwalą obecną wersję) |
| „`match`: exact means one of its `operations` is the requested operation” | Etykieta obiecuje więcej, niż dowodzi (przypadek Freepika). | „`exact` is a search label; verify the documented endpoint or MCP tool accepts the user’s actual inputs”. Albo zmienić nazwę na `operation_listed`. | OpenAI, Kimi |
| „`no_auth: true`: callable now” | Pomija regulamin i ograniczenia bulku (Nominatim). | „No credential required; check permitted use and volume before calling.” | OpenAI |
| „A remote endpoint … is connected once” | Myli „hostowany” z „podłączony i uwierzytelniony w tej sesji”. | „A hosted endpoint needs no installation, but may still require connection, authentication and a suitable operation tool.” | OpenAI |
| „Start from `call.example` when present” | Przykład może dotyczyć innej operacji. | „…only if its operation and required inputs match the task.” | OpenAI |
| „Ranking is not proof of fit” | Za słabe. | „Results are ranked by keyword match, not by fit for volume, budget or region. Read `free_plan.kind` and `notes`.” | Kimi |
| „Skip it when a built-in or connected tool already does the job” | Chwalone (OpenAI, DeepSeek, Kimi), ale nie przewiduje wyczerpanego lub niewystarczającego narzędzia. | „…does the job within this task’s volume, cost and data constraints; if it is exhausted or lacks a required option, search anyway.” | Qwen |
| „after checking your built-in and connected tools and your own model” | Nieostre. | „after one quick check: if you cannot name the tool that performs the operation, search.” | Qwen, Mistral |
| „web search or scraping” we frontmatterze | Ładuje skill przy zwykłym wyszukiwaniu w sieci. | Usunąć. | xAI |
| „confirm limits and pricing in `docs` before relying on them” | Agenci cytują to jako powód, by od razu pominąć katalog. | Zawęzić do konkretnych pól: „Verified fields (`verified_by: live_call`) can be used directly; confirm pricing only beyond the free quota and terms for batch or commercial use.” | wniosek z DeepSeek, Mistral, Qwen, xAI |

### Brakujące wyzwalacze

- **Użytkownik sam wskazuje usługę** („geokoduj przez Nominatim”, „wyślij przez Twilio”). Skill wtedy nie odpala, a właśnie tu `get_api` wyłapałby zakaz bulku, MCP `docs_only` czy ograniczenia trialu. Propozycja xAI: *„If the user names a service, or you are about to use one for a batch or a message, payment or other third-party action, call `get_api` first. A vendor you already know is not already checked.”*
- **Dane na żywo przy braku dostępu do sieci** (Qwen).
- **Budżet zerowy:** wprost ostrzec, że darmowe plany to często triale (Kimi).

### Czego NIE wdrażać

DeepSeek proponuje dopisać: „jeśli znasz API z danych treningowych, użyj go bezpośrednio”. Zredukowałoby to użycie katalogu do minimum, a Kimi pokazał, że pamięć modelu była tu **nieaktualna** (nagłówek Freepika po rebrandingu). Lepiej iść w przeciwną stronę, jak proponuje xAI: „znany dostawca to nie sprawdzony dostawca”. Propozycję Google („nie wywołuj, jeśli masz tylko napisać kod integracji”) warto rozważyć ostrożnie. Przy pisaniu kodu też potrzebne są poprawne auth i endpoint.

## 6. Rekomendacje (top 10, według wpływu)

1. **Semantyczna walidacja `match: exact`.** `exact` przyznawać tylko wtedy, gdy `call.operation` albo narzędzie MCP faktycznie realizuje żądaną operację. Wyniki `docs_only` i MCP bez narzędzia dla danej operacji degradować lub oznaczać jako `unusable`.
   - *Uzasadnienie:* bezpośrednio usuwa główną blokadę zaufania. Obala 4 z najczęściej cytowanych błędów (Freepik, HF, Google Maps, Twilio). xAI: „I would then trust an empty list and skip web search.”
   - *Nakład:* średni.
2. **Rozdzielenie darmowego planu i trialu.** Wprowadzić `free_plan.kind: recurring | trial | credit`. Filtr `free_tier` domyślnie wyklucza triale; dodać opcję `include_trials`. Ujednolicić `requires_card`, łącznie z brakującym polem u Google.
   - *Uzasadnienie:* 5 agentów o to prosi, a Google wskazał to jako jedyną zmianę, która zmieniłaby jego zachowanie.
   - *Nakład:* mały.
3. **Ranking pod zadanie, nie pod słowa kluczowe.** Uwzględniać wolumen (bulk vs single), zgodę na bulk i użycie produkcyjne, `requires_card` przy filtrze `no_card`, typ wejścia (tekst vs obraz) oraz region.
   - *Uzasadnienie:* ranking we wszystkich trzech zadaniach był odrzucany (Esri/Google nad LocationIQ, AWS jako pierwszy). Agenci wprost mówią „I would not follow the ranking”.
   - *Nakład:* średni.
4. **Pełny obiekt `call` dla każdego wyniku `exact`:** metoda, URL, miejsce i nazwa klucza, wymagane parametry, pola odpowiedzi.
   - *Uzasadnienie:* 7/7 agentów tego szuka. Brak pola powoduje halucynacje (Google, Mistral, Kimi uzupełniali je z pamięci).
   - *Nakład:* duży, wymaga pracy przy każdym wpisie.
5. **Weryfikacja wywołaniem na żywo i jawne pochodzenie danych:** `verified_by: live_call | docs_read | derived`, `tested_at` oraz nagrana odpowiedź (status i fragment body). Przy okazji naprawić uptime probe, który liczy 404 jako „up”.
   - *Uzasadnienie:* to jedyny warunek, przy którym Qwen, DeepSeek i Kimi pominęliby dokumentację przy pierwszym tanim wywołaniu.
   - *Nakład:* duży (infrastruktura testów, konta testowe). Samą naprawę probe’a można zrobić małym nakładem od razu.
6. **Uczciwa sekcja MCP.** Nie publikować `mcp.config.url` z `derived: true` bez udanego handshake’u. Dodać `callable: true/false`, blok uwierzytelniania i schemat wejścia narzędzi. Dodać filtr `callable_mcp`.
   - *Uzasadnienie:* przypadki Esri (ścieżka dokumentacji jako URL MCP), Birda (brak auth) i Twilio (`official`, choć tylko docs). MCP to unikalna wartość katalogu względem web searcha (Qwen, DeepSeek), a obecnie jest najmniej wiarygodna.
   - *Nakład:* średni.
7. **Wycena konkretnego zadania.** `unit_price` dla operacji (i kraju docelowego w SMS) oraz wyliczane `covers_job` („200 geokodów mieści się w dziennym limicie”, „1 klip 5 s = X”).
   - *Uzasadnienie:* dla Mistrala to pole „decisive”; przy zerowym budżecie decyduje o całym zadaniu.
   - *Nakład:* średni do dużego (ceny zmienne, zależne od kraju).
8. **Przepisanie skilla i opisów narzędzi według sekcji 5.** W szczególności: warunek „currently connected tools”, zawężona klauzula 403, nowa definicja `exact`, wyzwalacz `get_api`, gdy użytkownik wskazuje usługę, zawężenie disclaimera „confirm in docs”, usunięcie „web search or scraping” z frontmattera.
   - *Uzasadnienie:* tanie; ogranicza wywołania w złym momencie i odbiera agentom argument do pominięcia katalogu.
   - *Nakład:* mały.
9. **Zwięzły blok decyzyjny w `search_apis`:** „czy mogę teraz wykonać 1 / N operacji”, wiążący limit rate (uzgodnione 2/s vs 60/min), wymóg karty, link do konkretnej sekcji dokumentacji.
   - *Uzasadnienie:* zmniejsza koszt tokenów i ryzyko błędnej interpretacji (Mistral i OpenCage).
   - *Nakład:* mały do średniego.
10. **Pokrycie i pola domenowe.** Uzupełnić brakujące usługi, które agenci wymieniali z pamięci:
    - geokodowanie: Mapbox, HERE, Geoapify, GUGiK/PRG;
    - SMS: Vonage, Telnyx.

    Dla SMS dodać pola rejestracji nadawcy, ograniczeń triali i obsługiwanych krajów. Dla danych osobowych dodać RODO/DPA.
    - *Uzasadnienie:* ważne, ale według agentów nie decyduje o użyciu. xAI: „Missing Vonage or Telnyx does not change that.”
    - *Nakład:* średni.

## 7. Cytaty warte zapamiętania

- **xAI:** *„I would not act on `match`, rank, MCP URL, or `covers_full_api` without opening docs. That is the same work as web search, plus a wrong shortlist.”*
- **xAI:** *„I would then trust an empty list and skip web search.”*
- **xAI:** *„A vendor you already know is not already checked.”*
- **OpenAI:** *„I wouldn’t use it as the authority for endpoints, prices, permissions or whether an MCP tool performs the operation.”*
- **OpenAI:** *„Those changes would keep the catalog a discovery aid rather than permission to call the first ‘exact’ hit.”*
- **Google:** *„Trust is the foundation. Parameter schemas save a follow-up query, but validation is what makes the catalog safe to touch in the first place.”*
- **Qwen:** *„Not a curl template — a transcript of a call that returned 200.”*
- **Qwen:** *„the uptime probe counted `detail: 404` on the base URL as ‘up’ — that’s a misleading signal.”*
- **Kimi:** *„The catalog gets me to the right door; the docs write the call.”*
- **Kimi:** *„That was memory dressed as confidence — exactly the failure mode I criticized the catalog for.”*
- **Kimi:** *„the catalog earns trust field by field, not as a whole — sourced, dated fields beat my memory; derived or example fields don’t.”*
- **Mistral:** *„The catalog is a suggestion engine, not a source of truth.”*
- **DeepSeek:** *„For anything else, the catalog is a filter, not a substitute for the source of truth.”*
