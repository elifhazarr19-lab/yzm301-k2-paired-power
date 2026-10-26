# Oturum 3 — MCP sunucusu ve AI ajanı (bonus katmanlar) · ilk prompt

Bu prompt, YZM301 "Teardown Sprint" ödevinin bonus katmanlarını yazan yeni Claude Code oturumuna verildi.
Öğrenci: Elif Hazar (bireysel). Test ailesi: K2 — t testi, eşleştirilmiş örneklem (t-paired).

---

## Rolün
Bir yazılım geliştiricisisin. Var olan, testleri geçen bir hesap motorunun üstüne iki ince katman ekleyeceksin: bir **MCP sunucusu** ve bu sunucuyu kullanan Türkçe bir **AI ajanı**. Hesap mantığına dokunmayacaksın.

## Temiz oda kuralı (çok önemli)
Bu repo bir temiz oda çalışması. Kod yazan oturum G*Power'ın decompile çıktısını görmemeli.
- **Okuyabileceğin dosyalar:** `SPEC.md`, `README.md`, `README_dev.md`, `AGENT_COST.md`, `pyproject.toml`, `src/`, `tests/`, `oracle/gpower_vectors.csv`, `oracle/library_vectors.csv`, `oracle/README.md`.
- **Açmayacağın dosyalar:** `LEDGER.md`, `HALLUCINATIONS.md`, `rea_notes/` klasörü, `prompts/oturum1_*.md`. Bunlar binary analizinden adres ve kod alıntısı içeriyor.
- Bir şey SPEC'te ya da yukarıdaki dosyalarda yoksa tahmin etme; bana sor.

## Ödevin bu katmanlar için şartları (ödev metninden, birebir)
**Genel kural:** "Hesap mantığı tek motordadır. CLI, MCP ve ajan bu motoru çağıran ince katmanlardır."

**+15 MCP SUNUCUSU**
- Aynı motoru çağıran ince bir adaptör; hesap mantığı MCP katmanına kopyalanmaz.
- Araç şeması (girdi ve çıktı alanları) README'de belgelenmeli.
- CLI ile MCP'nin aynı girdide aynı çıktıyı verdiğini gösteren testler.

**+10 AI AJANI (MCP şart)**
- Hekimin kendi diliyle sorduğu klinik soruyu (Türkçe) MCP aracını çağırarak yanıtlayan bir ajan.
- 10 soruluk değerlendirme seti: her soru için beklenen test ailesi, parametreler ve N. Doğru seçim oranını raporlayın.
- Araç çağrı kayıtları (log).
- Ölçülmüş token karşılaştırması: aynı sorular MCP üzerinden ve GUI üzerinden (ekran görüntüsüyle) çözülür; iki yolun token, süre ve doğruluk değerleri raporlanır.
- Ajan hesabı kendisi YAPMAZ. Hesap her zaman motordan gelir.
- Test ailesi etiketleri: `t2-indep`, `t-paired`, `anova-oneway`, `chi2-contingency`, `multireg-r2`, `ambiguous`, `unsupported`. Etiket `ambiguous` ya da `unsupported` ise (ya da güven düşükse) ajan hesap yapmaz, araştırmacıya sorar. Bu repo yalnızca `t-paired` hesaplar; diğer aileler için ajan "desteklenmiyor" der.

**Teslim:** "Bonus katman yaptıysanız README'nin başında hangi katmanları yaptığınızı açıkça yazın."

## Görevler (sırayla; her adımdan sonra testleri çalıştır)

**G1 — MCP sunucusu**
- `src/pairedpower/mcp_server.py`: resmi Python `mcp` paketiyle (FastMCP) stdio sunucusu. `pyproject.toml`'a bağımlılık ve bir komut girişi (ör. `pairedpower-mcp`) ekle.
- Araç(lar) yalnızca `engine.py`'deki fonksiyonları çağırır. Doğrulama, yuvarlama, JSON alan adları CLI ile **aynı kod yolundan** gelmeli; gerekirse CLI ile MCP'nin ortak kullanacağı tek bir "girdi → sonuç sözlüğü" fonksiyonunu motor tarafına taşı, ama hesap formülü kopyalama.
- Çıktı alanları CLI ile birebir aynı: `n_total`, `actual_power`, `critical`, `df`, `ncp`; hata durumunda `error`.

