# Raport: test produktu z agentami AI (2026-11-03)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5), Alibaba (Qwen) (qwen/qwen3.8-max-0902), Moonshot AI (moonshotai/kimi-k3)

Materiał pokazany agentom: `material.txt` w tym katalogu.

# Raport: testy agentów AI z katalogiem API (MCP + skill)

## 1. Podsumowanie

Wszystkich siedmiu agentów deklaruje, że sięgnie po `search_apis`, gdy brakuje im jakiejś zdolności (wideo, geokodowanie, SMS). W praktyce **żaden nie wykonałby działania na podstawie samego wyniku**. Wszyscy traktują katalog jako listę kandydatów, a decydujące szczegóły sprawdzają w dokumentacji dostawcy lub przez web search. Jedyną realną blokadą, wskazaną przez wszystkich siedmiu, jest **zaufanie do danych**. Agenci znaleźli wewnętrzne sprzeczności w polach, na podstawie których mają filtrować i decydować: `mcp_fit` przeczy liście `tools`, jednorazowe kredyty są oznaczone jako `free_tier`, a ranking nie respektuje przekazanych filtrów. Druga blokada to brak kompletnego, wykonywalnego wywołania (`call`) dla wyników `exact`. Nawet przy dobrym wyborze (GUGiK) agent musi otworzyć dokumentację, zanim wyśle pierwsze z 200 zapytań. Instalacja, opóźnienia i koszt tokenów nie blokują nikogo. Jest jednak jedno ostrzeżenie strukturalne: według OpenAI skill Claude'a może się w ogóle nie załadować na innych platformach, a same opisy narzędzi nie mówią, *kiedy* ich używać.

## 2. Tabela agentów

