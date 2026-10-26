"""Türkçe klinik soru → MCP aracı → sade Türkçe cevap.

LLM olarak Claude Code başsız modda (`claude -p`) çalışır. Yalnızca bizim MCP sunucumuz
yüklenir (`--strict-mcp-config`) ve yalnızca `t_paired_power` aracına izin verilir;
yerleşik araçlar kapalıdır (`--tools ""`). Ajan hesap yapmaz: sayılar MCP aracından gelir.

Her soru için tam akış (araç çağrısı argümanları, araç sonucu, son cevap, ölçülmüş token
kullanımı, süre) `agent/logs/<id>.json` dosyasına yazılır. Token ve süre değerleri
`--output-format stream-json` çıktısındaki `result` olayından alınır; tahmin yazılmaz.

Kullanım:
    python agent/agent.py "Soru metni"            (log: agent/logs/adhoc_<zaman>.json)
    python agent/agent.py --id Q01 "Soru metni"
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
ROOT = AGENT_DIR.parent
LOG_DIR = AGENT_DIR / "logs"
SYSTEM_PROMPT = AGENT_DIR / "system_prompt.md"
SERVER_KEY = "pairedpower"
TOOL_ID = f"mcp__{SERVER_KEY}__t_paired_power"
DEFAULT_MODEL = "claude-haiku-5-5"
TIMEOUT_S = 300
FINAL_BLOCK = re.compile(r"\{[^{}]*\"etiket\"[^{}]*\}")


def mcp_config():
    env = {"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    return {"mcpServers": {SERVER_KEY: {
        "type": "stdio", "command": sys.executable,
        "args": ["-m", "pairedpower.mcp_server"], "env": env,
    }}}


def claude_command(question, config_path, model):
    exe = shutil.which("claude")
    if exe is None:
        raise SystemExit("claude komutu bulunamadı (Claude Code kurulu olmalı).")
    return [
        exe, "-p", question,
        "--model", model,
        "--output-format", "stream-json", "--verbose",
        "--system-prompt-file", str(SYSTEM_PROMPT),
        "--mcp-config", str(config_path), "--strict-mcp-config",
        "--tools", "",
        "--allowedTools", TOOL_ID,
        "--setting-sources", "",
        "--no-session-persistence",
        "--disable-slash-commands",
    ]


def parse_stream(lines):
    """stream-json olaylarından araç çağrıları, sonuçları ve son kullanım değerlerini çıkarır."""
    calls, results, texts, final = [], {}, [], None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        event = json.loads(line)
        kind = event.get("type")
        if kind == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append({"id": block["id"], "name": block["name"], "input": block["input"]})
                elif block.get("type") == "text":
                    texts.append(block["text"])
        elif kind == "user":
            content = event.get("message", {}).get("content", [])
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_result":
                    results[block["tool_use_id"]] = {
                        "is_error": block.get("is_error", False),
                        "content": block.get("content"),
                    }
        elif kind == "result":
            final = event
    for call in calls:
        call["result"] = results.get(call["id"])
        call["result_json"] = _result_json(call["result"])
    return calls, texts, final


def _result_json(result):
    if not result or result.get("is_error"):
        return None
    content = result["content"]
    if isinstance(content, list):
        content = "".join(b.get("text", "") for b in content if b.get("type") == "text")
    try:
        return json.loads(content)
    except (TypeError, json.JSONDecodeError):
        return None


def final_block(answer):
    matches = FINAL_BLOCK.findall(answer or "")
    if not matches:
        return None
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


def ask(question, qid=None, model=DEFAULT_MODEL, log_dir=LOG_DIR):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    qid = qid or "adhoc_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    with tempfile.TemporaryDirectory() as work:
        config_path = Path(work) / "mcp.json"
        config_path.write_text(json.dumps(mcp_config()), encoding="utf-8")
        cmd = claude_command(question, config_path, model)
        started = datetime.now(timezone.utc)
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              cwd=work, timeout=TIMEOUT_S)
        wall = time.perf_counter() - t0
    raw = proc.stdout.splitlines()
    calls, texts, final = parse_stream(raw)
    answer = (final or {}).get("result") or (texts[-1] if texts else "")
    log = {
        "id": qid,
        "question": question,
        "model": model,
        "started_utc": started.isoformat(),
        "wall_seconds_measured": round(wall, 3),
        "exit_code": proc.returncode,
        "stderr": proc.stderr,
        "tool_calls": calls,
        "final_answer": answer,
        "final_block": final_block(answer),
        "usage": (final or {}).get("usage"),
        "model_usage": (final or {}).get("modelUsage"),
        "total_cost_usd": (final or {}).get("total_cost_usd"),
        "duration_ms": (final or {}).get("duration_ms"),
        "duration_api_ms": (final or {}).get("duration_api_ms"),
        "num_turns": (final or {}).get("num_turns"),
        "command": [c if c != question else "<soru>" for c in cmd[1:]],
        "raw_stream": [json.loads(x) for x in raw if x.strip()],
    }
    (log_dir / f"{qid}.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return log


def main(argv=None):
    parser = argparse.ArgumentParser(description="Türkçe klinik güç analizi ajanı (MCP)")
    parser.add_argument("question")
    parser.add_argument("--id")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--log-dir", default=str(LOG_DIR))
    args = parser.parse_args(argv)
    log = ask(args.question, args.id, args.model, args.log_dir)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(log["final_answer"])
    print(f"\n[log: {Path(args.log_dir) / (log['id'] + '.json')} · araç çağrısı: {len(log['tool_calls'])}"
          f" · süre: {log['wall_seconds_measured']} sn · maliyet: {log['total_cost_usd']} USD]")
    return 0 if log["exit_code"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
