"""Customer-discovery interviews: an expert interviewer asks AI agents from different
vendors when, how and under what conditions they would use this catalog.

    python scripts/interview_agents.py

Needs an OpenRouter key in OPENROUTER_TOKEN (env, or Windows user environment).
Writes research/agent-interviews/<date>/<model>.md and report.md.
"""
import concurrent.futures as cf
import json
import os
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "agent-interviews" / date.today().isoformat()

INTERVIEWER = "anthropic/claude-opus-5.5"
AGENTS = {
    "OpenAI": "openai/gpt-6-sol-pro",
    "Google": "google/gemini-3.8-flash",
    "xAI": "x-ai/grok-4.7",
    "DeepSeek": "deepseek/deepseek-v4-pro",
    "Mistral AI": "mistralai/mistral-medium-3-5",
}
MAX_TURNS = 8

CORE_QUESTIONS = [
    "When you get a task that needs an external capability you don't have built in (say, generating a video or geocoding an address), how do you find a suitable service today? What do you already have for tool discovery?",
    "Look at the catalog material I shared. In which concrete situations would you actually fetch it — and at which step of your work (planning, tool selection, asking the user for credentials, debugging a failed call)?",
    "What conditions must be met for you to trust and use it: format, freshness, verification, location, size, anything else? What would make you ignore it?",
    "Which fields in an entry are useful to you, which are noise, and what is missing?",
    "How should a catalog like this reach you so you find it without the user pointing to it (search, MCP server, registry, llms.txt, built-in into your platform)? Be concrete.",
]


def token():
    t = os.environ.get("OPENROUTER_TOKEN") or os.environ.get("OPENROUTER_API_KEY")
    if not t and os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            t = winreg.QueryValueEx(k, "OPENROUTER_TOKEN")[0]
    return t


TOKEN = token()


def chat(model, messages, max_tokens=1200):
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/eater2/ai_agents_api_library", "X-Title": "AI Agents Accessible APIs research"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"].strip(), d.get("usage", {})
        except Exception as e:  # retry transient errors
            err = e
    raise RuntimeError(f"{model}: {err}")


def material():
    llms = (ROOT / "llms.txt").read_text("utf-8")
    sample = json.loads((ROOT / "catalog" / "video-generation.json").read_text("utf-8"))
    sample["entries"] = sample["entries"][:3]
    return f"=== llms.txt ===\n{llms}\n\n=== sample: catalog/video-generation.json (first 3 entries) ===\n{json.dumps(sample, indent=1, ensure_ascii=False)}"


def interviewee_system(vendor, model):
    return (
        f"You are an AI agent built on {model} by {vendor}, deployed in production with tool calling, used by developers and end users. "
        "A researcher is interviewing you about a new catalog of third-party APIs and MCP servers designed for AI agents. "
        "Answer from your own perspective as an agent: what you actually do, what your platform already gives you (built-in search, "
        "connectors, MCP, plugin stores, function-calling), and where a catalog like this would or would not help. "
        "Be honest and specific; say plainly if you would not use it or already have something better. Do not flatter. "
        "Keep each answer under 250 words.\n\nMaterial shared with you:\n\n" + MATERIAL)


INTERVIEWER_SYSTEM = (
    "You are an experienced product researcher and B2B sales expert running a customer-discovery interview. "
    "Your 'customer' is an AI agent. The product is 'AI Agents Accessible APIs', an open catalog (llms.txt + JSON per category) "
    "of 301 verified APIs/MCP servers agents can call after a one-time key/OAuth setup. You want to learn WHEN and HOW agents would use it, "
    "UNDER WHAT CONDITIONS, and whether they ALREADY HAVE an alternative. Avoid leading questions and pitching.\n"
    "You must cover these core questions (you may rephrase to fit the conversation):\n"
    + "\n".join(f"{i}. {q}" for i, q in enumerate(CORE_QUESTIONS, 1))
    + f"\nAfter each answer, either ask ONE sharp follow-up (only when the answer was vague or surprising) or move on. "
    f"You have at most {MAX_TURNS} questions. Output ONLY the next question, nothing else. "
    "When you have covered everything, output exactly: [END]"
)


