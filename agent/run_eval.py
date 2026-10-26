"""10 soruluk değerlendirme setini ajanla çalıştırır ve agent/EVAL_RAPORU.md üretir.

Beklenen N/güç değerleri oracle/gpower_vectors.csv'deki G*Power 3.1.9.7 değerleridir;
betik her satırı o dosyayla çapraz kontrol eder.

Kullanım:
    python agent/run_eval.py                 (10 soruyu çalıştırır, logları yazar, raporu üretir)
    python agent/run_eval.py --reuse         (var olan logları kullanır, yalnızca raporu üretir)
    python agent/run_eval.py --model claude-opus-5-5 --log-dir agent/logs_opus --report agent/EVAL_RAPORU_opus.md
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent  # noqa: E402

AGENT_DIR = agent.AGENT_DIR
EVAL_SET = AGENT_DIR / "eval_set.csv"
REPORT = AGENT_DIR / "EVAL_RAPORU.md"
GPOWER = agent.ROOT / "oracle" / "gpower_vectors.csv"
PARAM_TOL = 1e-9
DECIMALS = 4  # araç çıktısı 4 ondalık (SPEC §6)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def check_against_gpower(rows):
    """eval_set'teki beklenen değerlerin G*Power vektörleriyle aynı olduğunu doğrular."""
    gp = {r["id"]: r for r in read_csv(GPOWER)}
    for row in rows:
        if not row["gpower_vektor"]:
            continue
        v = gp[row["gpower_vektor"]]
        assert v["mode"] == row["mode"] and float(v["tails"]) == float(row["tails"]), row["id"]
        assert float(v["dz"]) == float(row["dz"]) and float(v["alpha"]) == float(row["alpha"]), row["id"]
        if row["mode"] == "a-priori":
            assert float(v["power"]) == float(row["power"]), row["id"]
            assert int(v["gp_n_total"]) == int(row["beklenen_n_total"]), row["id"]
        else:
            assert float(v["n_input"]) == float(row["n"]), row["id"]
        assert float(v["gp_actual_power"]) == float(row["beklenen_guc"]), row["id"]


def expected_params(row):
    p = {"mode": row["mode"], "tails": float(row["tails"]), "dz": float(row["dz"]),
         "alpha": float(row["alpha"])}
    if row["mode"] == "a-priori":
        p["power"] = float(row["power"])
    else:
        p["n"] = float(row["n"])
    return p


def params_match(expected, given):
    if given.get("mode") != expected["mode"]:
        return False
    for key in ("tails", "dz", "alpha", "power", "n"):
        if key not in expected:
            continue
        try:
            value = float(given.get(key))
        except (TypeError, ValueError):
            return False
        if abs(value - expected[key]) > PARAM_TOL:
            return False
    return True


def number_in_answer(row, answer):
    """Araç sonucundaki ana sayı (N ya da güç) son cevapta geçiyor mu? (yardımcı ölçüt)"""
    text = answer or ""
    if row["mode"] == "a-priori":
        n = int(row["beklenen_n_total"])
        s = str(n)
        if len(s) > 3:
            s = s[:-3] + r"[.,\s]?" + s[-3:]
        return re.search(rf"(?<![\d.,]){s}(?![\d])", text) is not None
    power = round(float(row["beklenen_guc"]), DECIMALS)
    p4 = f"{power:.4f}"
    pct2 = f"{power * 100:.2f}"
    pct1 = f"{power * 100:.1f}"
    pct0 = f"{power * 100:.0f}"
    forms = {p4, p4.replace(".", ","), pct2, pct2.replace(".", ","), pct1, pct1.replace(".", ",")}
    return any(f in text for f in forms) or re.search(rf"%\s?{pct0}(?![\d.,])|{pct0}\s?%", text) is not None


