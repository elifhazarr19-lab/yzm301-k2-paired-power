# Uyum raporu — pairedpower (t-paired)

Bu rapor üç referans kaynağa karşı yapılan testlerin sonuçlarını özetler:
G*Power 3.1.9.7 kara kutu vektörleri, statsmodels kütüphane vektörleri ve SPEC §7 senaryoları.
§5, CLI ile MCP sunucusunun aynı girdide aynı çıktıyı verdiğini gösterir.

## Çalıştırma

```
pytest -q
```

Kütüphane vektörlerini yeniden üretmek için (statsmodels gerekir):

```
python tests/gen_library_vectors.py
```

| Dosya | Test sayısı | Kaynak |
|---|---|---|
| `tests/test_spec.py` | 50 | `SPEC.md` §7 Examples satırları, geçersiz girdi, §3.1 kararları, ek kurallar |
| `tests/test_differential.py` | 38 | `oracle/gpower_vectors.csv` (30 hesaplı + 8 hata) |
| `tests/test_library.py` | 1001 | `oracle/library_vectors.csv` (1000 satır) |
| `tests/test_mcp_parity.py` | 99 | CLI = MCP: 38 G*Power + 60 kütüphane satırı (+1 sayım testi) |
| `tests/test_manual.py` | 2 | `oracle/manual_vectors.csv` — G*Power 3.1 kılavuzu §19.3 (s. 48) matched-pairs örnekleri |
| **Toplam** | **1190** | Hepsi geçiyor |

**Kılavuz örnekleri:** Kılavuz değerleri 6 ondalıkla veriyor; CLI çıktısı 6 ondalığa yuvarlanınca ikisi de birebir aynı.
M01 (post hoc, iki kuyruk, dz=0.421637, α=0.05, N=50): güç 0.832114, kritik t 2.009575, df 49, δ 2.981424 → bizim 0.8321145, 2.0095752, 49, 2.9814238.
M02 (aynı, dz=0.2828427): güç 0.500352 → bizim 0.5003516.

## 0. SPEC v1.1 (§3.1) uyumu

SPEC §3.1'deki yedi karar gözden geçirildi; kod ve testler bunlara göre güncellendi, `SPEC-BELIRSIZ`
işaretleri kaldırıldı.

