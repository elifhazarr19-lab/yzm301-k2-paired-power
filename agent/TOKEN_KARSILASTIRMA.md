# Token karşılaştırması — MCP yolu ve GUI yolu (ekran görüntüsüyle)

Üretim: `python agent/token_compare.py` · 2026-10-26 15:14. Bu dosyadaki her sayı aşağıda adı geçen log, CSV ya da ölçümden gelir.

## Özet (aynı model, aynı birim)

Aynı model (**claude-opus-5-5**) ve aynı birimle (**bağlama eklenen token**), GUI'nin uygulanabildiği 9 soruda (Q01–Q09): MCP yolu **9,124**, GUI yolu **19,660** token ekledi (ölçüm yükü çıkarılmış; ham 26,275). GUI yolu **2.2 kat** daha fazla bağlam tüketti; Q01'deki tek seferlik kurulum hariç (Q02–Q09) oran **1.5 kat** (7,860 / 11,719). Model çağrısı: MCP 16, GUI 31. Süre: MCP 187 sn, GUI 254 sn. Doğruluk: MCP 10/10, GUI 9/9. GUI yolu soruyu anlama adımını **içermiyor** (parametreler hazır verildi); yani GUI değerleri bir alt sınırdır.

Faturalanan token yalnızca MCP yolunda ölçüldü. GUI yolu için faturalanan token **ölçülmedi**; aşağıda ölçülen bağlam boyutlarından hesaplanmış bir aralık var (ölçüm değildir).

## Düzen

| | MCP yolu | GUI yolu |
|---|---|---|
| Kim çözdü | `agent/agent.py` → `claude -p` (Claude Code 2.1.309); ana karşılaştırma **claude-opus-5-5** (`agent/logs_opus/`), ek olarak claude-haiku-5-5 (`agent/logs/`); yalnızca `t_paired_power` MCP aracı | Claude Code masaüstü oturumu (Oturum 3), **claude-opus-5-5**, bilgisayar kullanımı aracıyla G*Power 3.1.9.7 penceresi; öğrencinin erişim onayıyla |
| Girdi | Hekimin Türkçe sorusu (ham metin) | Sorudan önceden çıkarılmış parametreler (`eval_set.csv`). **Soruyu anlama adımı GUI ölçümüne dahil değil** |
| Kanıt | `agent/logs_opus/Qxx.json`, `agent/EVAL_RAPORU_opus.md` (haiku: `agent/logs/`, `agent/EVAL_RAPORU.md`) | `agent/gui_measurements.csv`, `agent/gui_screenshots/Q01–Q09.jpg` |

## Ana tablo — aynı birim, aynı model (claude-opus-5-5)

| id | MCP bağlama eklenen | GUI bağlama eklenen (ölçüm yükü çıkarılmış) | GUI ham artış | MCP model çağrısı | GUI model çağrısı (GUI + ölçüm) | MCP süre (sn) | GUI süre (sn) | MCP doğru | GUI doğru |
|---|---|---|---|---|---|---|---|---|---|
| Q01 | 1,264 | 7,941 | 8,676 | 2 | 11 (10 + 1) | 20.1 | 84 | ✅ | ✅ |
| Q02 | 1,245 | 1,569 | 2,304 | 2 | 2 (1 + 1) | 20.4 | 19 | ✅ | ✅ |
| Q03 | 1,055 | 1,381 | 2,116 | 2 | 2 (1 + 1) | 20.1 | 19 | ✅ | ✅ |
| Q04 | 944 | 2,328 | 3,063 | 2 | 4 (3 + 1) | 18.3 | 28 | ✅ | ✅ |
| Q05 | 949 | 1,140 | 1,875 | 2 | 2 (1 + 1) | 20.2 | 15 | ✅ | ✅ |
| Q06 | 1,225 | 1,421 | 2,156 | 2 | 2 (1 + 1) | 23.3 | 22 | ✅ | ✅ |
| Q07 | 1,108 | 1,012 | 1,747 | 2 | 2 (1 + 1) | 20.4 | 13 | ✅ | ✅ |
| Q08 | 732 | 1,146 | 1,881 | 1 | 2 (1 + 1) | 19.7 | 20 | ✅ | ✅ |
| Q09 | 602 | 1,722 | 2,457 | 1 | 4 (3 + 1) | 24.8 | 34 | ✅ | ✅ |
| Q10 | 718 | uygulanamaz | — | 1 | 0 | 17.6 | — | ✅ | uygulanamaz |
| **Q01–Q09 toplam** | **9,124** | **19,660** | 26,275 | **16** | **31** | **187.3** | **254** | 9/9 | 9/9 |
| Q02–Q09 (kurulum hariç) | 7,860 | 11,719 | 17,599 | 14 | 20 | 167.2 | 170 | | |