def evaluate(row, log):
    calls = [c for c in log["tool_calls"] if c["name"] == agent.TOOL_ID]
    block = log.get("final_block") or {}
    label = block.get("etiket")
    accepted = row["kabul_edilen_etiketler"].split("|")
    res = {"id": row["id"], "label": label, "label_ok": label in accepted,
           "n_calls": len(calls), "params_ok": None, "value_ok": None, "number_in_answer": None}
    if row["beklenen_karar"] == "hesapla":
        res["decision_ok"] = len(calls) >= 1
        last = calls[-1] if calls else None
        res["params"] = last["input"] if last else None
        res["params_ok"] = bool(last) and params_match(expected_params(row), last["input"])
        out = (last or {}).get("result_json") or {}
        res["tool_out"] = out
        exp_power = round(float(row["beklenen_guc"]), DECIMALS)
        exp_n = int(row["beklenen_n_total"])
        res["value_ok"] = out.get("n_total") == exp_n and out.get("actual_power") == exp_power
        res["number_in_answer"] = number_in_answer(row, log["final_answer"])
    else:
        res["decision_ok"] = len(calls) == 0
    usage = log.get("usage") or {}
    res["tokens"] = {
        "input": usage.get("input_tokens", 0),
        "cache_creation": usage.get("cache_creation_input_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "output": usage.get("output_tokens", 0),
    }
    res["tokens"]["total"] = sum(res["tokens"].values())
    res["cost"] = log.get("total_cost_usd")
    res["wall_s"] = log.get("wall_seconds_measured")
    res["duration_ms"] = log.get("duration_ms")
    res["turns"] = log.get("num_turns")
    res["model"] = log.get("model")
    return res


def _mark(value):
    return "—" if value is None else ("✅" if value else "❌")


def _ratio(results, key):
    vals = [r[key] for r in results if r[key] is not None]
    return f"{sum(vals)}/{len(vals)}"


def write_report(rows, results, report=REPORT, log_dir=agent.LOG_DIR):
    models = sorted({r["model"] for r in results})
    tot = {k: sum(r["tokens"][k] for r in results) for k in ("input", "cache_creation", "cache_read", "output", "total")}
    cost = sum(r["cost"] or 0 for r in results)
    wall = sum(r["wall_s"] or 0 for r in results)
    lines = [
        "# Ajan değerlendirme raporu (MCP yolu)",
        "",
        f"Üretim: `python agent/run_eval.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')} · model: {', '.join(models)}",
        "",
        "Soru seti: `agent/eval_set.csv` (10 kurgusal Türkçe klinik soru). Beklenen N/güç değerleri",
        "`oracle/gpower_vectors.csv`'deki G*Power 3.1.9.7 değerleridir (betik her satırı o dosyayla çapraz kontrol eder).",
        f"Her sorunun tam akışı: `{Path(log_dir).relative_to(agent.ROOT).as_posix()}/<id>.json`. Token, maliyet ve süre `claude -p --output-format stream-json`",
        "çıktısının `result` olayından alınmıştır (ölçülmüş; tahmin değil). Duvar saati süresi betik tarafından ölçüldü.",
        "",
        "## Özet",
        "",
        "| Ölçüt | Sonuç |",
        "|---|---|",
        f"| Etiket doğruluğu (doğru test ailesi seçimi) | **{_ratio(results, 'label_ok')}** |",
        f"| Karar doğruluğu (t-paired → aracı çağır; diğerleri → çağırma) | **{_ratio(results, 'decision_ok')}** |",
        f"| Parametre doğruluğu (mod, kuyruk, dz, α, güç/N; yalnızca t-paired) | **{_ratio(results, 'params_ok')}** |",
        f"| N/güç doğruluğu (araç sonucu = G*Power, 4 ondalık; yalnızca t-paired) | **{_ratio(results, 'value_ok')}** |",
        f"| Araç sonucundaki sayı son cevapta geçiyor (yardımcı ölçüt) | {_ratio(results, 'number_in_answer')} |",
        f"| Toplam token (input + cache yazma + cache okuma + output) | {tot['total']:,} |",
        f"| Toplam maliyet (Claude Code'un bildirdiği, liste fiyatı) | ${cost:.4f} |",
        f"| Toplam duvar saati süresi | {wall:.1f} sn |",
        "",
        "Doğruluk kuralları:",
        "- **Etiket:** ajanın son cevabındaki JSON bloğundaki `etiket`, `kabul_edilen_etiketler` sütunundakilerden biri olmalı.",
        "  Başka aileden sorularda (Q08, Q09) hem ailenin kendi etiketi hem `unsupported` kabul edilir; iki durumda da",
        "  bu repo hesap yapmaz.",
        "- **Parametre:** son araç çağrısının argümanları beklenenlerle aynı olmalı (sayılar 1e-9 toleransla).",
        "- **N/güç:** araç sonucunun `n_total` ve `actual_power` değeri G*Power değerine (4 ondalığa yuvarlanmış) tam eşit olmalı.",
        "",
        "## Soru başına",
        "",
        "| id | beklenen etiket | ajan etiketi | etiket | karar | araç çağrısı | parametre | N/güç | beklenen (G*Power) | araç sonucu | token | maliyet ($) | süre (sn) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    by_id = {r["id"]: r for r in rows}
    for r in results:
        row = by_id[r["id"]]
        if row["beklenen_karar"] == "hesapla":
            exp = f"N={row['beklenen_n_total']}, güç={round(float(row['beklenen_guc']), DECIMALS)} ({row['gpower_vektor']})"
            out = r.get("tool_out") or {}
            got = f"N={out.get('n_total')}, güç={out.get('actual_power')}"
        else:
            exp = row["beklenen_karar"]
            got = "araç çağrılmadı" if r["n_calls"] == 0 else f"{r['n_calls']} çağrı"
        lines.append(
            f"| {r['id']} | {row['beklenen_etiket']} | {r['label']} | {_mark(r['label_ok'])} | {_mark(r['decision_ok'])} | "
            f"{r['n_calls']} | {_mark(r['params_ok'])} | {_mark(r['value_ok'])} | {exp} | {got} | "
            f"{r['tokens']['total']:,} | {(r['cost'] or 0):.5f} | {r['wall_s']:.1f} |"
        )
    lines += [
        "",
        "## Token dökümü (soru başına)",
        "",
        "| id | input | cache yazma | cache okuma | output | toplam | tur sayısı | API süresi dahil toplam (ms) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        t = r["tokens"]
        lines.append(f"| {r['id']} | {t['input']} | {t['cache_creation']:,} | {t['cache_read']:,} | {t['output']:,} | "
                     f"{t['total']:,} | {r['turns']} | {r['duration_ms']} |")
    lines.append(f"| **toplam** | {tot['input']} | {tot['cache_creation']:,} | {tot['cache_read']:,} | {tot['output']:,} | "
                 f"**{tot['total']:,}** | | |")
    lines += [
        "",
        "## Araç çağrıları",
        "",
        "| id | argümanlar | sonuç |",
        "|---|---|---|",
    ]
    for r in results:
        if r["n_calls"]:
            lines.append(f"| {r['id']} | `{json.dumps(r.get('params'), ensure_ascii=False)}` | "
                         f"`{json.dumps(r.get('tool_out'), ensure_ascii=False)}` |")
        else:
            lines.append(f"| {r['id']} | araç çağrılmadı | — |")
    Path(report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    (Path(log_dir) / "eval_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse", action="store_true", help="var olan logları kullan")
    parser.add_argument("--model", default=agent.DEFAULT_MODEL)
    parser.add_argument("--only", nargs="*", help="yalnızca bu id'leri yeniden çalıştır")
    parser.add_argument("--log-dir", default=str(agent.LOG_DIR), help="log klasörü (ör. agent/logs_opus)")
    parser.add_argument("--report", default=str(REPORT), help="rapor dosyası")
    args = parser.parse_args(argv)
    log_dir = Path(args.log_dir).resolve()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = read_csv(EVAL_SET)
    check_against_gpower(rows)
    results = []
    for row in rows:
        path = log_dir / f"{row['id']}.json"
        rerun = not args.reuse and (not args.only or row["id"] in args.only)
        if rerun or not path.exists():
            print(f"{row['id']} çalışıyor...", flush=True)
            log = agent.ask(row["soru"], row["id"], args.model, log_dir)
        else:
            log = json.loads(path.read_text(encoding="utf-8"))
        r = evaluate(row, log)
        print(f"  {r['id']}: etiket={r['label']} {_mark(r['label_ok'])} karar={_mark(r['decision_ok'])} "
              f"param={_mark(r['params_ok'])} N/güç={_mark(r['value_ok'])} token={r['tokens']['total']} "
              f"süre={r['wall_s']}s", flush=True)
        results.append(r)
    report = Path(args.report).resolve()
    write_report(rows, results, report, log_dir)
    print(f"Rapor: {report.relative_to(agent.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
