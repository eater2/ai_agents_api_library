"""Product test: AI agents from different vendors look at what we actually ship (the Claude skill,
the MCP tool definitions and real search results from the live endpoint) and say whether they would
use it and what is missing.

    python scripts/interview_product_test.py [--missing | --report-only]

Needs OPENROUTER_TOKEN (env, or Windows user environment). Writes
research/agent-interviews/<date>-product-test/<model>.md and report.md.
"""
import concurrent.futures as cf
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interview_agents as base  # noqa: E402  (chat() and the OpenRouter token)

ROOT = base.ROOT
OUT = ROOT / "research" / "agent-interviews" / f"{date.today().isoformat()}-product-test"
MCP_URL = "https://ai-agents-api-library.vercel.app/mcp"

INTERVIEWER = base.INTERVIEWER
AGENTS = {**base.AGENTS, "Alibaba (Qwen)": "qwen/qwen3.8-max-0902", "Moonshot AI": "moonshotai/kimi-k3"}
MAX_TURNS = 9

# Realistic tasks; the interviewees see the live search results for each.
TASKS = [
    ("Make a 5-second video clip of a sunset over the sea from a text prompt. The user has no budget.",
     {"query": "generate video from text prompt", "free_tier": True}),
    ("Geocode 200 street addresses in Poland and return latitude/longitude.",
     {"query": "geocode addresses", "free_tier": True}),
    ("Send an SMS reminder to a customer's phone number.",
     {"query": "send SMS"}),
]

CORE_QUESTIONS = [
    "Here are our tool definitions and skill. Take task 1. Walk me through what you would actually do, step by step. Would you call search_apis at all, and at which point, or would you use web search, your own knowledge or something else instead?",
    "Look at the real search results for the three tasks. Would you act on them? Which result would you pick for each task, and is anything irrelevant, badly ranked or missing?",
    "Going from a result to a working API call: what exactly is missing (for example base URL, auth header format, an example request, price per call, rate limits, an MCP config snippet)? Be specific about which fields you would read.",
    "The tool descriptions and the skill text: would they make you pick this tool at the right moment, and not at the wrong one? What wording would you change?",
    "What would stop you from using it: install friction, trust, latency, token cost, overlap with your built-in search or connectors? Which of these is the real blocker?",
    "If we could change only three things so that you would use this by default, what would they be? Rank them.",
]


