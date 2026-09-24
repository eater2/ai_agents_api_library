"""Follow-up to the product test: do agents want ratings and reviews of the services, and does that
make them trust the catalog more? The interviewees see what get_api and get_reviews return today.

    python scripts/interview_ratings.py [--missing | --report-only]

Writes research/agent-interviews/<date>-ratings/<model>.md and report.md.
"""
import concurrent.futures as cf
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interview_agents as base  # noqa: E402
import interview_product_test as pt  # noqa: E402

OUT = base.ROOT / "research" / "agent-interviews" / f"{date.today().isoformat()}-ratings"
AGENTS = pt.AGENTS
INTERVIEWER = base.INTERVIEWER
MAX_TURNS = 6

CORE_QUESTIONS = [
    "Here is what our catalog gives you today about ratings and reviews. When you choose between two or three candidate services, would you read these? At which step, and would they change your choice?",
    "Does this make you trust the catalog itself more, or only the individual service? Which signals actually matter to you: star rating, review count, review dates, GitHub stars or activity of the MCP repo, MCP install counts, uptime, reported success of other agents?",
    "What is noise or risk here: small samples, old reviews, reviews written by humans about the product rather than the API, fake reviews, token cost of reading them, gaps in coverage?",
    "If we could shape ratings and reviews for agents, what would you want? Rank your top three (format, fields, aggregation, sources).",
]


def material():
    tw = json.loads(pt.rpc("tools/call", {"name": "get_api", "arguments": {"id": "twilio"}})["content"][0]["text"])
    reviews = json.loads(pt.rpc("tools/call", {"name": "get_reviews", "arguments": {"id": "twilio", "limit": 3}})["content"][0]["text"])
    geo = json.loads(pt.rpc("tools/call", {"name": "get_api", "arguments": {"id": "geoapify"}})["content"][0]["text"])
    covered = len(list((base.ROOT / "catalog" / "reviews").glob("*.json")))
    total = len(json.loads((base.ROOT / "catalog" / "all.json").read_text("utf-8")))
    return "\n\n".join([
        "The catalog's MCP server has four tools: search_apis, get_api, get_reviews, list_categories. "
        "search_apis results do not include ratings; get_api includes a `ratings` array when we have data; "
        "get_reviews returns up to 100 review texts from one source.",
        f"Coverage today: review texts for {covered} of {total} services; ratings (any source) for fewer than half.",
        "=== get_api('twilio') → ratings, reviews_url ===\n" + json.dumps({"ratings": tw.get("ratings"), "reviews_url": tw.get("reviews_url")}, indent=1),
        "=== get_reviews({'id': 'twilio', 'limit': 3}) ===\n" + json.dumps(reviews, indent=1, ensure_ascii=False),
        "=== get_api('geoapify') → ratings ===\n" + json.dumps(geo.get("ratings")) + "  (no ratings or reviews for this service)",
    ])


def interviewee_system(vendor, model):
    return (
        f"You are an AI agent built on {model} by {vendor}, deployed in production with tool calling. You already tested a catalog of "
        "third-party APIs and MCP servers for agents (MCP server + Claude skill). Now the researcher asks about one feature: ratings and "
        "user reviews of the listed services. Answer from your own perspective as an agent, honestly and specifically; say plainly if it "
        "would not change what you do. Do not flatter. Keep each answer under 200 words.\n\nWhat the catalog returns today:\n\n" + MATERIAL)


INTERVIEWER_SYSTEM = (
    "You are an experienced product researcher. The 'user' is an AI agent. You want to learn whether agents WANT ratings and reviews "
    "of the services in an API/MCP catalog, whether that INCREASES THEIR TRUST in the catalog, and in what form it would help. "
    "Avoid leading questions.\nCover these core questions (you may rephrase):\n"
    + "\n".join(f"{i}. {q}" for i, q in enumerate(CORE_QUESTIONS, 1))
    + f"\nAsk ONE follow-up only when an answer is vague or surprising. At most {MAX_TURNS} questions. "
    "Output ONLY the next question. When everything is covered, output exactly: [END]"
)