| Agent | Użyje? | W którym momencie | Główna blokada | Czego brakuje |
|---|---|---|---|---|
| **OpenAI** (gpt-6-sol-pro) | warunkowo | Dopiero po sprawdzeniu wbudowanych i podłączonych narzędzi, gdy żadne nie wykona operacji. Ranking nie jest dla niego „autoryzacją” do działania. | Zaufanie. Dodatkowo twarda przeszkoda: MCP musi być podłączone, a skill Claude'a może nie działać na jego platformie. | Przepisy wywołań zależne od operacji i przetestowane (request, auth, odpowiedź, błędy). Limity i warunki dla konkretnego zadania ze źródłem. Krótkie podsumowanie akcji. |
| **Google** (gemini-3.8-flash) | warunkowo (deklaruje „tak”) | „Od razu” po stwierdzeniu braku zdolności. W zadaniu 1 i tak przechodzi na web search. | Zaufanie do flag boolean (`free_tier`, `no_card`, `mcp_fit`) | Spójne flagi. Gwarantowany `call` w `get_api` dla każdego `exact`. `endpoint_summary` w wynikach wyszukiwania. Ustandaryzowane konfiguracje MCP. |
| **xAI** (grok-4.7) | warunkowo | Jedno wywołanie dla nieznanej operacji, potem „odrzucam ranking i weryfikuję”. Przy budżecie, bulk lub pytaniu o parametry idzie od razu do web search. | Zaufanie: mylą się etykiety, na których ma działać | Prawdziwe flagi. Pełne żądanie przy `exact`. Ranking zgodny z filtrami. `unit_price` i `free_plan.kind` na karcie wyniku. |
| **DeepSeek** (v4-pro) | tak, jako pierwszy krok | Pierwszy krok. Przy cienkich wynikach „porzucam szybko” i przechodzi do web search. | Zaufanie plus luki w pokryciu | Testy endpointów na żywo. Flaga `coverage`. `call` dostępny bez dodatkowej rundy. |
| **Mistral** (medium-3-5) | warunkowo (deklaratywnie „tak”) | Shortlista, a potem zawsze dokumentacja | Zaufanie (nieaktualne dane) | Probe konkretnego endpointu sprzed ≤7 dni. `free_tier_verified`. Pole `breaking_changes`. |
| **Qwen** (3.8-max) | tak, jako shortlista | Natychmiast, gdy brak podłączonego narzędzia | Zaufanie: pewnie brzmiące pola skłaniają do działania bez sprawdzenia | Pola, które same się uwierzytelniają (dosłowny cytat ceny, `contradictions: []`, `verified_by: test_call`). Poprawki skilla. Odchudzone odpowiedzi. |
| **Moonshot** (kimi-k3) | tak, jako trop | Wcześnie, po krótkim przejrzeniu własnej pamięci | Zaufanie („it's not close”) | Kompletny `call` z testem na żywo (≤30 dni). Mechaniczna klasyfikacja `free_plan.kind` i `mcp_fit`. Pokrycie podstawowych usług lub `coverage_note`. |

### Realne zachowanie a uprzejme deklaracje

- **Rzeczywisty wzorzec u wszystkich:** `search_apis` → (czasem `get_api`) → dokumentacja lub web search → dopiero wtedy działanie. Katalog oszczędza krok tworzenia shortlisty, ale nie krok weryfikacji. DeepSeek nazwał to wprost: „discovery index, not a decision tool”.
- **Mistral** był najbardziej uprzejmy i najmniej wiarygodny. Najpierw zaakceptował Freepika jako „lasting free tier”, chwalił `mcp_fit` i twierdził, że GUGiK ma „no rate limits”. Napisał też request do Twilio z pamięci. Wycofał się dopiero pod presją pytań. Jego „tak” należy traktować jako deklarację, nie zachowanie.
- **DeepSeek** sam sobie zaprzeczył: w Q1 szuka w katalogu najpierw, w Q5 dla szybko zmieniających się kategorii pomija go. Twierdził też, że przykład Freepika ma `duration: 5`, choć ma 6. Uznał Textbelt za „perfect” do przypomnienia dla klienta.
- **Google** deklaruje użycie katalogu „rather than web search”, ale w jedynym zadaniu, które przeszedł krok po kroku, wrócił do web search. Swój postulat „cały `call` w `search_apis`” wycofał po dopytaniu i zastąpił go `endpoint_summary`.
- **OpenAI, xAI, Moonshot i Qwen** byli najbardziej spójni i krytyczni. Ich opinie warto traktować jako najlepsze przybliżenie realnego zachowania.

## 3. Błędy i słabości w wynikach wyszukiwania

### Zadanie 1: 5-sekundowe wideo, zero budżetu (`query: "generate video from text prompt"`, `free_tier: true`)

| Problem | Ilu agentów zauważyło |
|---|---|
| **Hugging Face Inference Providers** ($0.10/mies., dopasowanie `listed`, narzędzia MCP służą tylko do przeszukiwania huba) jest za wysoko lub w ogóle nie powinien przejść filtra | 7/7 |
| **Freepik/Magnific:** `mcp_fit` = „no MCP tool named for this operation”, a lista `tools` zawiera `video_generate` | 6/7 (nie zauważył Mistral) |
| **Freepik:** ~5 EUR jednorazowych kredytów oznaczone `free_tier: true` / `has_trial: false`, czyli trial według definicji samego skilla | 5/7 (DeepSeek i Mistral przyjęli to bezkrytycznie) |
| **Freepik:** `no_card: false` przy zapytaniu „zero budżetu”. Pole nie jest widoczne w wyniku wyszukiwania, wychodzi dopiero w `get_api` | 5/7 |
| Przykład `call` generuje **6 s**, a nie 5 s. Brak informacji o dozwolonych wartościach `duration` | 3/7 (OpenAI, xAI, Qwen) |
| Brak `unit_price`, więc nie wiadomo, czy 5 EUR wystarczy na jeden klip | 3/7 (xAI, Qwen, Moonshot) |
| Freepik jest w kategorii `image-generation`, więc wyszukiwanie z `category: video-generation` go nie znajdzie | 2/7 (xAI, Moonshot) |
| Za mało wyników. Brakuje m.in. Replicate, fal.ai, Runway, Luma, Kling, Pika, Minimax, Pollinations, HF Spaces oraz ścieżki dla modeli lokalnych (LTX/Wan/CogVideo) | 5/7 |
| Dla jednorazowego zadania przy zerowym budżecie powinno się szukać z `include_trials` | 2/7 (xAI, DeepSeek) |

### Zadanie 2: geokodowanie 200 polskich adresów

| Problem | Ilu agentów |
|---|---|
| **GUGiK na 1. miejscu słusznie.** Wszyscy by go wybrali, ale nikt nie wysłałby 200 zapytań bez otwarcia dokumentacji | 7/7 |
| **Photon** (publiczna instancja, „extensive usage throttled/banned”) za wysoko dla zadania wsadowego | 5/7 |
| **Google Maps** za wysoko: wymaga konta billingowego z kartą, a jego MCP nie ma narzędzia do geokodowania, mimo `match: exact` | 6/7 |
| **OpenCage:** darmowy plan „testing-only” bez wyraźnego oznaczenia, powinien być poniżej LocationIQ | 4/7 |
| **Brak Nominatim**, choć skill sam podaje go jako przykład („geocode with Nominatim”) | 5/7 |
| Kara za bulk nie zadziałała: zapytanie nie przekazało `volume: "bulk"`, a katalog nie wywnioskował wolumenu z „200” | 3/7 (OpenAI, xAI, Moonshot) |
| GUGiK: „no published quota” nie oznacza limitu ani zgody na pętlę 200 wywołań. Mistral odczytał to jako „brak limitów” | 6/7 |
| GUGiK: nie wiadomo, w jakim układzie współrzędnych przychodzi wynik (PL-1992 czy WGS84). Ryzyko cichego, poważnego błędu | 2/7 (xAI, Moonshot) |

### Zadanie 3: SMS z przypomnieniem do klienta

| Problem | Ilu agentów |
|---|---|
| **Textbelt na 1. miejscu** (wspólny klucz, 1 SMS/dzień) to błędny ranking dla komunikacji z klientem | 6/7 (DeepSeek uznał go za dobry wybór) |
| **Sinch:** `mcp_fit` wskazuje `start-sms-verification` (2FA), a lista zawiera `send-text-message` | 6/7 |
| **Telnyx:** MCP to generyczny `invoke_api_endpoint`, a nie narzędzie SMS. Do tego `auth: none` (xAI nie podłączyłby go) | 4–5/7 |
| Triale Twilio, Sinch, Telnyx i Vonage działają tylko dla zweryfikowanych numerów lub szablonów, więc nie ma darmowej ścieżki do dowolnego klienta. Katalog tego nie mówi wprost na poziomie wyniku | 6/7 |
| Wynik Twilio pokazuje MCP w wersji alpha (stdio), a nie kanoniczny REST (`/Messages.json`, Basic Auth, `To/From/Body`) | 3/7 (Google, Mistral, Qwen) |
| Ceny dla Polski (`price_pl`) dołączone, choć kraj docelowy nie został podany | 1/7 (xAI). OpenAI też wymaga kraju przed decyzją |
| Vonage (ma narzędzie MCP `SMS`) za nisko | 1/7 (DeepSeek) |
| Brakujący dostawcy: Plivo, Bird/MessageBird, AWS SNS, Infobip, Bandwidth, **SMSAPI.pl** (ważne przy kontekście polskim) | 5/7 |
| Brak wskazówek o zgodzie, opt-out i RODO przy SMS do klienta | 3/7 (OpenAI, Qwen, Moonshot) |

## 4. Brakujące pola i informacje (od wyniku do działającego wywołania)

| Brakujące pole / informacja | Ilu agentów prosiło | Kto |
|---|---|---|
| **Kompletny `call` dla każdego wyniku `exact`**, nie tylko dla „popularnych” usług: metoda, pełny URL lub ścieżka, nazwy parametrów, przykład z realnymi danymi | **7** | wszyscy |
| **Schemat odpowiedzi / przykładowa odpowiedź** (ścieżka do lat/lon, `data.generated[0]`, rozpoznanie braku trafienia lub wielu trafień) | **6** | OpenAI, Google, xAI, DeepSeek, Qwen, Moonshot |
| **Liczbowe limity i zasady dla wsadów** (czy 200 wywołań jest dozwolone, z jaką szybkością) | **6** | OpenAI, Google, xAI, DeepSeek, Qwen, Moonshot |
| **Spójność `mcp_fit` z `tools`** (wyliczana mechanicznie) | **6** | Google, xAI, DeepSeek, Qwen, Moonshot, OpenAI |
| **Dowód, że wywołanie działa** (test na żywo, `last_live_call: {at, status}`, a nie samo `link_check`) | **5** | OpenAI, DeepSeek (≤7 dni), Mistral (≤7 dni, konkretny endpoint), Qwen (`verified_by: test_call`), Moonshot (≤30 dni) |
| **Jawny sposób uwierzytelnienia** (nagłówek, Basic, nazwa zmiennej środowiskowej), a nie tylko `auth: "api_key"` | **5** | OpenAI, Google, Mistral, Qwen, Moonshot |
| **Poprawna klasyfikacja `free_plan.kind`** (trwała pula a jednorazowy kredyt) i widoczność `no_card` na karcie wyniku | **5** | Google, xAI, DeepSeek, Qwen, Moonshot |
| **Zachowanie przy błędach / 429 / retry**, w tym czy błędy zużywają limit | **4** | OpenAI, xAI, DeepSeek, Qwen |
| **`unit_price` / koszt dla wolumenu zadania** | **4** | OpenAI, xAI, Qwen, Moonshot |
| **Dozwolone wartości parametrów** (np. `duration`) | **3** | OpenAI, xAI, Qwen |
| **Kodowanie znaków / polskie znaki diakrytyczne** | **3** | DeepSeek, xAI, Qwen |
| **Krótsze odpowiedzi / parametr `fields` lub `verbose`** (bez `ratings` i pełnych konfiguracji MCP w wynikach) | **3** | Qwen, Moonshot, OpenAI |
| **Źródło i dosłowny cytat dla ceny/limitu, jawne „unknown”** | **2** | Qwen, OpenAI |
| **Układ współrzędnych (CRS) w odpowiedziach geo** | **2** | xAI, Moonshot |
| **Flaga pokrycia (`coverage` / `coverage_note`)** | **2** | DeepSeek, Moonshot |
| Format numeru E.164, ograniczenia krajowe dla SMS, kupno numeru nadawcy | 2–3 | Google, DeepSeek, Moonshot |
| Warunki użycia i przechowywania wyników | 1 | OpenAI |
| Rozróżnienie MCP remote (bez instalacji) i stdio, gotowe bloki konfiguracji | 1–2 | Google, Mistral |
| `breaking_changes` z datą | 1 | Mistral |
| Angielskie streszczenie dokumentacji nieanglojęzycznej (GUGiK) | 1 | DeepSeek |

**Uwaga o sprzecznym postulacie:** DeepSeek i początkowo Google chcieli pełnego `call` bezpośrednio w `search_apis`. Qwen, Moonshot i OpenAI chcą chudszych wyników. Kompromis, który Google zaakceptował po dopytaniu: krótki `endpoint_summary` oraz `free_plan.kind`, `no_card` i `unit_price` na karcie wyniku, a pełny, gwarantowany `call` w `get_api`.

## 5. Uwagi do opisów narzędzi i skilla

### Problem nadrzędny
- **Opisy narzędzi MCP mówią, *co* zwracają, ale nie *kiedy* ich użyć** (OpenAI, xAI, Qwen). Cała logika wyzwalania jest w skillu Claude'a, który według OpenAI może nie być ładowany na innych platformach. Agenci spoza ekosystemu Claude'a dostaną więc narzędzia bez instrukcji.

### Konkretne frazy do zmiany

| Obecne brzmienie | Problem | Proponowana zmiana | Zgłosili |
|---|---|---|---|
| „if you cannot name the tool that does it, search” | Myli *znajomość dostawcy* z *posiadaniem wywoływalnego narzędzia*. Jeśli agent pamięta Runway lub Nominatim, traktuje to jako zgodę na pominięcie katalogu, a to właśnie wtedy liczą się trial i zakazy bulk. Nie uwzględnia też ograniczeń budżetu, kraju i wolumenu. | „If you cannot name **a connected tool you can actually call right now** that does it at this volume, search. Knowing a vendor exists is not having a callable tool. Also search when the task's constraint (zero budget, a country, a volume) depends on current pricing, quotas or terms you can't verify from memory.” | xAI, Qwen, Moonshot, OpenAI, Google (DeepSeek i Mistral chwalili tę frazę, czyli jest zrozumiała, ale prowadzi do pomijania katalogu) |
| „The user names a service … call `get_api` first. A vendor you already know is not a checked vendor.” | Kłóci się z regułą „skip when a connected tool already does the job”. Wymusza zbędne wywołanie, gdy Twilio lub Slack są już podłączone. | „If the user names a service **that is not already connected**, call `get_api` before using it. If it is connected and working, do not search for alternatives unless the user asked for options, you are about to rely on limits/pricing/batch behaviour you haven't verified, or the call failed for a service-side reason.” | OpenAI, Google, xAI, DeepSeek, Qwen, Moonshot (Mistral chciał wzmocnić tę regułę, ale to opinia odosobniona) |
| `get_api` wymaga `id` | Skill tego nie mówi | Dodać: „If you only know the name, find the id with `search_apis` first.” | OpenAI |
| `search_apis`: „exact = … example call or an MCP tool performs it” | Obiecuje więcej, niż dane potwierdzają | „`exact` means catalog evidence names the operation; verify inputs, endpoint, limits and MCP-tool availability before use.” Najlepiej jednak naprawić dane, a nie tylko tekst. | OpenAI, DeepSeek |
| `get_api`: „Full entry” | Sugeruje kompletność | „Catalogued details; fields may be absent or insufficient to construct a request.” Albo zagwarantować kompletność. | OpenAI |
| `search_apis`: „by operation or keywords” | „keywords” zachęca do szukania po nazwie dostawcy | „Search by the operation you need (e.g. 'geocode street addresses'). If you know the service, use `get_api`.” | DeepSeek |
| Opis `search_apis` nie mówi, że `call` jest w `get_api` | Agent nie wie, gdzie szukać przykładu | „Search returns a summary. For the example request (`call`), full tool list, rate limits and pricing, call `get_api`.” | DeepSeek |
| „Skip it when a built-in or connected tool already does the job within this task's volume, cost and data limits” | „within limits” łatwo przeoczyć. Brak zastrzeżenia o aktualności danych. Google podał przykład: model z wizją „umie” OCR, więc pominie katalog przy 50 PDF-ach. | Dodać: „Check the connected tool's actual quota and format support against the full task volume; if unsure, search. Doing it inline is not a reason to skip when scale or context limits make it impractical.” | DeepSeek, Moonshot, Google |
| „a call failed for a service-side reason you can't fix” | 401 to często błąd klucza użytkownika. Przy 429 lub wyczerpanym limicie wystarczy czasem poczekać. | „On 401/403 with a correct key format, ask the user to check the credential. Search on 402, 429 (when waiting isn't acceptable), unsupported region or missing endpoint, when switching providers is cheaper than waiting or upgrading.” | DeepSeek, Moonshot |
| `get_reviews` / `list_categories` | OK jako opcjonalne | Dopisać: „Reviews cannot establish task fit; categories need not be listed before a clear operation search.” | OpenAI |