| § | Karar | Durum |
|---|---|---|
| 1 | Başarı ve hata JSON'u stdout'a; stderr boş | Uyumlu (hata JSON'u stdout; testle doğrulandı: `stderr == ""`) |
| 2 | `inf`, `-inf`, `nan` sayı değil → hata | Uyumlu (CLI'da `isfinite` kontrolü; 6 varyantla test) |
| 3 | `--tails` kontrolü bayrak okumasında, §4'ten önce | **Düzeltildi**: önce tails kontrolü yapılmıyordu (eksik `--power` önce hata veriyordu); artık ilk kontrol |
| 4 | `--n`, `--n-total`, `--n_total` farklı değerle → hata | Uyumlu (testle doğrulandı) |
| 5 | A-priori N > 2147483646 ya da arama NaN → hata | **Düzeltildi**: önceden yalnızca arama sınırı kontrol ediliyordu; artık bulunan N de kontrol ediliyor, arama NaN üretirse hata |
| 6 | Sonsuz/NaN N → hata (metin önemsiz) | Uyumlu |
| 7 | `--dz`/`--d` iki modda zorunlu; moda ait olmayan bayraklar yok sayılır | Uyumlu |

Değişen dosyalar: `src/pairedpower/engine.py` (`check_tails` herkese açık oldu, arama NaN ve N üst sınır
kontrolü), `src/pairedpower/cli.py` (tails önce, `SPEC-BELIRSIZ` işaretleri kaldırıldı),
`tests/test_spec.py` (12 yeni test). G*Power ve statsmodels sonuçları bu değişikliklerden etkilenmedi
(aynı testler hâlâ geçiyor).

## 1. G*Power vektörleri

Kapsam: `status = GUI-TOPLANDI` (30 hesaplı) ve `GUI-TOPLANDI-HATA` (8 hata). `IPTAL` olan
4 satır (V30, V31, V35, V36) kapsam daraltması nedeniyle kullanılmadı.

| Ölçüt | Sonuç |
|---|---|
| N ve df tam eşleşme | **30 / 30** (N ve df tam sayı, her biri eşleşti) |
| 7 basamak eşleşme (actual_power, critical, ncp) | **30 / 30** satır, 90 / 90 değer |
| Hata vektörleri: CLI `error` döndürüyor ve çıkış kodu ≠ 0 | **8 / 8** |

Karşılaştırma: CLI `--precision 7` ile çalıştırıldı (gizli bayrak, varsayılan çıktı 4 ondalık kalıyor);
motorun tam hassasiyetli değeri 7 ondalığa yuvarlanıp G*Power'ın 7 ondalık değeriyle tam eşitlik aranıyor.

**Uyuşmazlık yok.**

**Güncel durum:** Önceki taslakta SPEC içinde eski vektör sayısı (27 hesaplı + 7 hatalı) kalmıştı. Bu tutarsızlık SPEC v1.1'de giderildi (`HALLUCINATIONS.md` H-12). Güncel referans kümesi 30 hesaplı + 8 hatalı vektörden oluşur. SPEC §7'deki örnekler bu kümenin tamamı değil, bir alt kümesidir; tabloda olmayan 8 hesaplı satır (V05, V06, V07, V08, V09, V11, V13, V17) da bu diferansiyel testte çalıştırıldı.

## 2. statsmodels kütüphane vektörleri

Üretim: `statsmodels 0.15.0`, `scipy 1.18.1`, tohum `20261019`. Her mod için 500 satır:
a-priori (tails, dz ∈ [0.05, 2.5], alpha ∈ {0.001, 0.01, 0.05, 0.10}, power ∈ [0.5, 0.99]) ve
post-hoc (N ∈ [3, 500] tamsayı). Eşleştirilmiş t, statsmodels'ta tek örneklem t testi olarak modellendi
(`effect_size = dz`, `nobs = N`). Tek kuyrukta `alternative="larger"`, iki kuyrukta `"two-sided"`.

### Post-hoc güç

| Ölçüt | Sonuç |
|---|---|
| statsmodels değeri sonlu olan satır | 419 / 500 |
| Bu satırlarda \|bizim güç − statsmodels gücü\| ≤ 1e-6 | **419 / 419** (en büyük fark 1.1e-16) |
| statsmodels NaN döndüren satır | 81 / 500 |

Açıklama (81 NaN): statsmodels iki kuyruklu gücün alt kuyruk terimi `nct.cdf(−t_c; df, δ)` büyük δ'da
NaN döndürüyor (SPEC §5.3'te belgelenen sayısal tuzak). Bu satırlarda statsmodels değeri
hesaplanamıyor. Bizim değerimiz, alt kuyruğu 0 sayan referansla birebir eşleşiyor
(`test_posthoc_statsmodels_nan_rows`); yani bu satırlar statsmodels'in eksikliği, bizim hatamız değil.

### A-priori N

| Ölçüt | Sonuç |
|---|---|
| statsmodels kök bulmuş satır | 494 / 500 |
| `ceil(statsmodels N) = bizim N` | **485 / 494** |
| Farklı çıkan satır | 9 / 494 (aşağıda) |
| statsmodels kök bulamadı (NaN) | 6 / 500 (aşağıda) |
| Bizim N için sınır koşulu (güç(N) ≥ hedef, güç(N−1) < hedef) sağlanıyor | **500 / 500** (`test_apriori_*`, bağımsız scipy referansıyla) |

**Yuvarlama kuralı farkı.** statsmodels N'yi kesirli döndürür (ör. 6.81); G*Power ve bizim motor
yukarı yuvarlar (`ceil`). Bu sözleşme farkı, eşleşen 485 satırda sonucu değiştirmiyor. Farklı çıkan
satırların hiçbiri "yakın tamsayı" tipi bir yuvarlama farkı değil; her biri aşağıdaki kütüphane hatasından.

**Farklı çıkan 9 satır** (hepsi iki kuyruklu, α = 0.001):

| id | statsmodels N | bizim N | Açıklama |
|---|---|---|---|
| L-A046 | 7.4756 | 10 | statsmodels kökünde güç ≈ 0.691; eğride N=11..25 arasında NaN var, kök arayıcı bozuluyor |
| L-A047 | 7.8911 | 10 | Aynı mekanizma (kökte güç ≈ 0.728; eğride 27 NaN) |
| L-A068 | 8.4645 | 10 | Aynı mekanizma (kökte güç ≈ 0.784; eğride 34 NaN) |
| L-A191 | 22.2500 | 25 | Aynı mekanizma (kökte güç ≈ 0.966; eğride 16 NaN) |
| L-A210 | 6.9448 | 8 | Aynı mekanizma (kökte güç ≈ 0.625; eğride 30 NaN) |
| L-A213 | 7.2318 | 9 | Aynı mekanizma (kökte güç ≈ 0.633; eğride 22 NaN) |
| L-A331 | 8.9633 | 10 | Aynı mekanizma (kökte güç ≈ 0.779; eğride 27 NaN) |
| L-A396 | 9.7500 | 12 | Aynı mekanizma (kökte güç ≈ 0.857; eğride 21 NaN) |
| L-A500 | 10.1893 | 12 | Aynı mekanizma (kökte güç ≈ 0.918; eğride 23 NaN) |

Mekanizma: statsmodels'ın döndürdüğü "kök" hedef gücü sağlamıyor (kökte güç 0.63–0.97, hedef 0.79–0.98).
Aynı aralıkta statsmodels'ın iki kuyruklu gücü NaN dönüyor; kök arayıcının bu NaN değerleri yüzünden yanlış bir noktada
durduğu en olası açıklama (kök arayıcının iç ayrıntıları bu çalışmada incelenmedi). Bizim N, bağımsız bir hesapla güç(N−1) < hedef ≤ güç(N) koşulunu sağlıyor (L-A046: N=9 için 0.899, N=10 için 0.960, hedef 0.955).

**NaN dönen 6 satır** (hepsi tek kuyruklu, α = 0.10, dz ≈ 2.1–2.4): hedef güç N=2'de zaten sağlanıyor
(ör. L-A049: güç(2) = 0.676 ≥ 0.666). statsmodels'ın arama aralığında işaret değişimi yok ve kök bulunamıyor.
Bizim sonuç SPEC §5.2 adım 2 gereği N=2; bu G*Power'ın V18/V20'de gösterdiği davranışla aynı.

## 3. statsmodels alt kuyruk kontrolü

statsmodels'ın iki kuyruklu gücü alt kuyruğu **dahil ediyor**. Doğrulama girdisi: dz = 0.05, N = 3, α = 0.05.

| Hesap | Güç |
|---|---|
| Yalnızca üst kuyruk | 0.0285 |
| Üst + alt kuyruk (bizim motor) | 0.0503 |
| statsmodels `two-sided` | 0.0503 (fark 2.8e-17 ile üst+alt'a eşit) |

Alt kuyruk katkısı ≈ 0.0218. (Test: `test_statsmodels_two_sided_includes_lower_tail`.)

## 4. Uyuşmazlık özeti

| # | Nerede | Sayı | Sorumlu | Açıklama |
|---|---|---|---|---|
| U1 | G*Power, N/df/7 basamak | 0 | — | Uyuşmazlık yok |
| U2 | statsmodels post-hoc NaN | 81 | statsmodels | Alt kuyruk NaN (SPEC §5.3); bizim değer doğrulandı |
| U3 | statsmodels a-priori yanlış kök | 9 | statsmodels | Eğride NaN; kök hedef gücü sağlamıyor; bizim N doğrulandı |
| U4 | statsmodels a-priori kök yok | 6 | statsmodels | Hedef N=2'de zaten sağlanıyor; bizim N=2 (SPEC §5.2) |
| U5 | Kesirli N ↔ ceil | 0 | — | Sözleşme farkı; ceil uygulandığında sonuç değişmiyor |

Ayrıca: G*Power'ın hata metinlerinde küçük metin farkları var (ör. V21'de "must" kelimesi eksik;
V32'de sondaki nokta yok). SPEC §4 notunda hata metninin puanlanmadığı yazıyor; bu yüzden test
yalnızca `error` alanının varlığını ve çıkış kodunu kontrol ediyor.

## 5. CLI = MCP eşitliği (Oturum 3)

Test: `tests/test_mcp_parity.py`. Her girdi iki yoldan çalıştırılır:
- **CLI:** `python -m pairedpower.cli ...` alt süreç olarak; stdout'taki tek satır JSON okunur.
- **MCP:** `python -m pairedpower.mcp_server` stdio sunucusu başlatılır; resmi `mcp` Python istemcisiyle
  (`stdio_client` + `ClientSession`) **gerçek MCP protokolü üzerinden** `initialize` → `list_tools` → `call_tool("t_paired_power", ...)`.

| Girdi kümesi | Satır | Birebir aynı JSON |
|---|---|---|
| `oracle/gpower_vectors.csv` hesaplı (`GUI-TOPLANDI`) | 30 | **30/30** |
| `oracle/gpower_vectors.csv` hata (`GUI-TOPLANDI-HATA`) | 8 | **8/8** (ikisi de `{"error": ...}`, aynı metin; CLI çıkış kodu 2) |
| `oracle/library_vectors.csv`, eşit aralıklı 30 a-priori + 30 post-hoc | 60 | **60/60** |
| **Toplam** | **98** | **98/98** |

"Birebir aynı": aynı anahtarlar, aynı değerler ve aynı tipler (int / float). Başarılı satırlarda anahtar sırası da
`n_total, actual_power, critical, df, ncp`. MCP aracı hiçbir satırda `isError` döndürmedi.

Neden aynı: iki katman da `engine.solve` (mod seçimi, zorunlu alanlar, §3.1 (2)–(3), §4 doğrulama) ve `engine.to_dict`
(4 ondalık yuvarlama, −0.0 düzeltmesi) yolunu kullanır; CLI'ya özgü olan yalnızca bayrak okuma ve eş ad çözümüdür.
Bu ortak yolu çıkarmak için `cli.py`'deki `_run`/`_format`/`_round` motora taşındı; var olan 1089 test değişiklikten sonra da geçti.

**Uyuşmazlık yok.**
