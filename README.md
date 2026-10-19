# pairedpower — Eşleştirilmiş örneklem t testi için güç analizi CLI'si (YZM301 · Teardown Sprint · K2)

> **Yapılan katmanlar:** ✅ Temel katman (CLI) · ❌ MCP sunucusu (yapılmadı) · ❌ AI ajanı (yapılmadı)

**Hazırlayan:** Elif Hazar — bireysel çalışma (gruplar listesinde 8. grup; hoca bireysel çalışmayı onayladı)
**Test ailesi:** K2 — t testi, eşleştirilmiş ortalamalar (önce/sonra tansiyon). G*Power karşılığı: *t tests → Means: Difference between two dependent means (matched pairs)*.

Bu proje G*Power'ın yerine geçmez ve G*Power adını taşımaz. G*Power'ın matched-pairs t testi davranışı tersine mühendislik ve arayüz gözlemiyle belgelendi, ardından temiz oda yöntemiyle yeniden yazıldı. CLI komutunun adı (`gpower-clone`) ödev sözleşmesinden gelir.

---

## Sonuçlar (özet)

| Ölçüt | Sonuç | Kaynak |
|---|---|---|
| G*Power arayüz vektörleri | 38 (30 hesaplı + 8 hata), hepsi ekran görüntülü | `oracle/gpower_vectors.csv`, `oracle/screenshots/` |
| **N ve df tam eşleşme** | **30/30** | `tests/test_differential.py` |
| Güç, kritik t, δ (G*Power'ın 7 ondalığı) | 90/90 | aynı |
| Hata vektörleri (G*Power hata verdi → biz de hata) | 8/8 | aynı |
| Kütüphane vektörleri (statsmodels) | 1000 vektör; farkların hepsi açıklandı | `oracle/library_vectors.csv`, `tests/UYUM_RAPORU.md` |
| Toplam test | 1089 geçti | `pytest -q` |
| [REA] bulguları | 16 adresli bulgu, GUI ile çapraz doğrulandı | `LEDGER.md`, `rea_notes/REA_BULGULAR.md` |
| Kanıtlanmış ajan hataları | 7 madde | `HALLUCINATIONS.md` |

## Kurulum

Python 3.10+ gerekir (geliştirme ve test Python 3.14, scipy 1.18.1 ile yapıldı).

```
python -m venv .venv
.venv\Scripts\activate          (macOS/Linux: source .venv/bin/activate)
pip install -e ".[dev]"
```

## Çalıştırma

```
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
{"n_total":34,"actual_power":0.8078,"critical":2.0345,"df":33,"ncp":2.9155}

gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 35
{"n_total":35,"actual_power":0.8195,"critical":2.0322,"df":34,"ncp":2.958}

gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.04
{"error": "Power must be greater than or equal to alpha."}      (çıkış kodu 2)
```

| Bayrak | Anlam |
|---|---|
| `--test t-paired` | test ailesi |
| `--mode a-priori` / `post-hoc` | N hesapla / gücü hesapla |
| `--tails 1` / `2` | tek / iki kuyruk |
| `--dz` (eş ad `--d`) | etki büyüklüğü dz = ortalama fark / farkların SD'si |
| `--alpha` | I. tip hata |
| `--power` | hedef güç (a-priori) |
| `--n` (eş adlar `--n-total`, `--n_total`) | çift sayısı (post-hoc) |

Ödevde t-paired için ayrı bir CONTRACT.md bulunmadığından bayrak ve alan adları t2-indep örneğinden türetildi; iki olası adlandırma da kabul edilir (`SPEC.md` §3, `HALLUCINATIONS.md` H-01).

## Testler

```
pytest -q
```
- `tests/test_spec.py` — SPEC §7 Gherkin senaryoları ve §3.1 kararları
- `tests/test_differential.py` — G*Power arayüz vektörlerine karşı diferansiyel test
- `tests/test_library.py`, `tests/gen_library_vectors.py` — statsmodels ile 1000 vektör
- `tests/UYUM_RAPORU.md` — uyum oranları ve her uyuşmazlığın açıklaması
- `tools/library_check.py` — inceleme oturumunda kullanılan bağımsız scipy çapraz kontrolü (uygulama kodu değildir)

## Sürüm bilgisi

| Bileşen | Sürüm / değer |
|---|---|
| İncelenen program | G*Power 3.1.9.7 (Windows), resmi sayfadan (psychologie.hhu.de) |
| Program dosyası | `GPowerNT.exe` (ödev metninde `GPower.exe` olarak geçiyor; resmi paketteki adı budur) |
| **SHA-256** | **`C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`** (`oracle/screenshots/S00_hash.png`) |
| Ghidra | 12.1.4 PUBLIC (zip SHA-256 GitHub sürüm sayfasıyla karşılaştırıldı) |
| REA | rea-agents 6.7.0 (npm), Ghidra sağlayıcısı |
| JDK | Temurin 21.0.12.1 |
| Ajanlar | Claude (claude.ai, inceleme ve şartname), Claude Code 2.1.303 (REA analizi ve temiz oda yazımı) |
| Python / scipy | 3.14 / 1.18.1 |

G*Power programı bu depoda **yoktur** ve dağıtılmaz (`.gitignore`).

## REA / Ghidra kontrolü

Ajan: *"REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?"* → Claude Code: evet; Ghidra 12.1.4 kullanılabilir, analyzeHeadless ve yerel decompiler bulundu.

![REA kontrol](oracle/screenshots/S01_rea_kontrol.png)

Not: claude.ai bulut sohbetlerinde REA kullanılamadı; yerel Claude Code gerekti (`HALLUCINATIONS.md` H-10).

## Süreç ve temiz oda

1. **İnceleme (Oturum 1):** belgeler okundu; G*Power arayüzünden 38 vektör ekran görüntüsüyle toplandı; REA + Ghidra ile hesap motoru incelendi (`prompts/oturum1_inceleme.md`, `prompts/oturum1_rea_gorevi.md`). Çıktılar: `LEDGER.md`, `SPEC.md`, `HALLUCINATIONS.md`, `oracle/`, `rea_notes/`.
2. **Yazım (Oturum 2):** ayrı bir klasörde (`C:\paired-power`), yeni bir Claude Code oturumu yalnızca `SPEC.md` ile başladı (`prompts/oturum2_yazim.md`). G*Power vektörleri (yalnızca girdi/çıktı değerleri) kod ve SPEC testleri bittikten sonra diferansiyel test için verildi (`prompts/oturum2_diferansiyel.md`). Yazım oturumu LEDGER'ı, REA notlarını ve decompile çıktısını görmedi.
3. Teslim edilen kodda decompile çıktısı yoktur. `rea_notes/REA_BULGULAR.md` yalnızca fonksiyon/dize adresleri ve kısa alıntılar içerir (ödevin izin verdiği biçimde).

## Belgeler

| Dosya | İçerik |
|---|---|
| `SPEC.md` | Kabul kriterleri Gherkin formatında; her kural kanıt etiketiyle |
| `LEDGER.md` | Kanıt defteri: [DOK], [REA], [AJAN] ve GUI gözlemleri |
| `HALLUCINATIONS.md` | Ajanın yanlış çıkardıkları, nasıl fark edildiği, hangi testin yakaladığı |
| `AGENT_COST.md` | Ajanlar, ölçülmüş maliyet, iterasyonlar, neyi farklı yapardık |
| `prompts/` | İki oturumun ilk prompt'ları ve sonraki görev prompt'ları |
| `oracle/` | G*Power vektörleri, kütüphane vektörleri, ekran görüntüleri |

## Demo

60 saniyelik CLI videosu (36 sn): https://drive.google.com/file/d/132n-g22Ssp__Az5gds-arHfjYCCOhaw2/view?usp=sharing

Videoda: a-priori (N=34), post-hoc (güç 0.8195), geçersiz girdi (`error`) ve G*Power diferansiyel testi (38 passed).

## Atıf

G*Power'ın yazarlarına bu aracı bilim dünyasına ücretsiz sundukları için teşekkür ederiz:

- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.

Bu çalışma YZM301 dersi kapsamında eğitim amacıyla yapılmıştır.