**Co działa (warto zostawić):** „Do not settle for an adjacent service”, zastrzeżenie, że `match: exact` to „still a search label”, rozróżnienie `free_tier`/`trial` w opisie (problem jest w danych, nie w tekście) oraz reguła „trust fields for a cheap read-only call; confirm pricing before money/bulk/third-party actions”. Qwen i Moonshot uznali ją za właściwe zabezpieczenie.

## 6. Rekomendacje (top 10 według wpływu)

1. **Walidacja spójności danych przed publikacją: wpis ze sprzecznością nie trafia do wyników.** `mcp_fit` wyliczać mechanicznie z `tools`, żeby Freepik `video_generate` i Sinch `send-text-message` były poprawnie oznaczone. `free_plan.kind` klasyfikować automatycznie („credits”, „one-time”, „expires” oznacza `trial`). Dodać widoczne pole `contradictions: []`.
   *Uzasadnienie:* wszyscy 7 agentów wskazało zaufanie jako blokadę. Sprzeczności widoczne w jednym payloadzie są najtańsze do usunięcia, a mają największy efekt. xAI: „If those two disagree, I re-check every hit.” *Nakład: mały–średni.*

2. **Gwarantowany, kompletny `call` dla każdego wyniku `exact`, nie tylko dla popularnych usług:** pełny URL, metoda, miejsce uwierzytelnienia (nazwa nagłówka lub zmiennej), wymagane parametry z dozwolonymi wartościami, przykładowa odpowiedź z ścieżką do wyniku, kształt błędu, CRS i jednostki. Bez kompletnego `call` wynik nie powinien mieć etykiety `exact`.
   *Uzasadnienie:* 7/7. Bez tego nawet najlepszy wybór (GUGiK) kończy się otwarciem dokumentacji. *Nakład: duży* (praca redakcyjna na wpis), ale można zacząć od top kategorii.

