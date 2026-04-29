import asyncio
import time
import json
import psutil
from pathlib import Path
from datetime import datetime
from ollama import AsyncClient

OUTPUT_FILE = Path(__file__).parent / "benchmark_results.md"

try:
    import pynvml
    pynvml.nvmlInit()
    _GPU_HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False

MODELS = [
    "qwen3:8b",
    "qwen3:32b",
    "mistral:7b",
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


def _gpu_snapshot():
    if not NVML_AVAILABLE:
        return None
    try:
        util = pynvml.nvmlDeviceGetUtilizationRates(_GPU_HANDLE)
        gpu_util = util.gpu
    except pynvml.NVMLError:
        gpu_util = None
    try:
        mem = pynvml.nvmlDeviceGetMemoryInfo(_GPU_HANDLE)
        gpu_mem_used = round(mem.used / 1024**2)
    except pynvml.NVMLError:
        gpu_mem_used = None  # GB10 (Unified Memory) unterstützt kein separates VRAM-Query
    return {
        "gpu_util_pct": gpu_util,
        "gpu_mem_used_mb": gpu_mem_used,
    }


class SystemSampler:
    def __init__(self):
        self.cpu_samples = []
        self.ram_samples = []
        self.gpu_util_samples = []
        self.gpu_mem_samples = []
        self._stop = False
        self._task = None

    async def _loop(self):
        psutil.cpu_percent()  # initialize counter
        while not self._stop:
            self.cpu_samples.append(psutil.cpu_percent())
            self.ram_samples.append(psutil.virtual_memory().percent)
            gpu = _gpu_snapshot()
            if gpu:
                self.gpu_util_samples.append(gpu["gpu_util_pct"])
                self.gpu_mem_samples.append(gpu["gpu_mem_used_mb"])
            await asyncio.sleep(0.5)

    def start(self):
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._stop = True
        if self._task:
            await self._task

    def summary(self):
        def _stats(samples):
            samples = [s for s in samples if s is not None]
            if not samples:
                return None, None
            return round(sum(samples) / len(samples), 1), max(samples)

        cpu_avg, cpu_peak = _stats(self.cpu_samples)
        ram_avg, ram_peak = _stats(self.ram_samples)
        gpu_util_avg, gpu_util_peak = _stats(self.gpu_util_samples)
        gpu_mem_avg, gpu_mem_peak = _stats(self.gpu_mem_samples)
        return {
            "cpu_avg_pct": cpu_avg,
            "cpu_peak_pct": cpu_peak,
            "ram_avg_pct": ram_avg,
            "ram_peak_pct": ram_peak,
            "gpu_util_avg_pct": gpu_util_avg,
            "gpu_util_peak_pct": gpu_util_peak,
            "gpu_mem_avg_mb": gpu_mem_avg,
            "gpu_mem_peak_mb": gpu_mem_peak,
        }


async def run_test(client: AsyncClient, model: str, test: dict) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": test["prompt"]},
    ]
    tools = test.get("tools")

    sampler = SystemSampler()
    sampler.start()

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
            await sampler.stop()

            ttft = round((first_token_at - start) * 1000) if first_token_at else None
            total_ms = round((end - start) * 1000)
            eval_tokens = chunk.eval_count or 0
            eval_ns = chunk.eval_duration or 0
            tps = round(eval_tokens / (eval_ns / 1e9), 1) if eval_ns else None

            prompt_tokens = chunk.prompt_eval_count or 0
            prompt_ms = round((chunk.prompt_eval_duration or 0) / 1e6)
            load_ms = round((chunk.load_duration or 0) / 1e6)

            return {
                "test_id": test["id"],
                "label": test["label"],
                "prompt": test["prompt"],
                "response": content.strip(),
                "tool_calls": tool_calls_made,
                "ttft_ms": ttft,
                "total_ms": total_ms,
                "load_ms": load_ms,
                "prompt_tokens": prompt_tokens,
                "prompt_ms": prompt_ms,
                "eval_tokens": eval_tokens,
                "tokens_per_sec": tps,
                **sampler.summary(),
            }


async def unload_all_models(client: AsyncClient):
    try:
        running = await client.ps()
        for m in running.models:
            print(f"  Entlade {m.model} aus Speicher...", end=" ", flush=True)
            await client.generate(model=m.model, keep_alive=0)
            print("OK")
    except Exception as e:
        print(f"  Warnung beim Entladen: {e}")


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
            gpu_info = ""
            if result.get("gpu_util_avg_pct") is not None:
                gpu_info = f" | GPU: {result['gpu_util_avg_pct']}% avg / {result['gpu_mem_peak_mb']}MB peak"
            print(
                f"TTFT: {result['ttft_ms']}ms | Total: {result['total_ms']}ms "
                f"| {result['tokens_per_sec']} tok/s "
                f"| CPU: {result['cpu_avg_pct']}% avg{gpu_info}"
            )
            if result["tool_calls"]:
                print(f"         Tool aufgerufen: {result['tool_calls']}")
        except Exception as e:
            print(f"FEHLER: {e}")
            results.append({"test_id": test["id"], "label": test["label"], "error": str(e)})
    return {"model": model, "results": results}


def render_markdown(all_results: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    has_gpu = NVML_AVAILABLE

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

        header = "| Test | TTFT (ms) | Gesamt (ms) | Load (ms) | Prompt-Tokens | Prompt (ms) | Tokens | tok/s | CPU Ø% | CPU Peak% | RAM Ø% | RAM Peak%"
        sep =    "|---|---|---|---|---|---|---|---|---|---|---|---"
        if has_gpu:
            header += " | GPU Ø% | GPU Peak% | VRAM Peak (MB)"
            sep    += "|---|---|---"
        header += " | Tool aufgerufen |"
        sep    += "|---|"

        lines.append(header)
        lines.append(sep)

        for r in entry["results"]:
            if "error" in r:
                cols = "– | " * (14 if has_gpu else 11)
                lines.append(f"| {r['label']} | {cols}Fehler: {r['error']} |")
            else:
                tools_str = ", ".join(tc["name"] for tc in r.get("tool_calls", [])) or "–"
                row = (
                    f"| {r['label']} "
                    f"| {r.get('ttft_ms', '–')} "
                    f"| {r.get('total_ms', '–')} "
                    f"| {r.get('load_ms', '–')} "
                    f"| {r.get('prompt_tokens', '–')} "
                    f"| {r.get('prompt_ms', '–')} "
                    f"| {r.get('eval_tokens', '–')} "
                    f"| {r.get('tokens_per_sec', '–')} "
                    f"| {r.get('cpu_avg_pct', '–')} "
                    f"| {r.get('cpu_peak_pct', '–')} "
                    f"| {r.get('ram_avg_pct', '–')} "
                    f"| {r.get('ram_peak_pct', '–')} "
                )
                if has_gpu:
                    row += (
                        f"| {r.get('gpu_util_avg_pct', '–')} "
                        f"| {r.get('gpu_util_peak_pct', '–')} "
                        f"| {r.get('gpu_mem_peak_mb', '–')} "
                    )
                row += f"| {tools_str} |"
                lines.append(row)
        lines.append("")

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
        await unload_all_models(client)
        result = await benchmark_model(client, model)
        all_results.append(result)

    md = render_markdown(all_results)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nErgebnisse gespeichert in {OUTPUT_FILE}")


asyncio.run(main())
