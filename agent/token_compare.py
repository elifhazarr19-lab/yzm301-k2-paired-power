"""MCP yolu ile GUI yolunu AYNI birimlerle karşılaştırır ve agent/TOKEN_KARSILASTIRMA.md üretir.

Kaynaklar (hepsi ölçüm):
- MCP: agent/logs_opus/Qxx.json (claude-opus-5-5, ana karşılaştırma) ve agent/logs/Qxx.json (claude-haiku-5-5, ek).
  Her logdaki `usage.iterations` son model çağrısının token kullanımını verir.
- Sabit önek: agent/logs_calibration/prefix_<model>.json — aynı bayraklarla, soru olarak yalnızca "." gönderilen çağrı.
- GUI: agent/gui_measurements.csv — her sorudan önce/sonra okunan oturum bağlamı (`get_usage` → tokensUsed),
  zaman damgaları, araç turu sayısı; agent/gui_screenshots/.
- Ölçüm yükü: bir ölçüm adımının (get_usage + date) bağlama eklediği token, ardışık iki ölçümün farkı
  (MEASUREMENT_OVERHEAD; aşağıda).

Kullanım:
    python agent/token_compare.py
"""

import csv
import json
from datetime import datetime
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
OUT = AGENT_DIR / "TOKEN_KARSILASTIRMA.md"
EVAL_SET = AGENT_DIR / "eval_set.csv"
GUI_CSV = AGENT_DIR / "gui_measurements.csv"
RUNS = {
    "opus": {"model": "claude-opus-5-5", "logs": AGENT_DIR / "logs_opus"},
    "haiku": {"model": "claude-haiku-5-5", "logs": AGENT_DIR / "logs"},
}
CALIBRATION = AGENT_DIR / "logs_calibration"
# Ardışık iki ölçüm adımı (get_usage + date, aradaki metin yok) arasındaki bağlam farkı: 236,387 → 237,122.
MEASUREMENT_OVERHEAD = 735
MEASUREMENT_OVERHEAD_SOURCE = "ardışık iki ölçüm: 236,387 → 237,122 token (2026-10-26 12:10:34Z → 12:10:38Z)"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def call_input(it):
    return it.get("input_tokens", 0) + it.get("cache_creation_input_tokens", 0) + it.get("cache_read_input_tokens", 0)


def prefix(name):
    """Sabit önek P: kalibrasyon çağrısının (soru ".") ilk ve tek model çağrısının toplam girdisi."""
    log = load(CALIBRATION / f"prefix_{name}.json")
    its = log["usage"]["iterations"]
    assert log["num_turns"] == 1 and len(its) == 1
    return call_input(its[0])


def mcp_rows(name):
    p = prefix(name)
    summary = {r["id"]: r for r in load(RUNS[name]["logs"] / "eval_summary.json")}
    rows = {}
    for qid, s in summary.items():
        log = load(RUNS[name]["logs"] / f"{qid}.json")
        last = log["usage"]["iterations"][-1]
        final_ctx = call_input(last) + last.get("output_tokens", 0)
        u = log["usage"]
        rows[qid] = {
            "added": final_ctx - p,
            "final_ctx": final_ctx,
            "turns": log["num_turns"],
            "billed": sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                 "cache_read_input_tokens", "output_tokens")),
            "cost": log.get("total_cost_usd") or 0.0,
            "wall": log["wall_seconds_measured"],
            "duration_ms": log["duration_ms"],
            "ok": s["decision_ok"] and s["label_ok"] and s["params_ok"] is not False and s["value_ok"] is not False,
            "label_ok": s["label_ok"], "decision_ok": s["decision_ok"],
            "params_ok": s["params_ok"], "value_ok": s["value_ok"],
        }
    return p, rows


def secs(a, b):
    fmt = "%H:%M:%S"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).seconds