3. **Ranking zgodny z filtrami i zadaniem.** `free_tier: true` wyklucza triale. `no_card: true` wyklucza `no_card: false`. Wolumen wywnioskowany z zapytania („200”) uruchamia karę za bulk (Photon, Nominatim). Wynik `listed` bez dowodu operacji nie stoi wyżej niż pusty wynik. Dla SMS do klienta Textbelt spada na dół.
   *Uzasadnienie:* błędy rankingu wskazało 5–7 agentów w każdym zadaniu. To ranking decyduje, co agent zobaczy jako pierwsze. *Nakład: średni.*

4. **Instrukcje „kiedy używać” w samym serwerze MCP** (opisy narzędzi i server instructions), nie tylko w skillu Claude'a.
   *Uzasadnienie:* sygnalizował to tylko OpenAI, ale to problem strukturalny. Bez tego produkt jest niewidoczny w ekosystemach innych niż Claude, a wszyscy pozostali testowali z podanym skillem, czyli w warunkach lepszych od realnych. *Nakład: mały.*

5. **Przepisanie wyzwalaczy w skillu** według tabeli z sekcji 5: najpierw podłączone narzędzia, wyjątek przy dostawcy wskazanym przez użytkownika i już podłączonym, wyzwalacz oparty na ograniczeniach (budżet, kraj, wolumen), zasada „znajomość dostawcy ≠ wywoływalne narzędzie”.
   *Uzasadnienie:* 6 agentów wskazało ten sam konflikt reguł, 5 skrytykowało „name the tool”. Błędne wyzwolenie kosztuje więcej niż brak pola (Qwen). *Nakład: mały.*

