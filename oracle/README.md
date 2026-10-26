# oracle/ — referans değerler (kâhin)

## `gpower_vectors.csv` — G*Power 3.1.9.7 arayüz vektörleri
Yalnızca G*Power arayüzünde elle girilip ekrandan okunan değerler. Kütüphane değerleri bu dosyaya karıştırılmaz.

| Durum (`status`) | Sayı | Anlam | Ekran görüntüsü |
|---|---|---|---|
| `GUI-TOPLANDI` | 30 | G*Power hesapladı; N, güç, kritik t, df, δ 7 ondalıkla kayıtlı | var |
| `GUI-TOPLANDI-HATA` | 8 | G*Power "Input error" verdi; mesaj `gp_error_message` sütununda birebir | var (hata penceresiyle) |
| `IPTAL (kapsam daraltildi)` | 4 | V30, V31, V35, V36 — planlandı, toplanmadı; testlerde **kullanılmaz** | yok |
| **Toplam satır** | **42** | | **38 PNG** |

- Kimlikler V01–V43'tür; **V37 kullanılmadı** (numara atlandı), iptal edilen dört satırın görüntüsü yoktur.
- Mod dağılımı: a-priori 23 hesaplı + 6 hata; post-hoc 7 hesaplı + 2 hata.
- Sınır vektörleri: V13–V26 (çok küçük/büyük dz, güç = α, geçersiz α/güç, negatif dz), V32–V34 ve V38–V39, V42 (post-hoc N alt sınırı, kesirli N), V40–V43 (REA iddialarının sınanması).
- V02 ve V20 ilk alımda hatalıydı ve yeniden alındı; repodaki görüntüler geçerli olanlardır (`LEDGER.md` G-02, G-05).

## `screenshots/`
| Dosya | İçerik |
|---|---|
| `V01.png` … `V43.png` (38 dosya) | Her vektörün G*Power penceresi (girdiler + çıktılar ya da hata penceresi) |
| `S00_surum.png`, `S00_hash.png` | G*Power sürümü (About) ve `GPowerNT.exe` SHA-256 |
| `S01_rea_kontrol.png` | "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" sorusunun cevabı |
| `S01a_kurulum.png` | Node.js / Java sürümleri |
| `S02_rea_maliyet.png`, `S03_yazim_maliyet.png` | Claude Code oturumlarının ölçülmüş maliyeti |
| `S04_testler.png` | Temiz kurulumla `pytest -q` → 1089 passed (Oturum 2 sonundaki durum; MCP ve kılavuz testleriyle güncel toplam 1190) |

## Diğer dosyalar
- `manual_vectors.csv` — G*Power 3.1 kılavuzunun (June 1, 2023, resmi sayfadan) §19.3 matched-pairs örnekleri: 2 post-hoc vektör, kılavuzun verdiği 6 ondalıklı değerlerle. Karşılaştırma: `tests/test_manual.py`.
- `gpower_sha256.txt` — `GPowerNT.exe` SHA-256 (PowerShell çıktısı, UTF-16).
- `library_vectors.csv` — statsmodels ile üretilmiş 1000 vektör (500 a-priori + 500 post-hoc). **G*Power değildir.** Üretim: `tests/gen_library_vectors.py`; karşılaştırma: `tests/test_library.py`, `tests/UYUM_RAPORU.md`.