def gui_rows():
    rows = {}
    for r in read_csv(GUI_CSV):
        if not r["baglam_once"]:
            rows[r["id"]] = None
            continue
        before, after = int(r["baglam_once"]), int(r["baglam_sonra"])
        gui_turns, meas_turns = int(r["gui_arac_turu"]), int(r["olcum_turu"])
        rows[r["id"]] = {
            "added_raw": after - before,
            "added": after - before - MEASUREMENT_OVERHEAD * meas_turns,
            "gui_turns": gui_turns,
            "turns": gui_turns + meas_turns,
            "wall": secs(r["saat_bas_utc"], r["saat_bit_utc"]),
            "ok": r["dogru"] == "1",
            "result": r["gui_sonucu"],
            # Hesaplanan sınırlar (ölçüm değil): her model çağrısı o anki bağlamın tamamını girdi olarak okur.
            "billed_lo": (gui_turns + meas_turns) * before,
            "billed_hi": (gui_turns + meas_turns) * after,
        }
    return rows


def fmt(n):
    return f"{n:,}"


def mark(v):
    return "—" if v is None else ("✅" if v else "❌")


def build():
    ids = [r["id"] for r in read_csv(EVAL_SET)]
    p_opus, opus = mcp_rows("opus")
    p_haiku, haiku = mcp_rows("haiku")
    gui = gui_rows()
    common = [q for q in ids if gui[q] is not None]          # GUI'nin uygulanabildiği sorular (Q01–Q09)
    no_setup = [q for q in common if q != "Q01"]             # kurulum hariç (Q02–Q09)

    def tot(rows, key, qs):
        return sum(rows[q][key] for q in qs)

    o_add, g_add, g_raw = tot(opus, "added", common), tot(gui, "added", common), tot(gui, "added_raw", common)
    o_add2, g_add2 = tot(opus, "added", no_setup), tot(gui, "added", no_setup)
    o_turns, g_turns = tot(opus, "turns", common), tot(gui, "turns", common)
    o_wall, g_wall = tot(opus, "wall", common), tot(gui, "wall", common)
    o_ok = sum(opus[q]["ok"] for q in ids)
    g_ok = sum(gui[q]["ok"] for q in common)
    ratio = g_add / o_add
    ratio2 = g_add2 / o_add2
    overhead = sum(opus[q]["wall"] - opus[q]["duration_ms"] / 1000 for q in ids) / len(ids)

    L = []
    a = L.append
    a("# Token karşılaştırması — MCP yolu ve GUI yolu (ekran görüntüsüyle)")
    a("")
    a(f"Üretim: `python agent/token_compare.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')}. Bu dosyadaki her sayı aşağıda adı geçen "
      "log, CSV ya da ölçümden gelir.")
    a("")
    a("## Özet (aynı model, aynı birim)")
    a("")
    a(f"Aynı model (**claude-opus-5-5**) ve aynı birimle (**bağlama eklenen token**), GUI'nin uygulanabildiği 9 soruda (Q01–Q09): "
      f"MCP yolu **{fmt(o_add)}**, GUI yolu **{fmt(g_add)}** token ekledi (ölçüm yükü çıkarılmış; ham {fmt(g_raw)}). "
      f"GUI yolu **{ratio:.1f} kat** daha fazla bağlam tüketti; Q01'deki tek seferlik kurulum hariç (Q02–Q09) oran **{ratio2:.1f} kat** "
      f"({fmt(o_add2)} / {fmt(g_add2)}). Model çağrısı: MCP {o_turns}, GUI {g_turns}. Süre: MCP {o_wall:.0f} sn, GUI {g_wall} sn. "
      f"Doğruluk: MCP {o_ok}/10, GUI {g_ok}/9. GUI yolu soruyu anlama adımını **içermiyor** (parametreler hazır verildi); "
      "yani GUI değerleri bir alt sınırdır.")
    a("")
    a("Faturalanan token yalnızca MCP yolunda ölçüldü. GUI yolu için faturalanan token **ölçülmedi**; aşağıda ölçülen bağlam "
      "boyutlarından hesaplanmış bir aralık var (ölçüm değildir).")
    a("")
    a("## Düzen")
    a("")
    a("| | MCP yolu | GUI yolu |")
    a("|---|---|---|")
    a("| Kim çözdü | `agent/agent.py` → `claude -p` (Claude Code 2.1.309); ana karşılaştırma **claude-opus-5-5** "
      "(`agent/logs_opus/`), ek olarak claude-haiku-5-5 (`agent/logs/`); yalnızca `t_paired_power` MCP aracı | "
      "Claude Code masaüstü oturumu (Oturum 3), **claude-opus-5-5**, bilgisayar kullanımı aracıyla G*Power 3.1.9.7 penceresi; "
      "öğrencinin erişim onayıyla |")
    a("| Girdi | Hekimin Türkçe sorusu (ham metin) | Sorudan önceden çıkarılmış parametreler (`eval_set.csv`). "
      "**Soruyu anlama adımı GUI ölçümüne dahil değil** |")
    a("| Kanıt | `agent/logs_opus/Qxx.json`, `agent/EVAL_RAPORU_opus.md` (haiku: `agent/logs/`, `agent/EVAL_RAPORU.md`) | "
      "`agent/gui_measurements.csv`, `agent/gui_screenshots/Q01–Q09.jpg` |")
    a("")
    a("## Ana tablo — aynı birim, aynı model (claude-opus-5-5)")
    a("")
    a("| id | MCP bağlama eklenen | GUI bağlama eklenen (ölçüm yükü çıkarılmış) | GUI ham artış | MCP model çağrısı | "
      "GUI model çağrısı (GUI + ölçüm) | MCP süre (sn) | GUI süre (sn) | MCP doğru | GUI doğru |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for q in ids:
        o, g = opus[q], gui[q]
        if g is None:
            a(f"| {q} | {fmt(o['added'])} | uygulanamaz | — | {o['turns']} | 0 | {o['wall']:.1f} | — | {mark(o['ok'])} | uygulanamaz |")
        else:
            a(f"| {q} | {fmt(o['added'])} | {fmt(g['added'])} | {fmt(g['added_raw'])} | {o['turns']} | "
              f"{g['turns']} ({g['gui_turns']} + {g['turns'] - g['gui_turns']}) | {o['wall']:.1f} | {g['wall']} | "
              f"{mark(o['ok'])} | {mark(g['ok'])} |")
    a(f"| **Q01–Q09 toplam** | **{fmt(o_add)}** | **{fmt(g_add)}** | {fmt(g_raw)} | **{o_turns}** | **{g_turns}** | "
      f"**{o_wall:.1f}** | **{g_wall}** | {sum(opus[q]['ok'] for q in common)}/9 | {g_ok}/9 |")
    a(f"| Q02–Q09 (kurulum hariç) | {fmt(o_add2)} | {fmt(g_add2)} | {fmt(tot(gui, 'added_raw', no_setup))} | "
      f"{tot(opus, 'turns', no_setup)} | {tot(gui, 'turns', no_setup)} | {tot(opus, 'wall', no_setup):.1f} | "
      f"{tot(gui, 'wall', no_setup)} | | |")
    a("")
    a("GUI Q01 tek seferlik kurulum içeriyor: bilgisayar kullanımı araç şemalarının yüklenmesi (+2,934 token), pencereyi öne "
      "getirme denemeleri, test türünün seçilmesi ve bir giriş hatasının düzeltilmesi. Q08/Q09'da G*Power'da yalnızca doğru testin "
      "bulunduğu kontrol edildi (G*Power vektörü yok). Q10 (belirsiz) GUI'de uygulanamaz.")
    a("")
    a("### Formüller")
    a("")
    a("- **MCP, bağlama eklenen** = (son model çağrısının girdisi + son çağrının çıktısı) − P.")
    a("  - Son çağrının girdisi = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`, "
      "`usage.iterations[-1]` alanından. Aracı çağıran sorularda bu girdi, sorunun kendisini, ilk çağrının çıktısını "
      "(araç çağrısı) ve araç sonucunu içerir.")
    a(f"  - **P (sabit önek: sistem prompt'u + araç şeması + çağrı çerçevesi)**, aynı bayraklarla yalnızca `\".\"` gönderilen "
      f"kalibrasyon çağrısının girdisidir: opus **{fmt(p_opus)}**, haiku **{fmt(p_haiku)}** token "
      "(`agent/logs_calibration/prefix_*.json`). \".\" ve mesaj çerçevesi birkaç token olduğu için P'ye dahil sayıldı.")
    a("- **GUI, bağlama eklenen** = `tokensUsed(sonra) − tokensUsed(önce)` − ölçüm yükü × ölçüm turu. `tokensUsed` her sorudan "
      "önce ve sonra `get_usage` aracıyla okundu (`agent/gui_measurements.csv`).")
    a(f"  - **Ölçüm yükü = {MEASUREMENT_OVERHEAD} token** / ölçüm adımı ({MEASUREMENT_OVERHEAD_SOURCE}). Her soruda bir ölçüm adımı var. "
      "\"GUI ham artış\" sütunu bu düzeltme yapılmamış değerdir.")
    a("- **Model çağrısı:** MCP için logdaki `num_turns`. GUI için o soruda yapılan araç turu sayısı (her tur bir model çağrısı) "
      "+ 1 ölçüm turu (`get_usage` ve `date` aynı turda paralel çağrıldı).")
    a("- **Süre:** MCP: betiğin ölçtüğü duvar saati (`claude -p` açılışı dahil). GUI: ardışık `date -u` damgaları arası "
      "(ölçüm adımı dahil).")
    a("")
    a("## Ek: aynı soruların claude-haiku-5-5 ile MCP sonuçları")
    a("")
    a("| id | haiku bağlama eklenen | haiku model çağrısı | haiku süre (sn) | haiku doğru | haiku faturalanan token | haiku maliyet ($) |")
    a("|---|---|---|---|---|---|---|")
    for q in ids:
        h = haiku[q]
        a(f"| {q} | {fmt(h['added'])} | {h['turns']} | {h['wall']:.1f} | {mark(h['ok'])} | {fmt(h['billed'])} | {h['cost']:.5f} |")
    a(f"| **toplam** | **{fmt(tot(haiku, 'added', ids))}** | {tot(haiku, 'turns', ids)} | {tot(haiku, 'wall', ids):.1f} | "
      f"{sum(haiku[q]['ok'] for q in ids)}/10 | {fmt(tot(haiku, 'billed', ids))} | {tot(haiku, 'cost', ids):.4f} |")
    a("")
    a("## Faturalanan token")
    a("")
    a("**MCP (ölçüldü):** her logdaki `usage` toplamı (input + cache yazma + cache okuma + output) ve `total_cost_usd`.")
    a("")
    a("| | Q01–Q09 faturalanan token | Q01–Q10 faturalanan token | Q01–Q10 maliyet |")
    a("|---|---|---|---|")
    for name in ("opus", "haiku"):
        rows = opus if name == "opus" else haiku
        a(f"| MCP · {RUNS[name]['model']} | {fmt(tot(rows, 'billed', common))} | {fmt(tot(rows, 'billed', ids))} | "
          f"${tot(rows, 'cost', ids):.4f} |")
    lo, hi = tot(gui, "billed_lo", common), tot(gui, "billed_hi", common)
    a(f"| GUI · claude-opus-5-5 | **ölçülmedi** | uygulanamaz | **ölçülmedi** |")
    a("")
    a("**GUI (hesaplanan aralık — ölçüm değil, ölçülen değerlerden hesaplanan sınır):** her model çağrısı o anki oturum "
      "bağlamının tamamını girdi olarak okur. Sorudaki model çağrısı sayısı t, sorudan önceki bağlam C_önce, sonraki C_sonra ise "
      "girdi token'ı t × C_önce ile t × C_sonra arasındadır.")
    a("")
    a(f"- Q01–Q09: **{fmt(lo)} – {fmt(hi)}** token (çıktı token'ı eklenmedi; büyük kısmı önbellekten okuma olarak faturalanır).")
    a("- Bu aralık bu oturumun büyük taban bağlamına (~167k token: önceki işler, araç şemaları) bağlıdır; boş bir oturumda "
      "başlayan bir GUI ajanı için çok daha küçük olurdu. Bu yüzden MCP'nin ölçülmüş faturalanan token'ıyla doğrudan "
      "karşılaştırılmamalıdır; asıl karşılaştırma yukarıdaki aynı birimli tablodur.")
    a("")
    a("## Doğruluk")
    a("")
    a("| | MCP · opus | MCP · haiku | GUI · opus |")
    a("|---|---|---|---|")
    for key, label in (("label_ok", "Test ailesi etiketi"), ("decision_ok", "Karar (araç çağır / çağırma)")):
        a(f"| {label} | {sum(opus[q][key] for q in ids)}/10 | {sum(haiku[q][key] for q in ids)}/10 | "
          + ("9/9 test seçimi (Q10 uygulanamaz)" if key == "label_ok" else "uygulanamaz") + " |")
    a(f"| Parametreler (t-paired, 7 soru) | {sum(bool(opus[q]['params_ok']) for q in ids)}/7 | "
      f"{sum(bool(haiku[q]['params_ok']) for q in ids)}/7 | hazır verildi |")
    a(f"| N/güç = G*Power (t-paired, 7 soru) | {sum(bool(opus[q]['value_ok']) for q in ids)}/7 | "
      f"{sum(bool(haiku[q]['value_ok']) for q in ids)}/7 | 7/7 (GUI zaten G*Power) |")
    a("")
    a("## Sınırlılıklar")
    a("")
    a("- GUI yolunda soruyu anlama ve parametre çıkarma adımı yok; MCP yolunda var. GUI değerleri bu yüzden alt sınırdır.")
    a("- GUI ekran görüntüleri tam ekran yerine 0.6 ölçekli kırpılmış (zoom) görüntülerdi; tam ekranla bağlam artışı daha büyük olurdu.")
    a("- MCP \"bağlama eklenen\" değeri son çağrının çıktısındaki düşünme (thinking) token'larını da içerir; GUI ölçümü de oturumun "
      "kendi metin ve düşünme token'larını içerir. İkisi de \"o soru için bağlamda harcanan token\"dır.")
    a("- GUI ölçüm yükü tek bir ardışık ölçümle bulundu (735). Soru başına yazılan kısa metinler (~20–40 token) ayıklanmadı.")
    a(f"- MCP süresi her soruda `claude -p` sürecinin açılışını ve kapanışını da içerir: duvar saati − logdaki `duration_ms` "
      f"ortalaması opus için {overhead:.1f} sn/soru. GUI süresi zaten açık bir G*Power penceresiyle ölçüldü.")
    a("")
    a("## Gözlemler")
    a("")
    a("- **GUI yolu hataya açık:** Q01'de alan metni seçilmeden yazıldı (\"0.50.5\", \"0.050.05\", \"0.800.95\"); G*Power yine de sonuç "
      "gösterdi. Hata ancak ekran görüntüsü okununca fark edildi ve `Ctrl+A` ile yeniden yapıldı (Oturum 1'deki V02/V20 insan "
      "hatalarına benzer).")
    a("- **MCP yolu soruyu da anlıyor:** Q01 ve Q07'de dz'yi ortalama fark / farkların SD'sinden kendisi çıkardı; Q08–Q10'da aracı "
      "çağırmadı. GUI yolunda bu karar dışarıda kalıyor.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    return {"opus_added": o_add, "gui_added": g_add, "ratio": ratio, "ratio_no_setup": ratio2,
            "opus_turns": o_turns, "gui_turns": g_turns, "opus_wall": o_wall, "gui_wall": g_wall,
            "opus_ok": o_ok, "gui_ok": g_ok, "billed_lo": lo, "billed_hi": hi,
            "opus_billed": tot(opus, "billed", ids), "opus_cost": tot(opus, "cost", ids),
            "p_opus": p_opus, "p_haiku": p_haiku, "haiku_added": tot(haiku, "added", ids)}


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(build(), ensure_ascii=False, indent=2))