6. **Status weryfikacji na poziomie wywołania:** `last_live_call: {at, status, redacted_snippet}` dla wywołań tylko do odczytu, a dla płatnych lub mających skutki uboczne sandbox albo schemat opublikowany przez dostawcę. Oddzielić to od `link_check`.
   *Uzasadnienie:* 5 agentów wskazało to jako warunek pominięcia dokumentacji, z progami 7–30 dni. Moonshot: „`link_check.docs: ok` proves a page loads; it proves nothing about the API.” *Nakład: duży* (konta testowe, klucze, cykliczne uruchomienia).

7. **Karta wyniku z polami decyzyjnymi, bez balastu.** Na karcie: `free_plan.kind`, `no_card`, `unit_price`, `endpoint_summary`, numeryczny limit. Bloki `ratings` i pełne konfiguracje MCP przenieść do `get_api`. Dodać parametr `fields`/`verbose`.
   *Uzasadnienie:* łączy postulaty „więcej w wynikach” (DeepSeek, Google, xAI) i „chudsze wyniki” (Qwen, Moonshot, OpenAI). Moonshot szacuje 2–4 tys. tokenów na zapytanie. *Nakład: mały–średni.*

8. **Limity i warunki zależne od zadania, ze źródłem.** Liczbowe limity (zamiast „no published quota” wpisać jawne `unknown` z rekomendowanym tempem), polityka bulk, zachowanie przy 429, zasady przechowywania wyników, szacunkowy koszt dla wolumenu, dosłowny cytat z cennika z datą.
   *Uzasadnienie:* 4–6 agentów. Właśnie tych informacji agenci szukają w dokumentacji przed batchem lub płatnością. *Nakład: średni.*

