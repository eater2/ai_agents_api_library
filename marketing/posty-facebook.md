# Posty na Facebooka: grupy o Claude, Claude Code, MCP i agentach AI

Propozycje do wklejenia. Zasady, żeby moderatorzy nie usuwali postów jako spamu:

- Jeden post na grupę i nie wszędzie tego samego dnia; teksty różnią się kątem.
- Najpierw przeczytaj regulamin grupy: część pozwala na autopromocję tylko w wątkach tygodniowych („Show & tell”, „Self-promo Saturday”).
- Link najlepiej w pierwszym komentarzu (FB ucina zasięg postów z linkiem), w treści: „link w komentarzu”.
- Dołącz obrazek: `docs/icon.png` albo zrzut ekranu z odpowiedzią Claude'a (np. wynik `search_apis` z opiniami).
- Odpowiadaj na komentarze w ciągu pierwszej godziny.

Linki:
- Strona: https://eater2.github.io/ai_agents_api_library/
- GitHub: https://github.com/eater2/ai_agents_api_library
- Endpoint MCP (bez klucza): https://ai-agents-api-library.vercel.app/mcp

Liczby aktualne na 2026-10-14 (v0.3.10): 333 serwisy, 29 kategorii, 4 narzędzia MCP. Przed publikacją sprawdź liczby w README.

---

## PL 1: polskie grupy o Claude / AI (ogólny)

> Zrobiłem darmowy katalog API dla agentów AI, z którego Claude korzysta sam 🤖
>
> Problem: prosisz Claude'a o coś, czego nie umie zrobić sam (wysłać SMS, wygenerować wideo, zgeokodować adres), a on zgaduje, jakiego serwisu użyć, albo wymyśla endpointy.
>
> Rozwiązanie: AI Agents API Library to otwarty katalog 330+ API i serwerów MCP w 29 kategoriach. Przy każdym: link do oficjalnej dokumentacji, jaki klucz trzeba podać, czy jest darmowy plan, czy jest oficjalny serwer MCP i kiedy wpis był ostatnio sprawdzany. Do tego opinie użytkowników (G2, Capterra, SourceForge), liczba pobrań SDK i codzienny test dostępności.
>
> Podłączasz to do Claude'a jako serwer MCP, bez klucza i bez instalacji:
> `https://ai-agents-api-library.vercel.app/mcp`
>
> Działa w Claude Code, Claude Desktop i claude.ai (Ustawienia → Konektory → Dodaj własny). Kod otwarty (MIT), przyjmuję poprawki.
>
> Link w komentarzu 👇 Chętnie usłyszę, jakich serwisów brakuje.

## PL 2: grupy programistów / Claude Code (techniczny)

> Dla użytkowników Claude Code: plugin, który podpowiada Claude'owi, jakiego zewnętrznego API użyć
>
> ```
> /plugin marketplace add eater2/ai_agents_api_library
> /plugin install ai-agents-api-library@eater2
> ```
>
> W środku są skill i serwer MCP z 4 narzędziami:
> • `search_apis`: szukanie po zadaniu, z filtrami: bez klucza, darmowy plan, bez karty, oficjalny MCP, minimalna ocena, liczba opinii, popularność SDK
> • `get_api`: auth, przykładowe wywołanie, linki do docs/OpenAPI/llms.txt
> • `get_reviews`: opinie użytkowników z plusami i minusami
> • `list_categories`
>
> Wolisz bez pluginu? `claude mcp add --transport http ai-agents-api-library https://ai-agents-api-library.vercel.app/mcp`
>
> Katalog to zwykły JSON w repo. Każdy wpis linkuje do oficjalnej dokumentacji producenta i ma datę ostatniego sprawdzenia, a codzienny skrypt testuje dostępność i handshake MCP. Jest też w oficjalnym MCP Registry i na Smithery.
>
> Repo w komentarzu. Gwiazdka ⭐ albo PR z nowym serwisem mile widziane.

## PL 3: krótki, z przykładem (do grup z dużym ruchem)

