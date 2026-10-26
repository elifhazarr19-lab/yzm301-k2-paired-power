# Ajan değerlendirme raporu (MCP yolu)

Üretim: `python agent/run_eval.py` · 2026-10-26 15:14 · model: claude-opus-5-5

Soru seti: `agent/eval_set.csv` (10 kurgusal Türkçe klinik soru). Beklenen N/güç değerleri
`oracle/gpower_vectors.csv`'deki G*Power 3.1.9.7 değerleridir (betik her satırı o dosyayla çapraz kontrol eder).
Her sorunun tam akışı: `agent/logs_opus/<id>.json`. Token, maliyet ve süre `claude -p --output-format stream-json`
çıktısının `result` olayından alınmıştır (ölçülmüş; tahmin değil). Duvar saati süresi betik tarafından ölçüldü.

## Özet

| Ölçüt | Sonuç |
|---|---|
| Etiket doğruluğu (doğru test ailesi seçimi) | **10/10** |
| Karar doğruluğu (t-paired → aracı çağır; diğerleri → çağırma) | **10/10** |
| Parametre doğruluğu (mod, kuyruk, dz, α, güç/N; yalnızca t-paired) | **7/7** |
| N/güç doğruluğu (araç sonucu = G*Power, 4 ondalık; yalnızca t-paired) | **7/7** |
| Araç sonucundaki sayı son cevapta geçiyor (yardımcı ölçüt) | 7/7 |
| Toplam token (input + cache yazma + cache okuma + output) | 73,538 |
| Toplam maliyet (Claude Code'un bildirdiği, liste fiyatı) | $0.2700 |
| Toplam duvar saati süresi | 204.9 sn |

Doğruluk kuralları:
- **Etiket:** ajanın son cevabındaki JSON bloğundaki `etiket`, `kabul_edilen_etiketler` sütunundakilerden biri olmalı.
  Başka aileden sorularda (Q08, Q09) hem ailenin kendi etiketi hem `unsupported` kabul edilir; iki durumda da
  bu repo hesap yapmaz.
- **Parametre:** son araç çağrısının argümanları beklenenlerle aynı olmalı (sayılar 1e-9 toleransla).
- **N/güç:** araç sonucunun `n_total` ve `actual_power` değeri G*Power değerine (4 ondalığa yuvarlanmış) tam eşit olmalı.

## Soru başına

| id | beklenen etiket | ajan etiketi | etiket | karar | araç çağrısı | parametre | N/güç | beklenen (G*Power) | araç sonucu | token | maliyet ($) | süre (sn) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q01 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=34, güç=0.8078 (V01) | N=34, güç=0.8078 | 8,849 | 0.03229 | 20.1 |
| Q02 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=27, güç=0.8118 (V03) | N=27, güç=0.8118 | 8,815 | 0.03209 | 20.4 |
| Q03 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=51, güç=0.8094 (V10) | N=51, güç=0.8094 | 8,601 | 0.02857 | 20.1 |
| Q04 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=35, güç=0.8195 (V27) | N=35, güç=0.8195 | 8,459 | 0.02671 | 18.3 |
| Q05 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=35, güç=0.895 (V28) | N=35, güç=0.895 | 8,459 | 0.02688 | 20.2 |
| Q06 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=78491, güç=0.8 (V14) | N=78491, güç=0.8 | 8,763 | 0.03206 | 23.3 |
| Q07 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=13, güç=0.9107 (V08) | N=13, güç=0.9107 | 8,671 | 0.02965 | 20.4 |
| Q08 | t2-indep | t2-indep | ✅ | ✅ | 0 | — | — | desteklenmiyor | araç çağrılmadı | 4,355 | 0.02103 | 19.7 |
| Q09 | chi2-contingency | chi2-contingency | ✅ | ✅ | 0 | — | — | desteklenmiyor | araç çağrılmadı | 4,225 | 0.01880 | 24.8 |
| Q10 | ambiguous | ambiguous | ✅ | ✅ | 0 | — | — | soru-sor | araç çağrılmadı | 4,341 | 0.02188 | 17.6 |

## Token dökümü (soru başına)

| id | input | cache yazma | cache okuma | output | toplam | tur sayısı | API süresi dahil toplam (ms) |
|---|---|---|---|---|---|---|---|
| Q01 | 4 | 1,385 | 6,465 | 995 | 8,849 | 2 | 13835 |
| Q02 | 4 | 1,370 | 6,450 | 991 | 8,815 | 2 | 13855 |
| Q03 | 4 | 1,346 | 6,426 | 825 | 8,601 | 2 | 13436 |
| Q04 | 4 | 1,314 | 6,396 | 745 | 8,459 | 2 | 11947 |
| Q05 | 4 | 1,308 | 6,391 | 756 | 8,459 | 2 | 13641 |
| Q06 | 4 | 1,338 | 6,418 | 1,003 | 8,763 | 2 | 16015 |
| Q07 | 4 | 1,363 | 6,432 | 872 | 8,671 | 2 | 13030 |
| Q08 | 2 | 1,109 | 2,663 | 581 | 4,355 | 1 | 12027 |
| Q09 | 2 | 1,078 | 2,663 | 482 | 4,225 | 1 | 17525 |
| Q10 | 2 | 1,015 | 2,663 | 661 | 4,341 | 1 | 10297 |
| **toplam** | 34 | 12,626 | 52,967 | 7,911 | **73,538** | | |

## Araç çağrıları

| id | argümanlar | sonuç |
|---|---|---|
| Q01 | `{"mode": "a-priori", "tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.8}` | `{"n_total": 34, "actual_power": 0.8078, "critical": 2.0345, "df": 33, "ncp": 2.9155}` |
| Q02 | `{"mode": "a-priori", "tails": 1, "dz": 0.5, "alpha": 0.05, "power": 0.8}` | `{"n_total": 27, "actual_power": 0.8118, "critical": 1.7056, "df": 26, "ncp": 2.5981}` |
| Q03 | `{"mode": "a-priori", "tails": 2, "dz": 0.5, "alpha": 0.01, "power": 0.8}` | `{"n_total": 51, "actual_power": 0.8094, "critical": 2.6778, "df": 50, "ncp": 3.5707}` |
| Q04 | `{"mode": "post-hoc", "tails": 2, "dz": 0.5, "alpha": 0.05, "n": 35}` | `{"n_total": 35, "actual_power": 0.8195, "critical": 2.0322, "df": 34, "ncp": 2.958}` |
| Q05 | `{"mode": "post-hoc", "tails": 1, "dz": 0.5, "alpha": 0.05, "n": 35}` | `{"n_total": 35, "actual_power": 0.895, "critical": 1.6909, "df": 34, "ncp": 2.958}` |
| Q06 | `{"mode": "a-priori", "tails": 2, "dz": 0.01, "alpha": 0.05, "power": 0.8}` | `{"n_total": 78491, "actual_power": 0.8, "critical": 1.96, "df": 78490, "ncp": 2.8016}` |
| Q07 | `{"mode": "a-priori", "tails": 2, "dz": 1, "alpha": 0.05, "power": 0.9}` | `{"n_total": 13, "actual_power": 0.9107, "critical": 2.1788, "df": 12, "ncp": 3.6056}` |
| Q08 | araç çağrılmadı | — |
| Q09 | araç çağrılmadı | — |
| Q10 | araç çağrılmadı | — |