**G2 — CLI = MCP testleri**
- `tests/test_mcp_parity.py`: `oracle/gpower_vectors.csv`'deki 38 satırın (30 hesaplı + 8 hata) her biri ve en az 50 `library_vectors.csv` satırı için CLI'yı alt süreç olarak, MCP aracını ise **gerçek MCP protokolü üzerinden** (stdio istemcisiyle) çağır; iki JSON'un birebir aynı olduğunu doğrula.
- Var olan 1089 test yine geçmeli.

**G3 — Ajan**
- Ajanın LLM'i olarak Claude Code'u başsız modda (`claude -p`) kullan; yalnızca bizim MCP aracımıza izin ver (`--mcp-config`, `--allowedTools`). Sistem prompt'u Türkçe olsun: önce test ailesi etiketini seç, sonra parametreleri çıkar, aracı çağır, sonucu hekime sade Türkçeyle anlat; sayıyı asla kendin üretme.
- Ajanı çalıştıran betik: `src/pairedpower/agent.py` (ya da `agent/` klasörü). Her soru için tam akışı (araç çağrısı argümanları, araç sonucu, son cevap, token kullanımı, süre) `agent/logs/` altına JSON olarak kaydet. `--output-format stream-json` ya da `json` çıktısındaki kullanım değerlerini kullan; tahmin yazma.

**G4 — 10 soruluk değerlendirme seti**
- `agent/eval_set.csv`: 10 Türkçe, kurgusal klinik soru (gerçek hasta verisi yok). Her satırda beklenen etiket, beklenen parametreler (mod, kuyruk, dz, α, güç ya da N) ve beklenen N/güç. Beklenen sayılar `oracle/gpower_vectors.csv`'deki G*Power değerlerinden seçilsin ki doğruluk G*Power'a karşı ölçülsün.
- Dağılım önerisi: 6–7 soru t-paired (a priori ve post hoc, tek ve iki kuyruk, en az bir sınır durumu), 1–2 soru başka aile (beklenen: `unsupported`), 1 soru belirsiz (beklenen: `ambiguous`, ajan soru sormalı).
- `agent/run_eval.py` setin tamamını çalıştırıp `agent/EVAL_RAPORU.md` üretsin: etiket doğruluğu, parametre doğruluğu, N/güç doğruluğu (G*Power'la tam eşleşme), soru başına token ve süre.

**G5 — GUI yolu ölçümü**
- Aynı 10 soru G*Power arayüzü üzerinden, ekran görüntüsüyle çözülecek. Bu adımı **öğrenciyle birlikte** yap: bilgisayar kullanımı (computer use) aracın varsa G*Power penceresini sen sürersin; yoksa öğrenciye adım adım ne yapacağını söyle. Token ve süreyi ölç (oturum kullanım değerleri ya da ekran görüntüsü). Ölçemediğin değeri "ölçülmedi" yaz, uydurma.
- Sonuçları `agent/TOKEN_KARSILASTIRMA.md`'ye yaz: iki yolun soru başına ve toplam token, süre, doğruluk değerleri; nasıl ölçüldüğü.

**G6 — Belgeler**
- `README.md` başındaki katman satırını güncelle (yalnızca gerçekten bitenleri ✅ yap).
- README'ye: MCP kurulumu ve çalıştırma, Claude Code'a kayıt komutu, **araç şeması tablosu** (her girdi/çıktı alanı, tipi, zorunluluk), ajanı çalıştırma, değerlendirme sonuç özeti, token karşılaştırması özeti.
- `AGENT_COST.md`'ye bu oturumun satırını ekle (model, süre, ölçülmüş token/maliyet, iterasyon).
- `tests/UYUM_RAPORU.md`'ye MCP eşitlik testinin sonucunu ekle.

## Kurallar
1. Kanıt yoksa iddia yok. Her rakam bir dosyaya, log'a ya da ölçüme bağlı olmalı.
2. Testleri her adımdan sonra çalıştır; kırılan test varsa düzeltmeden ilerleme.
3. Git'e commit/push yapmadan önce bana sor.
4. Bitirince bana kısa bir özet ver: hangi şartlar tamam, hangileri eksik, ölçülen token farkı.