GUI Q01 tek seferlik kurulum içeriyor: bilgisayar kullanımı araç şemalarının yüklenmesi (+2,934 token), pencereyi öne getirme denemeleri, test türünün seçilmesi ve bir giriş hatasının düzeltilmesi. Q08/Q09'da G*Power'da yalnızca doğru testin bulunduğu kontrol edildi (G*Power vektörü yok). Q10 (belirsiz) GUI'de uygulanamaz.

### Formüller

- **MCP, bağlama eklenen** = (son model çağrısının girdisi + son çağrının çıktısı) − P.
  - Son çağrının girdisi = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`, `usage.iterations[-1]` alanından. Aracı çağıran sorularda bu girdi, sorunun kendisini, ilk çağrının çıktısını (araç çağrısı) ve araç sonucunu içerir.
  - **P (sabit önek: sistem prompt'u + araç şeması + çağrı çerçevesi)**, aynı bayraklarla yalnızca `"."` gönderilen kalibrasyon çağrısının girdisidir: opus **3,623**, haiku **3,586** token (`agent/logs_calibration/prefix_*.json`). "." ve mesaj çerçevesi birkaç token olduğu için P'ye dahil sayıldı.
- **GUI, bağlama eklenen** = `tokensUsed(sonra) − tokensUsed(önce)` − ölçüm yükü × ölçüm turu. `tokensUsed` her sorudan önce ve sonra `get_usage` aracıyla okundu (`agent/gui_measurements.csv`).
  - **Ölçüm yükü = 735 token** / ölçüm adımı (ardışık iki ölçüm: 236,387 → 237,122 token (2026-10-26 12:10:34Z → 12:10:38Z)). Her soruda bir ölçüm adımı var. "GUI ham artış" sütunu bu düzeltme yapılmamış değerdir.
- **Model çağrısı:** MCP için logdaki `num_turns`. GUI için o soruda yapılan araç turu sayısı (her tur bir model çağrısı) + 1 ölçüm turu (`get_usage` ve `date` aynı turda paralel çağrıldı).
- **Süre:** MCP: betiğin ölçtüğü duvar saati (`claude -p` açılışı dahil). GUI: ardışık `date -u` damgaları arası (ölçüm adımı dahil).

## Ek: aynı soruların claude-haiku-5-5 ile MCP sonuçları

| id | haiku bağlama eklenen | haiku model çağrısı | haiku süre (sn) | haiku doğru | haiku faturalanan token | haiku maliyet ($) |
|---|---|---|---|---|---|---|
| Q01 | 1,019 | 2 | 19.1 | ✅ | 8,608 | 0.00073 |
| Q02 | 911 | 2 | 13.2 | ✅ | 8,454 | 0.00067 |
| Q03 | 1,060 | 2 | 16.8 | ✅ | 8,634 | 0.00076 |
| Q04 | 880 | 2 | 17.9 | ✅ | 8,397 | 0.00067 |
| Q05 | 837 | 2 | 17.2 | ✅ | 8,358 | 0.00065 |
| Q06 | 1,158 | 2 | 20.8 | ✅ | 8,712 | 0.00081 |
| Q07 | 973 | 2 | 17.9 | ✅ | 8,540 | 0.00071 |
| Q08 | 727 | 1 | 16.5 | ✅ | 4,313 | 0.00053 |
| Q09 | 737 | 1 | 17.4 | ✅ | 4,323 | 0.00054 |
| Q10 | 1,276 | 1 | 17.7 | ✅ | 4,862 | 0.00083 |
| **toplam** | **9,578** | 17 | 174.6 | 10/10 | 73,201 | 0.0069 |

## Faturalanan token

**MCP (ölçüldü):** her logdaki `usage` toplamı (input + cache yazma + cache okuma + output) ve `total_cost_usd`.

| | Q01–Q09 faturalanan token | Q01–Q10 faturalanan token | Q01–Q10 maliyet |
|---|---|---|---|
| MCP · claude-opus-5-5 | 69,197 | 73,538 | $0.2700 |
| MCP · claude-haiku-5-5 | 68,339 | 73,201 | $0.0069 |
| GUI · claude-opus-5-5 | **ölçülmedi** | uygulanamaz | **ölçülmedi** |

**GUI (hesaplanan aralık — ölçüm değil, ölçülen değerlerden hesaplanan sınır):** her model çağrısı o anki oturum bağlamının tamamını girdi olarak okur. Sorudaki model çağrısı sayısı t, sorudan önceki bağlam C_önce, sonraki C_sonra ise girdi token'ı t × C_önce ile t × C_sonra arasındadır.

- Q01–Q09: **5,517,724 – 5,659,398** token (çıktı token'ı eklenmedi; büyük kısmı önbellekten okuma olarak faturalanır).
- Bu aralık bu oturumun büyük taban bağlamına (~167k token: önceki işler, araç şemaları) bağlıdır; boş bir oturumda başlayan bir GUI ajanı için çok daha küçük olurdu. Bu yüzden MCP'nin ölçülmüş faturalanan token'ıyla doğrudan karşılaştırılmamalıdır; asıl karşılaştırma yukarıdaki aynı birimli tablodur.

## Doğruluk

| | MCP · opus | MCP · haiku | GUI · opus |
|---|---|---|---|
| Test ailesi etiketi | 10/10 | 10/10 | 9/9 test seçimi (Q10 uygulanamaz) |
| Karar (araç çağır / çağırma) | 10/10 | 10/10 | uygulanamaz |
| Parametreler (t-paired, 7 soru) | 7/7 | 7/7 | hazır verildi |
| N/güç = G*Power (t-paired, 7 soru) | 7/7 | 7/7 | 7/7 (GUI zaten G*Power) |

## Sınırlılıklar

- GUI yolunda soruyu anlama ve parametre çıkarma adımı yok; MCP yolunda var. GUI değerleri bu yüzden alt sınırdır.
- GUI ekran görüntüleri tam ekran yerine 0.6 ölçekli kırpılmış (zoom) görüntülerdi; tam ekranla bağlam artışı daha büyük olurdu.
- MCP "bağlama eklenen" değeri son çağrının çıktısındaki düşünme (thinking) token'larını da içerir; GUI ölçümü de oturumun kendi metin ve düşünme token'larını içerir. İkisi de "o soru için bağlamda harcanan token"dır.
- GUI ölçüm yükü tek bir ardışık ölçümle bulundu (735). Soru başına yazılan kısa metinler (~20–40 token) ayıklanmadı.
- MCP süresi her soruda `claude -p` sürecinin açılışını ve kapanışını da içerir: duvar saati − logdaki `duration_ms` ortalaması opus için 6.9 sn/soru. GUI süresi zaten açık bir G*Power penceresiyle ölçüldü.

## Gözlemler

- **GUI yolu hataya açık:** Q01'de alan metni seçilmeden yazıldı ("0.50.5", "0.050.05", "0.800.95"); G*Power yine de sonuç gösterdi. Hata ancak ekran görüntüsü okununca fark edildi ve `Ctrl+A` ile yeniden yapıldı (Oturum 1'deki V02/V20 insan hatalarına benzer).
- **MCP yolu soruyu da anlıyor:** Q01 ve Q07'de dz'yi ortalama fark / farkların SD'sinden kendisi çıkardı; Q08–Q10'da aracı çağırmadı. GUI yolunda bu karar dışarıda kalıyor.
