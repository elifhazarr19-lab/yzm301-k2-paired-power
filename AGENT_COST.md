# AGENT_COST.md — Ajan maliyet ve süreç günlüğü (taslak)

> Ölçülmüş değerler ekran görüntüsüyle desteklenir. Ölçülemeyenler açıkça "ölçülmedi" diye yazılır.

## Oturumlar

| # | Oturum | Ajan / model | Ne yaptı | Süre | Token / maliyet | Kaynak |
|---|---|---|---|---|---|---|
| 1a | İnceleme (plan, SPEC, LEDGER, GUI vektörlerinin okunması ve bağımsız hesap) | Claude (claude.ai, bulut sohbeti, öğrencinin bilgisayarına bağlı) | Belgeleri okudu, 42 ekran görüntüsünü okudu, scipy ile 30 vektörü çapraz kontrol etti, SPEC/LEDGER/HALLUCINATIONS'ı yazdı | ~5,5 saat (14:21–19:56, insan beklemeleri dahil) | **Ölçülmedi** — claude.ai sohbet arayüzü oturum başına token göstermiyor | — |
| 1b | İnceleme (REA + Ghidra ile binary analizi) | Claude Code 2.1.303, claude-opus-5-5 (+ küçük claude-haiku-5-5 çağrıları) | GPowerNT.exe'yi Ghidra ile açtı, 18 bulgu yazdı (`rea_notes/REA_BULGULAR.md`) | Duvar saati 39 dk 43 sn; API 8 dk 18 sn | **$5.52**; opus: 1.3k input, 44.3k output, 9.2M cache read, 348.4k cache write; 42 istek, girdinin %96'sı önbellekten | `oracle/screenshots/S02_rea_maliyet.png` |
| 2 | Yazım (temiz oda; yazım + diferansiyel test + kütüphane vektörleri + SPEC v1.1 uyumu) | Claude Code, claude-haiku-5-5 | `src/`, `tests/` (1089 test), `oracle/library_vectors.csv`, `tests/UYUM_RAPORU.md`; 3 görev prompt'u | Duvar saati 22 dk 28 sn; API 7 dk 30 sn | **$0.59**; haiku: 3.1k input, 85.8k output, 8.0M cache read, 144.5k cache write; 45 istek, girdinin %99'u önbellekten; 1081 satır eklendi, 35 silindi | `oracle/screenshots/S03_yazim_maliyet.png` |

## Karşılaştırma
- REA analizi (opus) $5.52 tuttu; yazım + test (haiku) $0.59. **Pahalı olan kod yazmak değil, binary'yi anlamaktı.** Doğru işe doğru model: ayrıntılı bir SPEC sayesinde daha küçük bir model kodu ilk denemede doğru yazdı (38/38 SPEC testi, ardından 30/30 G*Power N uyumu).
- Yazım oturumu SPEC'te 6 belirsizlik ve 1 sayım tutarsızlığı (H-12) buldu; SPEC v1.1 ile kapatıldı.

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
