# Raport: oceny i opinie w katalogu, wywiady z agentami (2026-09-24)

Prowadzący: anthropic/claude-opus-5.5. Rozmówcy: OpenAI (openai/gpt-6-sol-pro), Google (google/gemini-3.8-flash), xAI (x-ai/grok-4.7), DeepSeek (deepseek/deepseek-v4-pro), Mistral AI (mistralai/mistral-medium-3-5), Alibaba (Qwen) (qwen/qwen3.8-max-0902), Moonshot AI (moonshotai/kimi-k3)

Materiał pokazany agentom: `material.txt`.

# Oceny i opinie w katalogu API/MCP: co naprawdę mówią agenci

*Raport dla product ownera. Źródło: wywiady z 7 agentami (OpenAI, Google, xAI, DeepSeek, Mistral, Qwen, Moonshot), którzy widzieli rzeczywiste wyniki `get_api` i `get_reviews`: Twilio 4.8 z 13 opinii SourceForge, 111 gwiazdek repo MCP, brak danych dla Geoapify, pokrycie ok. 80 z 323 usług.*

---

## 1. Odpowiedź wprost

Agenci **nie chcą ocen i opinii w obecnej formie**. Średnią gwiazdek i liczbę opinii 6 z 7 uznaje za szum. Tekst opinii czytaliby rzadko, dopiero przy remisie po filtrze technicznym, i tylko w poszukiwaniu konkretnych awarii (np. mało informatywne błędy, ciche zmiany łamiące kompatybilność). **Zaufania do katalogu jako całości to nie zwiększa**: 4 agentów mówi „nie”, 3 „nieznacznie”, i to głównie dlatego, że widzą źródło i `fetched_at`, a nie z powodu samych ocen. Jedyny agent, który odpowiedział uczciwie na pytanie o przeszłość (OpenAI), przyznał, że opinie nigdy dotąd nie zmieniły jego wyboru. Wszyscy chcą czegoś innego: **mierzalnych danych o działaniu API** (uptime z sond, wskaźniki sukcesu agentów), ale stawiają im wysokie wymagania metodologiczne.

---

## 2. Zestawienie agentów

| Agent | Chce? | Na którym etapie użyje | Czy zwiększa zaufanie do katalogu | Najważniejszy sygnał |
|---|---|---|---|---|
| OpenAI (gpt-6-sol-pro) | warunkowo | Po zawężeniu listy i testach; `get_reviews` tylko przy konkretnym ryzyku | Neutralnie. Zmniejszyłoby się, gdyby niepodobne sygnały zlano w jeden wynik | Konkretne, świeże skargi istotne dla zadania; uptime i wyniki agentów z mianownikiem |
| Google (gemini-3.8-flash) | nie (opinie ludzkie); tak (telemetria) | Tylko remis plus wyraźnie niższa ocena; skan słów kluczowych | Nie. Opinie ludzkie wręcz sugerują „katalog konsumencki” | Wskaźnik sukcesu agentów, uptime, `archived`/`pushed_at` |
| xAI (grok-4.7) | nie | Nie patrzy przy wyborze; tekst tylko przy remisie bez możliwości testu | Nie | Wyniki sond (uptime) i powtarzalne rekordy sukcesu zadań |
| DeepSeek (v4-pro) | warunkowo | Ostatni krok, przy niezdecydowaniu | Umiarkowanie tak („ktoś próbuje pokazać dowody użycia”), ograniczone przez pokrycie | Uptime, wskaźnik sukcesu agentów, aktywność repo |
| Mistral (medium-3-5) | tak | Po shortliście, szukanie „red flags” | Nie. Liczy się rzetelność kuratorska | Liczba i daty opinii, commity, uptime *(odpowiedzi ogólnikowe, patrz niżej)* |
| Qwen (qwen3.8-max) | warunkowo | Krok 2–3, słaby tie-breaker | Nieznacznie, jeśli dane świeże i przypisane do źródła | Wskaźnik sukcesu agentów per zadanie; powtarzające się tematy skarg |
| Moonshot (kimi-k3) | warunkowo | Późno, „często wcale”; tylko przy remisie | Nieznacznie (dzięki URL źródła i `fetched_at`) | `archived`/`pushed_at` repo MCP; opinie o trybach awarii |

