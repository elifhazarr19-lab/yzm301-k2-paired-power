# AGENT_COST.md — Ajan maliyet ve süreç günlüğü

> Ölçülmüş değerler ekran görüntüsüyle desteklenir. Ölçülemeyenler açıkça "ölçülmedi" diye yazılır.

## Oturumlar

| # | Oturum | Ajan / model | Ne yaptı | Süre | Token / maliyet | Kaynak |
|---|---|---|---|---|---|---|
| 1a | İnceleme (plan, SPEC, LEDGER, GUI vektörlerinin okunması ve bağımsız hesap) | Claude (claude.ai, bulut sohbeti, öğrencinin bilgisayarına bağlı) | Belgeleri okudu, 42 ekran görüntüsünü okudu, scipy ile 30 vektörü çapraz kontrol etti, SPEC/LEDGER/HALLUCINATIONS'ı yazdı | ~5,5 saat (14:21–19:56, insan beklemeleri dahil) | **Ölçülmedi** — claude.ai sohbet arayüzü oturum başına token göstermiyor | — |
| 1b | İnceleme (REA + Ghidra ile binary analizi) | Claude Code 2.1.303, claude-opus-5-5 (+ küçük claude-haiku-5-5 çağrıları) | GPowerNT.exe'yi Ghidra ile açtı, 18 bulgu yazdı (`rea_notes/REA_BULGULAR.md`) | Duvar saati 39 dk 43 sn; API 8 dk 18 sn | **$5.52**; opus: 1.3k input, 44.3k output, 9.2M cache read, 348.4k cache write; 42 istek, girdinin %96'sı önbellekten | `oracle/screenshots/S02_rea_maliyet.png` |
| 2 | Yazım (temiz oda; yazım + diferansiyel test + kütüphane vektörleri + SPEC v1.1 uyumu) | Claude Code, claude-haiku-5-5 | `src/`, `tests/` (1089 test), `oracle/library_vectors.csv`, `tests/UYUM_RAPORU.md`; 3 görev prompt'u | Duvar saati 22 dk 28 sn; API 7 dk 30 sn | **$0.59**; haiku: 3.1k input, 85.8k output, 8.0M cache read, 144.5k cache write; 45 istek, girdinin %99'u önbellekten; 1081 satır eklendi, 35 silindi | `oracle/screenshots/S03_yazim_maliyet.png` |
| 1c | Son kontrol ve belge düzeltmeleri (Oturum 1'in devamı, 2026-10-26) | Claude Code (masaüstü uygulaması), claude-opus-5-5 | Belgeler arası tutarsızlıkları düzeltti (HALLUCINATIONS, SPEC, LEDGER, README); Oturum 3'ün ilk prompt'unu yazdı ve oturumu başlattı; Oturum 3'ün token karşılaştırmasını aynı birime getirmesini istedi; G*Power kılavuzunun §19.3 örneklerini kâhine ekledi (`oracle/manual_vectors.csv`, `tests/test_manual.py`); temiz bir klonda kurulum ve 1190 testi doğruladı. `src/`'ye dokunmadı | Ölçülmedi | **Ölçülmedi** (Pro plan; oturum başına token/maliyet gösterilmiyor) | git geçmişi (`b60c867`, `573cb27`) |
| 3 | Bonus katmanlar (MCP sunucusu, CLI = MCP testleri, ajan, 10 soruluk değerlendirme, GUI karşılaştırması, belgeler) | Claude Code (masaüstü uygulaması), claude-opus-5-5, effort medium | `src/pairedpower/mcp_server.py`, motorda ortak `solve`/`to_dict`/`calculate`, `tests/test_mcp_parity.py` (99 test), `agent/` (ajan, set, rapor, loglar), G*Power'ı bilgisayar kullanımı aracıyla sürdü | Duvar saati ~20 dk (oturum 11:43:20Z açıldı; belgeler 12:03Z'de yazıldı) | **Ölçülmedi** (Pro plan; oturum başına token/maliyet gösterilmiyor). Ölçülebilenler: bağlam penceresi 12:03Z'de 215,855 token; 5 saatlik plan kullanımı 11:55Z'de %33 → 12:03Z'de %39 | `get_usage` aracı (oturum içi) |
| 3a | Ajan değerlendirmesi (10 soru, MCP yolu) | `claude -p` (Claude Code 2.1.309), claude-haiku-5-5 | `agent/run_eval.py`: 10 soru, 10 ayrı başsız çağrı, 7 MCP araç çağrısı | 174.6 sn (10 soru toplamı) | **$0.0069**; 73,201 token (input 34 · cache yazma 12,808 · cache okuma 52,714 · output 7,645); 17 tur | `agent/logs/Q01–Q10.json`, `agent/EVAL_RAPORU.md` |
| 3b | Ajan değerlendirmesi, aynı set, GUI ile aynı model | `claude -p` (Claude Code 2.1.309), claude-opus-5-5 | `agent/run_eval.py --model claude-opus-5-5 --log-dir agent/logs_opus`; 10/10 etiket, 7/7 parametre, 7/7 N/güç | 204.9 sn | **$0.2700**; 73,538 token; 17 tur | `agent/logs_opus/`, `agent/EVAL_RAPORU_opus.md` |
| 3c | Önek kalibrasyonu (soru ".", iki model) | `claude -p`, haiku ve opus | Sistem prompt'u + araç şemasının token sayısı (haiku 3,586, opus 3,623) | 14.8 + 13.9 sn | $0.0006 + $0.0392 | `agent/logs_calibration/` |
| 3d | GUI yolu (aynı 10 soru, G*Power ekran görüntüleriyle) | Oturum 3 içinde, claude-opus-5-5 + bilgisayar kullanımı | 31 model çağrısı (22 GUI + 9 ölçüm), 9 kırpılmış ekran görüntüsü | 254 sn | Bağlama eklenen 19,660 token (ölçüm yükü çıkarılmış; ham 26,275), ölçüldü; faturalanan token/maliyet **ölçülmedi** | `agent/TOKEN_KARSILASTIRMA.md`, `agent/gui_measurements.csv`, `agent/gui_screenshots/` |

