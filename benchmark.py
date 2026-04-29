import asyncio
import time
import json
from datetime import datetime
from ollama import AsyncClient

MODELS = [
    "qwen3:8b",
    "qwen3:32b",
    "gemma3:27b",
]

SYSTEM_PROMPT = (
    "Du bist ein freundlicher Assistent. Antworte immer auf Deutsch. "
    "Benutze keine Emojis oder Sonderzeichen."
)

TESTS = [
    {
        "id": "smalltalk",
        "label": "Small Talk",
        "prompt": "Hallo! Wie geht es dir? Was machst du so den ganzen Tag?",
    },
    {
        "id": "reasoning",
        "label": "Reasoning / längere Antwort",
        "prompt": (
            "Ein älterer Bewohner in einem Pflegeheim fühlt sich einsam und hat "
            "Heimweh nach seiner Heimatstadt. Wie würdest du das Gespräch mit ihm "
            "einfühlsam führen?"
        ),
    },
    {
        "id": "tool_calling",
        "label": "Tool Calling",
        "prompt": "Wie ist gerade das Wetter in Hamburg? Scheint die Sonne?",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_temperature",
                    "description": "Gibt die aktuelle Temperatur an einem Ort zurück.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_rain",
                    "description": "Gibt aktuelle Niederschlagsdaten zurück.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                },
            },
        ],
    },
]


async def run_test(client: AsyncClient, model: str, test: dict) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": test["prompt"]},
    ]
    tools = test.get("tools")

    start = time.perf_counter()
    first_token_at = None
    content = ""
    tool_calls_made = []

    async for chunk in await client.chat(
        model=model,
        messages=messages,
        tools=tools or [],
        stream=True,
    ):
        msg = chunk.message
        if first_token_at is None and (msg.content or msg.tool_calls):
            first_token_at = time.perf_counter()
        if msg.content:
            content += msg.content
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_made.append({
                    "name": tc.function.name,
                    "arguments": dict(tc.function.arguments),
                })
        if chunk.done:
            end = time.perf_counter()
            ttft = round((first_token_at - start) * 1000) if first_token_at else None
            total_ms = round((end - start) * 1000)
            eval_tokens = chunk.eval_count or 0
            eval_ns = chunk.eval_duration or 0
            tps = round(eval_tokens / (eval_ns / 1e9), 1) if eval_ns else None
            return {
                "test_id": test["id"],
                "label": test["label"],
                "prompt": test["prompt"],
                "response": content.strip(),
                "tool_calls": tool_calls_made,
                "ttft_ms": ttft,
                "total_ms": total_ms,
                "eval_tokens": eval_tokens,
                "tokens_per_sec": tps,
            }


async def benchmark_model(client: AsyncClient, model: str) -> dict:
    print(f"\n{'='*60}")
    print(f"Modell: {model}")
    print(f"{'='*60}")
    results = []
    for test in TESTS:
        print(f"  [{test['id']}] {test['label']}...", end=" ", flush=True)
        try:
            result = await run_test(client, model, test)
            results.append(result)
            print(f"TTFT: {result['ttft_ms']}ms | Total: {result['total_ms']}ms | {result['tokens_per_sec']} tok/s")
            if result["tool_calls"]:
                print(f"         Tool aufgerufen: {result['tool_calls']}")
        except Exception as e:
            print(f"FEHLER: {e}")
            results.append({"test_id": test["id"], "label": test["label"], "error": str(e)})
    return {"model": model, "results": results}


def render_markdown(all_results: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Modell-Benchmark",
        f"Zuletzt ausgeführt: {now}",
        "",
        "Getestete Modelle auf dem NVIDIA Spark via Ollama.",
        "Metriken: TTFT = Time to First Token, tok/s = generierte Tokens pro Sekunde.",
        "",
    ]

    for entry in all_results:
        model = entry["model"]
        lines += [f"## {model}", ""]

        # Tabelle
        lines.append("| Test | TTFT (ms) | Gesamt (ms) | Tokens | tok/s | Tool aufgerufen |")
        lines.append("|---|---|---|---|---|---|")
        for r in entry["results"]:
            if "error" in r:
                lines.append(f"| {r['label']} | – | – | – | – | Fehler: {r['error']} |")
            else:
                tools_str = ", ".join(tc["name"] for tc in r.get("tool_calls", [])) or "–"
                lines.append(
                    f"| {r['label']} "
                    f"| {r.get('ttft_ms', '–')} "
                    f"| {r.get('total_ms', '–')} "
                    f"| {r.get('eval_tokens', '–')} "
                    f"| {r.get('tokens_per_sec', '–')} "
                    f"| {tools_str} |"
                )
        lines.append("")

        # Beispielantworten
        lines.append("### Beispielantworten")
        lines.append("")
        for r in entry["results"]:
            if "error" in r:
                continue
            lines.append(f"**{r['label']}**")
            lines.append(f"> {r['prompt']}")
            lines.append("")
            if r.get("tool_calls"):
                for tc in r["tool_calls"]:
                    lines.append(f"*Tool: `{tc['name']}` mit `{json.dumps(tc['arguments'], ensure_ascii=False)}`*")
                lines.append("")
            if r.get("response"):
                lines.append(r["response"])
            lines.append("")

    return "\n".join(lines)


async def main():
    client = AsyncClient()
    all_results = []

    for model in MODELS:
        result = await benchmark_model(client, model)
        all_results.append(result)

    md = render_markdown(all_results)
    with open("cloud.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nErgebnisse gespeichert in cloud.md")


asyncio.run(main())