> Zapytałem Claude'a: „Potrzebuję API do wysyłki SMS, z darmowym limitem i dobrymi opiniami”.
>
> Zamiast zgadywać, sprawdził w katalogu AI Agents API Library: dostałem 3 serwisy posortowane po ocenach użytkowników, z informacją, co ludzie chwalą, a na co narzekają, jaki klucz założyć i gdzie.
>
> Darmowy serwer MCP, bez klucza: https://ai-agents-api-library.vercel.app/mcp
> Szczegóły w komentarzu.

(Przed publikacją zrób prawdziwe zapytanie i wstaw zrzut ekranu z faktyczną odpowiedzią; nie opisuj wyniku, którego nie było.)

---

## EN 1: international Claude / Anthropic groups

> I built a free catalog of APIs that Claude can look up by itself 🤖
>
> When you ask Claude to do something it can't do natively (send an SMS, generate a video, geocode an address), it has to guess which service to use, and sometimes invents endpoints.
>
> AI Agents API Library is an open catalog of 330+ APIs and MCP servers in 29 categories. Each entry has the official docs link, which key to ask you for, the free tier, whether there's an official MCP server, and a last-checked date. It also includes user ratings (G2, Capterra, SourceForge), SDK download counts and a daily uptime check.
>
> Connect it as a remote MCP server, with no key and no install:
> `https://ai-agents-api-library.vercel.app/mcp`
>
> It works in Claude Code, Claude Desktop and claude.ai (Settings → Connectors → Add custom connector). It's MIT-licensed, and contributions are welcome.
>
> Link in the first comment. Which services are missing?

## EN 2: Claude Code / MCP developer groups

> Claude Code plugin: lets Claude pick third-party APIs from data instead of guessing
>
> ```
> /plugin marketplace add eater2/ai_agents_api_library
> /plugin install ai-agents-api-library@eater2
> ```
>
> It bundles a skill and an MCP server with 4 tools: `search_apis` (filters: no auth, free tier, no card, official MCP, min rating, min reviews, SDK downloads; sort by fit, rating or usage), `get_api` (auth plus an example call), `get_reviews` (pros and cons from user reviews) and `list_categories`.
>
> Every entry links to the vendor's official docs and carries a last-checked date. A daily job probes uptime and the MCP handshake. It's listed in the official MCP Registry (`io.github.eater2/ai-agents-api-library`) and on Smithery.
>
> Repo in the comments. Feedback and PRs welcome.

## EN 3: AI agents / automation groups (n8n, LangChain, agent builders)

> Building agents? You don't need Claude to use this.
>
> The whole catalog is plain JSON with an `llms.txt`, so any agent (GPT, Gemini, LangChain, n8n) can read it directly:
> • 330+ APIs and MCP servers, 29 categories
> • for each one: auth type, free tier, official MCP endpoint, SDK, OpenAPI, llms.txt
> • user ratings and usage signals to choose between similar services
>
> There's also an MCP endpoint, free with no key: https://ai-agents-api-library.vercel.app/mcp
>
> Open source (MIT). Link in the comments.

---

## Pierwszy komentarz (pod każdym postem)

> 🔗 Strona: https://eater2.github.io/ai_agents_api_library/
> 💻 GitHub: https://github.com/eater2/ai_agents_api_library
> 🔌 MCP: https://ai-agents-api-library.vercel.app/mcp

## Gdzie szukać grup (wpisz w wyszukiwarkę FB i sprawdź aktywność oraz regulamin)

- PL: „Claude AI Polska”, „ChatGPT i AI Polska”, „Sztuczna inteligencja”, „AI dla programistów”, „Programiści Polska”, „n8n Polska”
- EN: „Claude AI”, „Anthropic Claude Users”, „Claude Code”, „Model Context Protocol (MCP)”, „AI Agents”, „n8n Community”, „LangChain”, „Prompt Engineering”

Grup nie sprawdzałem; to tylko frazy do wyszukania. Unikaj grup bez moderacji, pełnych spamu: posty giną tam bez odzewu.