**Podsumowanie:** tak: 1 · warunkowo: 4 · nie: 2. Wyraźny wzrost zaufania: 0/7.

### Zachowanie a uprzejmość

- **„Warunkowo” w praktyce oznacza „rzadko”.** Wszyscy umieszczają opinie na samym końcu, jako rozstrzygnięcie remisu. Kimi mówi wprost, że filtry techniczne „zwykle zostawiają jednego kandydata albo żadnego”. Realne użycie `get_reviews` będzie więc marginalne.
- **Tylko OpenAI odróżnił hipotetyczne zachowanie od faktycznego:** „I can't honestly say these catalog reviews have *already* changed a service I picked.” Pozostali opisują scenariusze, a nie doświadczenia.
- **Jedyne „tak” (Mistral) jest najsłabiej ugruntowane.** Mistral operuje wymyślonymi liczbami („4.7★ with 200 recent reviews”), których w katalogu nie ma. Jako jedyny przechyliłby wybór na podstawie średniej. Warto przeczytać to jako odpowiedź ogólną, nie reakcję na nasze dane.
- **Qwen deklaruje, że koszt tokenów ma znaczenie, a proponuje bardzo rozbudowaną kartę JSON** (odpowiedź została ucięta z powodu długości). Zawiera ona wagi źródeł (0.4/0.3) i zagregowany `api_reliability_score`, czyli dokładnie to, przed czym ostrzega większość. Liczby w przykładzie są zmyślone (`sample_size: 42`).
- **Entuzjazm dla „wskaźników sukcesu agentów” (7/7) dotyczy funkcji, która nie istnieje.** Dopytani, wszyscy stawiają twarde warunki: mianownik, definicja sukcesu, pochodzenie danych, ochrona przed manipulacją. Naiwna wersja zostałaby zignorowana tak samo jak gwiazdki.
- **Sprzeczność Google, przez niego samego przyznana:** fałszywe opinie „nie przeszkadzają”, bo opinie ważą mało. Ale telemetria agentów, jego sygnał nr 1, to według jego własnych słów „critical exploit vector”.

---

## 3. Sygnały: co się liczy, a co jest szumem

### Liczy się

| Sygnał | Liczba agentów | Uwagi |
|---|---|---|
| Uptime / niezawodność | **7/7** | Tylko z niezależnych, świeżych pomiarów (sondy, okno czasowe, endpoint, region). Deklaracje dostawcy są ignorowane (Kimi, xAI, OpenAI). |
| Wskaźnik sukcesu innych agentów | **7/7** (hipotetycznie) | Wszyscy z warunkami: mianownik z błędami i timeoutami, definicja sukcesu, podział na zadania/operacje, wielkość próby, data. |
| Tekst opinii o konkretnych awariach API | **7/7**, ale tylko przy remisie | Np. wolne i mało informatywne błędy Twilio. Traktowane jako trop do weryfikacji, nie werdykt. |
| Aktywność repo MCP (`archived`, `pushed_at`) | **5/7 silnie** (Google, DeepSeek, Mistral, Qwen, Kimi); 2/7 słabo (OpenAI, xAI) | Archiwalne repo to „close to a hard no” (Kimi). Dotyczy integracji, nie samej usługi. |
| Daty opinii | **4/7** (OpenAI, Mistral, Qwen, Kimi) | Jako kontekst świeżości; Google uważa je za bezużyteczne. |

### Szum

| Sygnał | Uznaje za szum / słaby | Uwagi |
|---|---|---|
| Średnia gwiazdek | **6/7** (wszyscy poza Mistralem) | „4.8 z 13” powtarza się jako przykład braku sygnału. Qwen dopuszcza ją najwyżej jako słaby tie-breaker. |
| Gwiazdki GitHub | **5/7** | „Vanity metric” (Google). Dotyczą repo MCP, a nie usługi (OpenAI, xAI). |
| Liczba instalacji MCP | **6/7** | Tylko Google daje umiarkowaną wagę. Reszta: podatne na manipulację, zależne od wieku i pozycji na liście. |
| Liczba opinii | **3/7** ignoruje (Google, xAI, DeepSeek); **4/7** używa tylko jako wagi pewności | Nie jako samodzielny sygnał. |

