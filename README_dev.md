# pairedpower — geliştirici notları

Eşleştirilmiş örneklem t testi (t-paired) için güç ve örneklem büyüklüğü hesaplayıcısı.
Davranış kaynağı: `SPEC.md`.

## Kurulum

Python 3.10+ gerekir. Geliştirme için sanal ortamda editable kurulum:

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Çalıştırma

```
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 35
```

Başarıda tek satır JSON ve çıkış kodu 0. Hatada `{"error": "..."}` ve çıkış kodu 2.

## Testler

```
pytest
```

`tests/test_spec.py`, `SPEC.md` §7'deki her Examples satırını ayrı bir test olarak çalıştırır.

## Yapı

- `src/pairedpower/engine.py` — saf hesap motoru (G/Ç yok). Doğrulama, N araması, güç.
  `solve` (mod seçimi + zorunlu alanlar), `to_dict` (çıktı sözlüğü, yuvarlama), `calculate` (girdi → sonuç ya da `{"error"}`):
  CLI ve MCP bu ortak yolu kullanır.
- `src/pairedpower/cli.py` — argüman okuma, eş ad çözümü, JSON çıktısı.
- `src/pairedpower/mcp_server.py` — FastMCP stdio sunucusu; tek araç `t_paired_power` → `engine.calculate`.
- `agent/` — `claude -p` ile çalışan Türkçe ajan ve değerlendirme betikleri.
- `tests/test_mcp_parity.py` — CLI alt süreci ile gerçek MCP protokolü üzerinden aracın aynı JSON'u verdiğini doğrular.
- `tests/test_spec.py` — SPEC §7 senaryoları.

## Sayısal notlar

- Merkezi t için `scipy.stats.t.isf`, noncentral t için `scipy.stats.nct` kullanılır.
- İki kuyruklu gücün alt kuyruk terimi büyük δ'da NaN dönebilir; bu terim 0 kabul edilir (SPEC §5.3).
- A-priori N, `scipy.optimize.brentq` ile kök bulunarak hesaplanır (SPEC §5.2).
- Test edilen sürüm: scipy 1.18.1.