## Karşılaştırma
- REA analizi (opus) $5.52 tuttu; yazım + test (haiku) $0.59. **Pahalı olan kod yazmak değil, binary'yi anlamaktı.** Doğru işe doğru model: ayrıntılı bir SPEC sayesinde daha küçük bir model kodu ilk denemede doğru yazdı (38/38 SPEC testi, ardından 30/30 G*Power N uyumu).
- Yazım oturumu SPEC'te 6 belirsizlik ve 1 sayım tutarsızlığı (H-12) buldu; SPEC v1.1 ile kapatıldı.

## İterasyonlar (Oturum 3)
- G1 (MCP sunucusu): 1 tur. Kurulan `mcp` 2.3.0'da FastMCP adı değişmişti (`MCPServer`); prompt FastMCP istediği için `mcp>=1.2,<2` sabitlendi (1.30.0).
  CLI'daki `_run`/`_format`/`_round` motora (`engine.solve`, `engine.to_dict`, `engine.calculate`) taşındı; 1089 test değişmeden geçti.
- G2 (CLI = MCP): 1 tur, 99/99 test (98 girdi + sayım testi). Toplam 1188 test.
- G3 (ajan): 1 deneme çalıştırması ile akış doğrulandı (log silindi), sonra değerlendirme.
- G4 (değerlendirme): tek çalıştırma, 10/10 etiket, 7/7 parametre, 7/7 N/güç. Prompt ya da set değerlendirme sonrasında değiştirilmedi.
- Token karşılaştırması ikinci turda yeniden kuruldu: ilk sürüm farklı birimleri (MCP faturalanan / GUI bağlam artışı) ve farklı modelleri (haiku / opus) yan yana koyuyordu. MCP seti opus ile yeniden çalıştırıldı, sabit önek kalibrasyonla ölçüldü, ana tablo tek birime (bağlama eklenen token) indirildi.
- G5 (GUI): Q01'de üçlü tıklama alan metnini seçmedi ("0.50.5" gibi değerler oluştu); ekran görüntüsünde fark edilip `Ctrl+A` ile yeniden yapıldı.

## İterasyonlar (Oturum 2)
- Görev 1 (yazım): 1 tur, 38/38 SPEC testi.
- Görev 2 (diferansiyel + kütüphane): 1 tur; SPEC v1.1 kopyalama hatası nedeniyle §3.1 işi ayrı bir tura kaldı.
- Görev 3 (SPEC v1.1 uyumu): 1 tur; 2 gerçek düzeltme (tails kontrol sırası, a-priori N üst sınırı).

## İterasyonlar (Oturum 1)
- G*Power vektör toplama: 6 tur (V01; V02–V12; V13–V26; V17/V20/V27–V34; V38–V39; V40–V43). 2 vektör veri toplama hatası nedeniyle yeniden alındı (V02: Calculate'e basılmamış, V20: kuyruk seçimi yanlış).
- REA: tek görev prompt'u, tek çalıştırma (`prompts/oturum1_rea_gorevi.md`).
- SPEC sürümleri: v0 → v0.9 (REA sonrası) → v1.0 (REA iddiaları GUI ile sınandıktan sonra; H-11 düzeltmesi).

## Gözlemler
- **Ajanın kendi maliyet tahmini güvenilir değil:** REA oturumundaki ajan "yaklaşık 320 bin token" dedi; ölçüm 9.2M cache read + 348k cache write gösterdi. Maliyet yalnızca ölçümle raporlanmalı.
- **Maliyetin %85'i REA'nın tersine mühendislik skill'inden** (Claude Code /usage ekranı). Uzun bağlam (>150k) kullanımın %77'si.
- **GUI ile vektör toplama pahalı ve hataya açık:** 42 ekran görüntüsü; her biri ajan tarafından görüntü olarak okundu. 2 insan hatası (V02, V20) ancak ekran görüntüsü ajanca okunduğunda yakalandı. Ödevdeki "ekran görüntüsü ≈ binlerce token" tezini destekleyen bir deneyim.

## Neyi farklı yapardık?
1. REA'yı en baştan yerel bir istemcide (Claude Code) kurardık; bulut sohbetinde kullanılabileceğini varsaymak zaman kaybettirdi (H-10).
2. REA görevini daha dar parçalara bölüp her parçadan sonra `/compact` kullanırdık; uzun bağlam maliyetin büyük kısmını oluşturdu.
3. Sınır vektörlerini (α=1e-07, dz=±20, kesirli N) baştan planlardık; en değerli hata (H-11) bunlardan biriyle yakalandı.