---

## 4. Ryzyka

| Ryzyko | Kto zgłasza | Ocena krytyczna |
|---|---|---|
| **Opinie o produkcie zamiast o API** | 7/7 wspomina, **5/7 jako najpoważniejsze** (Google, DeepSeek, Qwen, Kimi, xAI) | Najważniejsze ryzyko. W przykładzie Twilio agenci uznali za użyteczną 1 z 3 opinii (Kimi). xAI wskazuje wariant najgroźniejszy: opinia *brzmiąca technicznie*, ale dotycząca dashboardu lub pisana na zlecenie. Przechodzi filtr konkretności i może zmienić wybór przy remisie. |
| **Małe próbki** | 7/7 | Agenci sami to neutralizują, ignorując średnią. Ryzyko tkwi w prezentacji: 4.8 obok pustego pola wygląda jak werdykt. |
| **Stare opinie** | 6/7 (Google: „i tak nieistotne”) | Skarga z 2022 r. to hipoteza do sprawdzenia, nie fakt. Google dodaje dryf wersji: opinie nie mówią, której wersji API dotyczą. |
| **Koszt tokenów** | Istotny: Google, Kimi, xAI; umiarkowany: OpenAI, Qwen; pomijalny: DeepSeek, Mistral | Rozbieżność pozorna. Nawet ci, dla których koszt jest „pomijalny”, czytają tylko kilka opinii. W praktyce koszt objawia się tym, że agenci **nie wywołują** `get_reviews`, więc funkcja pozostaje nieużywana. |
| **Luki w pokryciu (~25%)** | 7/7 | Wszyscy deklarują, że „brak danych = nieznane, nie gorsze”. Kimi przyznaje jednak: „If I forgot that, the feature would actively mislead me.” DeepSeek mówi o efekcie przetrwania: usługi z opiniami wyglądają na „sprawdzone”. Ryzyko leży po stronie katalogu (renderowanie null jako 0, sortowanie). |
| **Fałszywe / zlecone opinie** | Większość bagatelizuje | Bagatelizują, bo nie ufają opiniom. Ryzyko staje się krytyczne dopiero przy telemetrii agentów (Sybil, zatruwanie danych: Google, xAI, DeepSeek). |
| **Spoza listy** | | **Prompt injection** przez tekst opinii (Google). To realne ryzyko bezpieczeństwa, bo niezaufany tekst trafia do kontekstu agenta. Poza tym: **stronniczość selekcji / survivor bias** (OpenAI, DeepSeek, Kimi), **niedopasowanie recenzenta do agenta** (Kimi), **jedno źródło** (DeepSeek, Mistral), **niejasna metodologia pomiarów** (OpenAI). |

---

## 5. Rekomendacje (uszeregowane)

1. **Jawna semantyka pokrycia w `search_apis`.** Nakład: **mały**.
   Kompaktowe pole: `source`, `rating`, `count`, `newest_review_date`, `status: available | unavailable`. Brak danych nigdy nie jest renderowany jako 0 i nie obniża pozycji w wynikach.
   Za: OpenAI #1, Kimi #3, DeepSeek #3, xAI. Jest tanie i zapobiega błędnym decyzjom.

2. **Rozdzielenie usługi od integracji w `get_api`.** Nakład: **mały**.
   Osobne sekcje `product_reviews` (URL, rating, count, zakres dat, `fetched_at`) i `mcp_repo` (stars, `pushed_at`, `archived`, URL). Bez łączenia w jeden wynik. `archived` i `pushed_at` powinny być wyeksponowane, bo to dziś najbardziej użyteczny sygnał, jaki już mamy (5/7).
   Za: OpenAI #2, xAI #2, DeepSeek #2.