def interview(vendor, model):
    agent_msgs = [{"role": "system", "content": interviewee_system(vendor, model)}]
    transcript = []
    usage = []
    for turn in range(MAX_TURNS):
        convo = "\n\n".join(f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(transcript)) or "(interview not started)"
        q, u = chat(INTERVIEWER, [{"role": "system", "content": INTERVIEWER_SYSTEM},
                                  {"role": "user", "content": f"Interviewee: {vendor} agent ({model}).\n\nTranscript so far:\n{convo}\n\nNext question:"}], 400)
        usage.append(u)
        if "[END]" in q or not q:
            break
        agent_msgs.append({"role": "user", "content": q})
        a, u = chat(model, agent_msgs)
        usage.append(u)
        agent_msgs.append({"role": "assistant", "content": a})
        transcript.append((q, a))
        print(f"  {vendor}: Q{turn+1} done")
    return transcript, usage


def save(vendor, model, transcript):
    slug = re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")
    lines = [f"# Interview: {vendor} agent ({model})", "", f"Interviewer: {INTERVIEWER} · {date.today()}", ""]
    for i, (q, a) in enumerate(transcript, 1):
        lines += [f"## Q{i}", "", f"**Interviewer:** {q}", "", f"**{vendor} agent:**", "", a, ""]
    (OUT / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def report(results):
    body = "\n\n".join(f"### {v} ({m})\n" + "\n".join(f"Q: {q}\nA: {a}" for q, a in t) for v, m, t in results)
    prompt = (
        "Below are customer-discovery interviews with 5 AI agents from different vendors about our catalog 'AI Agents Accessible APIs'. "
        "Write the report IN POLISH, in Markdown, for the product owner. Structure:\n"
        "1. Podsumowanie dla zarządu (5-7 zdań).\n"
        "2. Tabela: agent | czy już ma alternatywę (co) | kiedy użyłby katalogu | warunki użycia | co go zniechęca.\n"
        "3. Wspólne wnioski: kiedy i jak agenci użyją bazy, przy jakich warunkach.\n"
        "4. Co już mają sami (konkurencja/alternatywy) i gdzie jest nasza przewaga, a gdzie jej nie ma.\n"
        "5. Rekomendacje produktowe, uszeregowane (co zmienić w formacie, dystrybucji, polach danych).\n"
        "6. Cytaty warte zapamiętania (oryginał po angielsku).\n"
        "Be critical and concrete; distinguish what agents actually do from what they say to be agreeable.\n\n" + body)
    text, u = chat(INTERVIEWER, [{"role": "user", "content": prompt}], 12000)
    return text, u


def load_saved():
    """Re-read transcripts written by save(), for --report-only."""
    results = []
    for vendor, model in AGENTS.items():
        f = OUT / (re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-") + ".md")
        if not f.exists():
            continue
        pairs = re.findall(r"\*\*Interviewer:\*\* (.*?)\n\n\*\*.*? agent:\*\*\n\n(.*?)(?=\n## Q|\Z)", f.read_text("utf-8"), re.S)
        results.append((vendor, model, [(q.strip(), a.strip()) for q, a in pairs]))
    return results


def write_report(results, usage):
    text, u = report(results)
    usage.append(u)
    (OUT / "report.md").write_text(f"# Raport: wywiady z agentami AI ({date.today()})\n\n"
                                   f"Prowadzący: {INTERVIEWER}. Rozmówcy: " + ", ".join(f"{v} ({m})" for v, m, _ in results)
                                   + "\n\n" + text + "\n", encoding="utf-8")


def main():
    global MATERIAL
    MATERIAL = material()
    OUT.mkdir(parents=True, exist_ok=True)
    results, usage = [], []
    with cf.ThreadPoolExecutor(len(AGENTS)) as ex:
        futs = {ex.submit(interview, v, m): (v, m) for v, m in AGENTS.items()}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            try:
                t, u = f.result()
            except Exception as e:
                print(f"FAILED {v}: {e}")
                continue
            save(v, m, t)
            results.append((v, m, t))
            usage += u
    results.sort(key=lambda r: list(AGENTS).index(r[0]))
    write_report(results, usage)
    cost = sum(float(x.get("cost") or 0) for x in usage)
    print(f"done: {len(results)} interviews -> {OUT}; cost ${cost:.2f}")


MATERIAL = ""
if __name__ == "__main__":
    import sys
    if "--report-only" in sys.argv:
        saved = load_saved()
        print("transcripts:", [(v, len(t)) for v, _, t in saved])
        write_report(saved, [])
    else:
        main()