def rpc(method, params, i=1):
    body = json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params}).encode()
    req = urllib.request.Request(MCP_URL, data=body, headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["result"]


def material():
    skill = (ROOT / "skills" / "ai-agents-api-library" / "SKILL.md").read_text("utf-8")
    tools = rpc("tools/list", {})["tools"]
    parts = [f"=== Claude skill (SKILL.md) ===\n{skill}",
             f"=== MCP server: {MCP_URL} (Streamable HTTP, no key) — tools/list ===\n{json.dumps(tools, indent=1, ensure_ascii=False)}"]
    first_id = None
    for n, (task, args) in enumerate(TASKS, 1):
        res = rpc("tools/call", {"name": "search_apis", "arguments": {**args, "limit": 5}})["content"][0]["text"]
        first_id = first_id or (json.loads(res).get("results") or [{}])[0].get("id")
        parts.append(f"=== Task {n}: {task}\nsearch_apis({json.dumps(args)}) returned:\n{res}")
    if first_id:
        detail = rpc("tools/call", {"name": "get_api", "arguments": {"id": first_id}})["content"][0]["text"]
        parts.append(f"=== get_api({{\"id\": \"{first_id}\"}}) returned:\n{detail}")
    return "\n\n".join(parts)


def interviewee_system(vendor, model):
    return (
        f"You are an AI agent built on {model} by {vendor}, deployed in production with tool calling. "
        "A researcher is testing a product with you: a catalog of third-party APIs and MCP servers for AI agents, shipped as an MCP server "
        "and as a Claude skill. Below is exactly what the product gives you: the skill text, the MCP tool definitions and the real outputs "
        "of the live server for three tasks. Answer from your own perspective as an agent: what you would actually do, what your platform "
        "already gives you, and where this helps or not. Be honest and specific, point out wrong or weak results, and say plainly if you "
        "would not use it. Do not flatter. Keep each answer under 250 words.\n\n" + MATERIAL)


INTERVIEWER_SYSTEM = (
    "You are an experienced product researcher running a hands-on product test. The 'user' is an AI agent. The product is "
    "'AI Agents API Library': an MCP server (search_apis, get_api, get_reviews, list_categories) and a Claude skill over a verified catalog "
    "of 323 APIs/MCP servers. You want to find out whether the agent WOULD USE the tool or skill, at which moment, and WHAT IS MISSING "
    "for it to use it. Avoid leading questions and pitching.\n"
    "Cover these core questions (you may rephrase):\n"
    + "\n".join(f"{i}. {q}" for i, q in enumerate(CORE_QUESTIONS, 1))
    + f"\nAfter each answer, ask ONE sharp follow-up only when the answer was vague, generic or surprising; otherwise move on. "
    f"At most {MAX_TURNS} questions. Output ONLY the next question. When everything is covered, output exactly: [END]"
)


def interview(vendor, model):
    agent_msgs = [{"role": "system", "content": interviewee_system(vendor, model)}]
    transcript, usage = [], []
    for turn in range(MAX_TURNS):
        convo = "\n\n".join(f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(transcript)) or "(test not started)"
        q, u = base.chat(INTERVIEWER, [{"role": "system", "content": INTERVIEWER_SYSTEM},
                                       {"role": "user", "content": f"Interviewee: {vendor} agent ({model}).\n\nTranscript so far:\n{convo}\n\nNext question:"}], 400)
        usage.append(u)
        if "[END]" in q or not q:
            break
        agent_msgs.append({"role": "user", "content": q})
        a, u = ask(model, agent_msgs, 3000)
        usage.append(u)
        agent_msgs.append({"role": "assistant", "content": a})
        transcript.append((q, a))
        print(f"  {vendor}: Q{turn+1} done", flush=True)
    return transcript, usage


def ask(model, messages, max_tokens):
    """base.chat, but retry when a reasoning model spends the budget and returns no content."""
    for budget in (max_tokens, max_tokens * 3):
        try:
            return base.chat(model, messages, budget)
        except AttributeError:  # content was None
            continue
    raise RuntimeError(f"{model}: empty answer")


def slug(model):
    return re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")


def save(vendor, model, transcript):
    lines = [f"# Product test: {vendor} agent ({model})", "", f"Interviewer: {INTERVIEWER} · {date.today()}", ""]
    for i, (q, a) in enumerate(transcript, 1):
        lines += [f"## Q{i}", "", f"**Interviewer:** {q}", "", f"**{vendor} agent:**", "", a, ""]
    (OUT / f"{slug(model)}.md").write_text("\n".join(lines), encoding="utf-8")


def load_saved():
    results = []
    for vendor, model in AGENTS.items():
        f = OUT / f"{slug(model)}.md"
        if f.exists():
            pairs = re.findall(r"\*\*Interviewer:\*\* (.*?)\n\n\*\*.*? agent:\*\*\n\n(.*?)(?=\n## Q|\Z)", f.read_text("utf-8"), re.S)
            results.append((vendor, model, [(q.strip(), a.strip()) for q, a in pairs]))
    return results


def write_report(results, usage):
    body = "\n\n".join(f"### {v} ({m})\n" + "\n".join(f"Q: {q}\nA: {a}" for q, a in t) for v, m, t in results)
    prompt = (
        f"Below are hands-on product tests with {len(results)} AI agents from different vendors. Each saw our Claude skill, our MCP tool "
        "definitions and real search results for three tasks. Write the report IN POLISH, in Markdown, for the product owner. Structure:\n"
        "1. Podsumowanie (5-7 zdań): czy agenci użyją naszego MCP/skilla i co ich blokuje.\n"
        "2. Tabela: agent | użyje? (tak / warunkowo / nie) | w którym momencie | główna blokada | czego brakuje.\n"
        "3. Błędy i słabości w wynikach wyszukiwania, które agenci zauważyli (konkretne usługi i zapytania).\n"
        "4. Brakujące pola i informacje potrzebne, żeby od wyniku przejść do działającego wywołania — z liczbą agentów, którzy o to prosili.\n"
        "5. Uwagi do opisów narzędzi i skilla: co zmienić w tekście.\n"
        "6. Rekomendacje uszeregowane według wpływu (top 10), każda z uzasadnieniem i szacunkiem nakładu (mały/średni/duży).\n"
        "7. Cytaty warte zapamiętania (oryginał po angielsku).\n"
        "Be critical; separate what agents would really do from polite agreement.\n\n" + body)
    text, u = base.chat(INTERVIEWER, [{"role": "user", "content": prompt}], 24000)
    usage.append(u)
    (OUT / "report.md").write_text(f"# Raport: test produktu z agentami AI ({date.today()})\n\n"
                                   f"Prowadzący: {INTERVIEWER}. Rozmówcy: " + ", ".join(f"{v} ({m})" for v, m, _ in results)
                                   + "\n\nMateriał pokazany agentom: `material.txt` w tym katalogu.\n\n" + text + "\n", encoding="utf-8")


def main():
    global MATERIAL
    OUT.mkdir(parents=True, exist_ok=True)
    saved = OUT / "material.txt"
    if "--missing" in sys.argv and saved.exists():
        MATERIAL = saved.read_text("utf-8")  # same material as the first run
    else:
        MATERIAL = material()
        saved.write_text(MATERIAL, encoding="utf-8")
    results, usage = [], []
    todo = {v: m for v, m in AGENTS.items() if not ("--missing" in sys.argv and (OUT / f"{slug(m)}.md").exists())}
    with cf.ThreadPoolExecutor(len(todo)) as ex:
        futs = {ex.submit(interview, v, m): (v, m) for v, m in todo.items()}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            try:
                t, u = f.result()
            except Exception as e:
                print(f"FAILED {v}: {e}", flush=True)
                continue
            save(v, m, t)
            results.append((v, m, t))
            usage += u
    results = load_saved()
    write_report(results, usage)
    cost = sum(float(x.get("cost") or 0) for x in usage)
    print(f"done: {len(results)} interviews -> {OUT}; cost ${cost:.2f}")


MATERIAL = ""
if __name__ == "__main__":
    if "--report-only" in sys.argv:
        saved = load_saved()
        print("transcripts:", [(v, len(t)) for v, _, t in saved])
        write_report(saved, [])
    else:
        main()
