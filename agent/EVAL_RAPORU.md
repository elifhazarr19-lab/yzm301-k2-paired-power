# Ajan değerlendirme raporu (MCP yolu)

Üretim: `python agent/run_eval.py` · 2026-10-26 15:10 · model: claude-haiku-5-5

Soru seti: `agent/eval_set.csv` (10 kurgusal Türkçe klinik soru). Beklenen N/güç değerleri
`oracle/gpower_vectors.csv`'deki G*Power 3.1.9.7 değerleridir (betik her satırı o dosyayla çapraz kontrol eder).
Her sorunun tam akışı: `agent/logs/<id>.json`. Token, maliyet ve süre `claude -p --output-format stream-json`
çıktısının `result` olayından alınmıştır (ölçülmüş; tahmin değil). Duvar saati süresi betik tarafından ölçüldü.

## Özet

| Ölçüt | Sonuç |
|---|---|
| Etiket doğruluğu (doğru test ailesi seçimi) | **10/10** |
| Karar doğruluğu (t-paired → aracı çağır; diğerleri → çağırma) | **10/10** |
| Parametre doğruluğu (mod, kuyruk, dz, α, güç/N; yalnızca t-paired) | **7/7** |
| N/güç doğruluğu (araç sonucu = G*Power, 4 ondalık; yalnızca t-paired) | **7/7** |
| Araç sonucundaki sayı son cevapta geçiyor (yardımcı ölçüt) | 7/7 |
| Toplam token (input + cache yazma + cache okuma + output) | 73,201 |
| Toplam maliyet (Claude Code'un bildirdiği, liste fiyatı) | $0.0069 |
| Toplam duvar saati süresi | 174.6 sn |

Doğruluk kuralları:
- **Etiket:** ajanın son cevabındaki JSON bloğundaki `etiket`, `kabul_edilen_etiketler` sütunundakilerden biri olmalı.
  Başka aileden sorularda (Q08, Q09) hem ailenin kendi etiketi hem `unsupported` kabul edilir; iki durumda da
  bu repo hesap yapmaz.
- **Parametre:** son araç çağrısının argümanları beklenenlerle aynı olmalı (sayılar 1e-9 toleransla).
- **N/güç:** araç sonucunun `n_total` ve `actual_power` değeri G*Power değerine (4 ondalığa yuvarlanmış) tam eşit olmalı.

## Soru başına

| id | beklenen etiket | ajan etiketi | etiket | karar | araç çağrısı | parametre | N/güç | beklenen (G*Power) | araç sonucu | token | maliyet ($) | süre (sn) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q01 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=34, güç=0.8078 (V01) | N=34, güç=0.8078 | 8,608 | 0.00073 | 19.1 |
| Q02 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=27, güç=0.8118 (V03) | N=27, güç=0.8118 | 8,454 | 0.00067 | 13.2 |
| Q03 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=51, güç=0.8094 (V10) | N=51, güç=0.8094 | 8,634 | 0.00076 | 16.8 |
| Q04 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=35, güç=0.8195 (V27) | N=35, güç=0.8195 | 8,397 | 0.00067 | 17.9 |
| Q05 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=35, güç=0.895 (V28) | N=35, güç=0.895 | 8,358 | 0.00065 | 17.2 |
| Q06 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=78491, güç=0.8 (V14) | N=78491, güç=0.8 | 8,712 | 0.00081 | 20.8 |
| Q07 | t-paired | t-paired | ✅ | ✅ | 1 | ✅ | ✅ | N=13, güç=0.9107 (V08) | N=13, güç=0.9107 | 8,540 | 0.00071 | 17.9 |
| Q08 | t2-indep | t2-indep | ✅ | ✅ | 0 | — | — | desteklenmiyor | araç çağrılmadı | 4,313 | 0.00053 | 16.5 |
| Q09 | chi2-contingency | chi2-contingency | ✅ | ✅ | 0 | — | — | desteklenmiyor | araç çağrılmadı | 4,323 | 0.00054 | 17.4 |
| Q10 | ambiguous | ambiguous | ✅ | ✅ | 0 | — | — | soru-sor | araç çağrılmadı | 4,862 | 0.00083 | 17.7 |

## Token dökümü (soru başına)

| id | input | cache yazma | cache okuma | output | toplam | tur sayısı | API süresi dahil toplam (ms) |
|---|---|---|---|---|---|---|---|
| Q01 | 4 | 1,426 | 6,423 | 755 | 8,608 | 2 | 12373 |
| Q02 | 4 | 1,380 | 6,411 | 659 | 8,454 | 2 | 6802 |
| Q03 | 4 | 1,411 | 6,391 | 828 | 8,634 | 2 | 10056 |
| Q04 | 4 | 1,353 | 6,364 | 676 | 8,397 | 2 | 10975 |
| Q05 | 4 | 1,356 | 6,361 | 637 | 8,358 | 2 | 10314 |
| Q06 | 4 | 1,391 | 6,378 | 939 | 8,712 | 2 | 14126 |
| Q07 | 4 | 1,404 | 6,397 | 735 | 8,540 | 2 | 10964 |
| Q08 | 2 | 1,070 | 2,663 | 578 | 4,313 | 1 | 9629 |
| Q09 | 2 | 1,040 | 2,663 | 618 | 4,323 | 1 | 11115 |
| Q10 | 2 | 977 | 2,663 | 1,220 | 4,862 | 1 | 10488 |
| **toplam** | 34 | 12,808 | 52,714 | 7,645 | **73,201** | | |

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