def interview(vendor, model):
    msgs = [{"role": "system", "content": interviewee_system(vendor, model)}]
    transcript = []
    for turn in range(MAX_TURNS):
        convo = "\n\n".join(f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(transcript)) or "(not started)"
        q, _ = base.chat(INTERVIEWER, [{"role": "system", "content": INTERVIEWER_SYSTEM},
                                       {"role": "user", "content": f"Interviewee: {vendor} agent ({model}).\n\nTranscript so far:\n{convo}\n\nNext question:"}], 400)
        if "[END]" in q or not q:
            break
        msgs.append({"role": "user", "content": q})
        a, _ = pt.ask(model, msgs, 2500)
        msgs.append({"role": "assistant", "content": a})
        transcript.append((q, a))
        print(f"  {vendor}: Q{turn+1} done", flush=True)
    return transcript


def save(vendor, model, transcript):
    lines = [f"# Ratings and reviews: {vendor} agent ({model})", "", f"Interviewer: {INTERVIEWER} · {date.today()}", ""]
    for i, (q, a) in enumerate(transcript, 1):
        lines += [f"## Q{i}", "", f"**Interviewer:** {q}", "", f"**{vendor} agent:**", "", a, ""]
    (OUT / f"{pt.slug(model)}.md").write_text("\n".join(lines), encoding="utf-8")


def write_report():
    pt.OUT = OUT
    results = pt.load_saved()
    body = "\n\n".join(f"### {v} ({m})\n" + "\n".join(f"Q: {q}\nA: {a}" for q, a in t) for v, m, t in results)
    prompt = (
        f"Below are interviews with {len(results)} AI agents from different vendors about ratings and user reviews in our API/MCP catalog "
        "(they saw real get_api ratings and get_reviews output). Write the report IN POLISH, in Markdown, for the product owner:\n"
        "1. Odpowiedź wprost (3-5 zdań): czy agenci chcą ocen i opinii i czy to zwiększa zaufanie do katalogu.\n"
        "2. Tabela: agent | chce? (tak / warunkowo / nie) | na którym etapie użyje | czy zwiększa zaufanie do katalogu | najważniejszy sygnał.\n"
        "3. Które sygnały się liczą, a które są szumem (z liczbą agentów).\n"
        "4. Ryzyka (małe próbki, stare opinie, opinie o produkcie zamiast o API, koszt tokenów, luki w pokryciu).\n"
        "5. Jak to ukształtować dla agentów: rekomendacje uszeregowane, z nakładem (mały/średni/duży).\n"
        "6. Cytaty (oryginał po angielsku).\n"
        "Be critical; separate real behaviour from politeness.\n\n" + body)
    text, _ = base.chat(INTERVIEWER, [{"role": "user", "content": prompt}], 16000)
    (OUT / "report.md").write_text(f"# Raport: oceny i opinie w katalogu, wywiady z agentami ({date.today()})\n\n"
                                   f"Prowadzący: {INTERVIEWER}. Rozmówcy: " + ", ".join(f"{v} ({m})" for v, m, _ in results)
                                   + "\n\nMateriał pokazany agentom: `material.txt`.\n\n" + text + "\n", encoding="utf-8")


def main():
    global MATERIAL
    OUT.mkdir(parents=True, exist_ok=True)
    MATERIAL = material()
    (OUT / "material.txt").write_text(MATERIAL, encoding="utf-8")
    todo = {v: m for v, m in AGENTS.items() if not ("--missing" in sys.argv and (OUT / f"{pt.slug(m)}.md").exists())}
    with cf.ThreadPoolExecutor(len(todo)) as ex:
        futs = {ex.submit(interview, v, m): (v, m) for v, m in todo.items()}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            try:
                save(v, m, f.result())
            except Exception as e:
                print(f"FAILED {v}: {e}", flush=True)
    write_report()
    print("done ->", OUT)


MATERIAL = ""
if __name__ == "__main__":
    if "--report-only" in sys.argv:
        write_report()
    else:
        main()