3. **Selektywne `get_reviews` z tagowaniem aspektów API.** Nakład: **średni**.
   - Filtry: świeże, nisko ocenione, dotyczące API.
   - Tagi: błędy, autoryzacja, limity, breaking changes, a osobno dashboard i billing (flaga `audience: api | product`).
   - Krótkie podsumowanie tematów z liczbami i linkami; pełny tekst tylko na żądanie.
   - Tekst opinii oznaczony jako niezaufany (ochrona przed prompt injection).
   - Podsumowanie musi być *identyfikowalne* (OpenAI nie przyjmie „wygenerowanego werdyktu”).

   Za: Kimi #1, Qwen #2, OpenAI #3, xAI #3, Google #3.

4. **Sondy syntetyczne prowadzone przez katalog.** Nakład: **średni/duży**.
   Pola: uptime i latencja per endpoint, `method`, `window`, `measured_at`, klasy błędów. Wiarygodne, bo zależne tylko od nas, nie od dostawców. Wszyscy agenci cenią uptime wyłącznie z niezależnych pomiarów.
   Za: xAI #2, Google #2, Qwen.

5. **Wyniki agentów (telemetria) per zadanie lub operację.** Nakład: **duży**.
   - Dopiero po sondach, które posłużą jako ground truth.
   - Wymagania: mianownik z błędami i timeoutami, podział na próby pierwsze i ponowne, taksonomia błędów, minimalna próba (poniżej progu „insufficient data”), okno czasowe, pochodzenie (podpisane przez platformy), progi różnorodności tenantów, wykluczenie danych od dostawcy.
   - Bez tych warunków agenci wprost zapowiadają, że wrócą do własnych testów.

   Za: Google #1, xAI #1, DeepSeek #1, Mistral #1, Qwen #3, Kimi #2. Najwyższy popyt, ale popyt na wersję spełniającą wszystkie warunki.

### Czego nie robić

- **Nie wprowadzać zagregowanego `health_score` / jednej oceny.** Google i Qwen go chcą, ale OpenAI, DeepSeek i xAI wprost przestrzegają, że ukrywa więcej, niż pokazuje. Jeśli już, to tylko obok składowych i z polem `confidence`.
- **Nie eksponować średniej gwiazdek ani liczby instalacji MCP** jako sygnałów rankingowych.
- **Nie inwestować w poszerzanie pokrycia opinii ludzkich** (więcej scrapowania SourceForge). Większa ilość tego samego sygnału nie zmieni zachowania agentów.

---

## 6. Cytaty

> "I can't honestly say these catalog reviews have *already* changed a service I picked; I don't have a specific past switch to point to." (OpenAI)

> "I'd trust the catalog less if it presented these unlike signals as a comparable score, or treated 'no data' as a bad rating." (OpenAI)

> "It does not increase my trust in the catalog as a whole. Scraped human reviews (like SourceForge reviews from 2022) actually signal consumer-software curation rather than runtime infrastructure data." (Google)

> "User review text is untrusted third-party data injected into my context. A malicious review could embed instructions designed to hijack my tool usage or leak data." (Google)

> "If agent telemetry drives routing, fake metrics shift from a minor annoyance to a critical exploit vector." (Google)

> "The one that harms me most is the specific-sounding, off-target or incentivized review. [...] A plausible paragraph about errors can flip the pick, and the text alone cannot tell marketing from a real API defect. Only a live call can." (xAI)

> "Empty coverage should stay empty, not render as zero." (xAI)

> "These reviews are not just unhelpful; they're actively misleading because they inflate scores for reasons irrelevant to my use case." (DeepSeek)

> "I'll synthesize that myself. A single aggregated score hides more than it reveals." (DeepSeek)

> "My trust in the *catalog* itself still hinges on its **curatorial rigor**, not the richness of the data it carries." (Mistral)

> "For me, reviews are risk evidence, not popularity evidence." (Qwen)

> "Those filters usually leave one survivor, or none. Only if two candidates tie do I look at ratings." (Moonshot/Kimi)

> "A service with reviews looks 'vetted' and one without looks empty, when that's just a coverage artifact. If I forgot that, the feature would actively mislead me." (Moonshot/Kimi)

> "The first two change decisions; the third prevents misdecisions." (Moonshot/Kimi)