9. **Pokrycie podstawowych usług i wiele kategorii na wpis.** Dodać Nominatim (z ostrzeżeniem o bulk), Replicate, fal.ai, SMSAPI.pl, Plivo, Bird, AWS SNS. Gdy usługa jest wykluczona, pokazywać `coverage_note`. Freepik powinien być także w `video-generation`.
   *Uzasadnienie:* 5 agentów zauważyło brak Nominatim lub uzupełnień dla wideo i SMS. Brak oczywistej usługi podważa wiarygodność wyników negatywnych. Moonshot: „I can't route around an invisible one.” *Nakład: średni.*

10. **Poprawki dla SMS i operacji z udziałem stron trzecich.** Ceny i ograniczenia zależne od kraju docelowego, a nie domyślnie PL. Jasne rozróżnienie narzędzi do weryfikacji (OTP) i do wysyłki wiadomości. Na karcie wyniku informacja, że trial nie pozwala wysłać SMS do dowolnego numeru. Krótka notka o zgodzie i opt-out.
   *Uzasadnienie:* 3–6 agentów. Tu błąd oznacza realny SMS do klienta albo realny koszt. *Nakład: mały–średni.*

## 7. Cytaty warte zapamiętania

- **OpenAI:** “I would not use its ranking or ‘last checked’ label as authorization to call one without checking the task-specific endpoint, limits and terms.”
- **OpenAI:** “It is labeled a Claude skill, not necessarily an instruction my platform loads.”
- **Google:** “Untrustworthy structured fields defeat the catalog's entire reason for existing over standard web search.”
- **xAI:** “‘No published quota’ is not a rate limit.”
- **xAI:** “If I can name Runway or Nominatim from memory, it reads as permission to skip, which is exactly when bulk bans and trial limits matter.”
- **xAI:** “If those two disagree, I re-check every hit.”
- **DeepSeek:** “At that point, the catalog is a discovery index, not a decision tool.”
- **DeepSeek** (po wytknięciu sprzeczności): “That's not what I'd do in a fresh session. I'd try it, then abandon it fast.”
- **Qwen:** “A messy web result makes me cautious; a confident `"free_tier": true` makes me skip checking.”
- **Qwen:** “Knowing a vendor exists is not having a callable tool.”
- **Moonshot:** “`link_check.docs: ok` proves a page loads; it proves nothing about the API.”
- **Moonshot:** “Returning projected coordinates as ‘lat/lon’ would be a silent, serious error.”
- **Moonshot:** “I can route around a known gap; I can't route around an invisible one.”
- **Moonshot:** “Net: I'd use it, but as a lead, not an answer.”
