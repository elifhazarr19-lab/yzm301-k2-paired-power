# LEDGER.md — Kanıt Defteri (K2 · t-paired · Grup 8)

> **Durum: Son sürüm — 2026-10-19 (Oturum 1 tamamlandı).**
> - G*Power 3.1.9.7 arayüzünden **42 vektör planlandı**: 30'u hesaplı (`GUI-TOPLANDI`), 8'i hata mesajlı (`GUI-TOPLANDI-HATA`) olarak ekran görüntüsüyle toplandı; 4'ü (V30, V31, V35, V36) kapsam daraltılınca iptal edildi. Bkz. `oracle/README.md`.
> - REA 6.7.0 + Ghidra 12.1.4 ile `GPowerNT.exe` incelendi: **16 [REA]** satırı (aşağıda), 2 [AJAN] satırı.
> - Bölümler kronolojik sırayla yazıldı: E-00 (oturum başındaki durum) → E-01/E-02 (binary ve araç kurulumu) → G-01…G-07 (GUI gözlemleri) → [DOK] → [AJAN] (ilk hipotezler) → [REA] (binary kanıtları).
> - Erken bölümlerdeki "bekliyor / yeniden alınacak" notları, o anki durumu kayıt altına almak için bırakıldı; her birinin sonradan nasıl kapandığı yanında belirtildi.

## Etiketler (ödev belgesinden, değiştirilmeden)
- **[DOK]** Kılavuzda ya da makalede yazıyor.
- **[REA]** Binary'den kanıtlandı (fonksiyon adresi ya da dize referansıyla). *Puan yalnızca bu satırlara verilir.*
- **[AJAN]** Ajanın çıkarımı; kanıtı yok.

Ek durum sütunu (ödevde yok, izlenebilirlik için eklendi):
`AÇIK` = sınanmadı · `GUI-DOĞRULANDI` = G*Power ekranıyla eşleşti · `ÇÜRÜTÜLDÜ` = yanlış çıktı (HALLUCINATIONS.md'ye taşınır)
`KAPANDI` = GUI ve/veya REA ile doğrulandı · `KAPSAM DIŞI` = bilinçli olarak uygulanmadı

## Erişim durumu (E-00) — oturum başlangıcı, 2026-10-19 14:21
*Bu tablo, inceleme sohbetinin (claude.ai bulut ortamı) **başlangıçtaki** araç durumunu gösterir. Araçlar sonradan öğrencinin bilgisayarına kuruldu → E-02.*

| Araç | Başlangıçta (bulut ortamı) | Nasıl kontrol edildi | Sonraki durum |
|---|---|---|---|
| G*Power 3.1.9.7 | YOK | `find / -iname "*gpower*"` boş; `which wine` boş | Öğrencinin Windows bilgisayarında kuruldu (E-01) |
| Ghidra | YOK | `which ghidra analyzeHeadless` boş (Java mevcut) | 12.1.4, öğrencinin bilgisayarında (E-02) |
| REA (rea-agents) | YOK | — | 6.7.0, Claude Code ile kullanıldı (E-02); bulut sohbetine bağlanamadı (H-10) |
| R / pwr | YOK | `which R` boş | Kullanılmadı; kütüphane vektörleri statsmodels ile üretildi |
| Python scipy 1.18.1 | VAR | — | Bağımsız çapraz kontrol (`tools/library_check.py`) |

## E-01 İncelenen binary'nin kimliği (2026-10-19)
| Alan | Değer |
|---|---|
| Kaynak | Resmi G*Power sayfası (psychologie.hhu.de), Windows paketi — öğrenci indirdi |
| Paket içeriği | `GPowerNT.exe`, `VC_redist.x86.exe`, `Close.wav`, `Minimieren.wav` (kurulum dosyası yok, program kurulumsuz çalışıyor) |
| Program dosyası | **`GPowerNT.exe`** (ödev metni `GPower.exe` diyor → H-07) |
| Sürüm | About penceresi: "G*Power Version 3.1.9.7", Copyright (C) 1992–2020 |
| SHA-256 | `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` |
| Nasıl alındı | PowerShell: `Get-FileHash "<yol>\GPowerNT.exe" -Algorithm SHA256` |
| Kanıt | `oracle/screenshots/S00_surum.png`, `oracle/screenshots/S00_hash.png`, `oracle/gpower_sha256.txt` (ekran görüntüsü ile metin dosyası karşılaştırıldı: aynı) |
| Not | Binary repoya konmadı; kopyası proje klasörünün dışında duruyor. |

## G*Power arayüz gözlemleri (GUI)
*Bunlar [REA] değildir; ekranda görülen davranışlardır. [REA] satırlarının "destekleyen GUI vektörü" olarak kullanılacaklar.*

### G-01 İlk referans vektörü ve ekran düzeni (V01)
- **Girdi:** t tests → Means: Difference between two dependent means (matched pairs) → A priori; Two tails, dz=0.5, α=0.05, power=0.80
- **Çıktı (ekran):** δ=2.9154759, critical t=2.0345153, Df=33, Total sample size=34, Actual power=0.8077775
- **Kanıt:** `oracle/screenshots/V01.png`
- **Tekrar üretme:** Yukarıdaki girdilerle Calculate.
- **Gözlemler:**
  1. Türkçe Windows'ta ondalık ayraç olarak **nokta** kabul edildi.
  2. Çıktı alanları **7 ondalık basamak** gösteriyor (D-05'teki 6 basamaklı değerler muhtemelen sondaki 0'ın atılmasıdır). → SPEC §5 basamak kararı için girdi.
  3. Ekranda Df = Total sample size − 1 görülüyor (33 = 34 − 1).
  4. Ekranda "Total sample size" etiketi var; t2-indep'teki n1/n2 alanları bu testte yok.
  5. Grafik üstünde "critical t = 2.03452" (5 basamak) yazıyor; çıktı tablosundaki 7 basamaklı değer esas alınmalı.
- **Bağımsız karşılaştırma:** A-01 modeli (scipy) 5 çıktının 5'ini 7 basamağa kadar aynı verdi. N=33'te güç 0.7953658 < 0.80, N=34'te 0.8077775 ≥ 0.80 → "hedefi geçen en küçük N" ile tutarlı (A-03).
- **Sınırlama:** Tek vektör; sınır durumları henüz sınanmadı.
- **Durum:** GUI-DOĞRULANDI (A-01 ve A-03 bu vektörde destek aldı; kod düzeyinde REA ile de doğrulandı → R-08, R-09, R-12)

### G-02 Normal bölge vektörleri (V03–V12)
- **Girdi/çıktı:** `oracle/gpower_vectors.csv` (V03–V12), ekran görüntüleri `oracle/screenshots/V03.png`…`V12.png`
- **Bağımsız karşılaştırma:** A-01 modeli 10 vektörün 10'unda N, Df, critical t, δ ve actual power değerlerini **7 basamağa kadar** aynı verdi (V01 ile birlikte 11/11).
- **Önemli gözlem — iki kuyrukta alt kuyruk güce ekleniyor:**
  - V03: tek kuyruk, α=0.05, N=27 → critical t 1.7056179, power **0.8118316**
  - V11: iki kuyruk, α=0.10, N=27 → aynı critical t 1.7056179, power **0.8118463**
  - Kritik değer aynı olduğu hâlde iki kuyrukta güç 0.0000147 daha büyük. Bu fark, noncentral t'nin −t_c altındaki olasılığına eşit (scipy: 1.47e-05). → A-01'deki "alt kuyruk eklenir mi?" belirsizliği GUI'de **evet** yönünde çözüldü.
- **UCLA değerleri (D-05) G*Power'da yeniden üretildi:** V06=10, V07=12, V08=13, V09=9 → D-05 artık birincil kanıtla destekleniyor.
- **Veri toplama hatası (kapandı):** V02'nin ilk ekran görüntüsünde çıktılar "?" idi — Calculate'e basılmadan alınmıştı. *(Gözlem: girdi değişince G*Power eski sonucu "?" ile siliyor.)* V02 aynı turda yeniden alındı ve geçerli: N=54, güç 0.9502120 → G-03. Repodaki `V02.png` yeni (geçerli) görüntüdür.
- **Durum:** GUI-DOĞRULANDI (kod düzeyinde REA ile de doğrulandı → R-10)

### G-03 Sınır vektörleri (V02, V13–V16, V18, V22, V23)
- **Kanıt:** `oracle/screenshots/` ilgili PNG'ler; değerler CSV'de.
- **Bağımsız karşılaştırma:** 8/8 vektör, A-01 modeli |dz| ile çalıştırıldığında 7 basamağa kadar aynı (toplam 19/19).
- **Gözlemler:**
  1. **En küçük N = 2.** V18 (güç = α = 0.05): N=2, Df=1, actual power 0.0619486. Arama N=2'den başlıyor; N=1 hiç denenmiyor/gösterilmiyor. (A-03 desteklendi.)
  2. **Büyük etkide N küçük ama ≥ 2:** V15 dz=3 → N=4 (N=3'te güç 0.7453 < 0.80); V16 dz=5, güç .95 → N=3. Actual power hedefin çok üstünde olabilir (0.967), çünkü N tamsayı.
  3. **Çok küçük etkide süre sorunu yok:** V14 dz=0.01 → N=78491, ekran donmadı (öğrenci beyanı). Arama yöntemi (doğrusal/ikili) GUI'den anlaşılamıyor → REA.
  4. **Negatif dz simetrik:** V22 (iki kuyruk, dz=−0.5) ve V23 (tek kuyruk, dz=−0.5) pozitif karşılıklarıyla (V01, V03) aynı N ve aynı actual power veriyor. Ancak ekranda **δ ve critical t negatif işaretle** gösteriliyor (−2.9154759, −2.0345153). Tek kuyrukta negatif dz, "negatif yöndeki" testi temsil ediyor; güç α'nın altına düşmüyor. → H-08
  5. **Güç = α kabul ediliyor** (V18): koşul "power ≥ alpha".
- **Durum:** GUI-DOĞRULANDI

### G-04 Hata mesajları (V19, V21, V24, V25, V26)
Hepsi "Input error" başlıklı bir pencere; çıktı alanları "?" kalıyor. Metinler birebir:
| Vektör | Girdi | Mesaj |
|---|---|---|
| V19 | power 0.04 < α 0.05 | `Power must be greater than or equal to alpha.` |
| V21 | dz = 0 | `In an a priori analysis, the absolute value of the effect size be greater than 0.00001.` (orijinal metinde dilbilgisi hatası: "be") |
| V24 | α = 0 | `Alpha is outside the admissible range (1e-07, 1).` |
| V25 | α = 1 | `Alpha is outside the admissible range (1e-07, 1).` |
| V26 | power = 1 | `Power is outside the admissible range (1e-07, 1).` |
- **Çıkarımlar:** α ve güç için kabul aralığı (1e-07, 1); 1 dışlanıyor. Alt sınırın (1e-07) dahil olup olmadığı henüz sınanmadı → yeni vektör önerisi. |dz| ≤ 0.00001 a priori'de hata; tam 0.00001'in davranışı sınanmadı.
- **Bu dizeler REA için çok iyi hedef:** binary'de `admissible range` ve `Power must be greater` dizeleri aranıp, onlara referans veren doğrulama fonksiyonunun adresi bulunacak.
- **Durum:** GUI-DOĞRULANDI

### Veri toplama notları
- V20 One ile yeniden alındı; V17 tamamlandı (G-05).

### G-05 Post hoc ve son a priori vektörleri (V17, V20, V27–V29, V32–V34)
- **Bağımsız karşılaştırma:** V17, V20, V27, V28, V29 ve V34 → 6/6 aynı (7 basamak). Toplam hesaplı vektör: **25/25**.
- **UCLA post hoc değerleri G*Power'da doğrulandı:** V27 0.8195358 (UCLA 0.819536), V28 0.8949909 (UCLA 0.894991). D-05'teki 6 basamaklı değerler 7 basamaklının yuvarlanmışı.
- **V20 (tek kuyruk, güç = α):** N=2, actual power 0.1058229 → tek kuyrukta da en küçük N=2.
- **Önemli — modlar arasında tutarsız alt sınır:**
  - Post hoc'ta N=2 ve N=1 hata veriyor: `Total sample size is outside the admissible range (3, 2147483646)` (V32, V33).
  - Ama a priori aynı test N=2 sonucunu üretebiliyor (V18, V20).
  - Yani a priori çözücü 2'den aramaya başlıyor; post hoc girdi doğrulaması ise 3'ün altını reddediyor. N=3'ün kabul edilip edilmediği (aralık açık mı kapalı mı) bilinmiyor → V39.
  - Üst sınır 2147483646 = 2³¹ − 2 (32 bit tamsayı sınırının bir eksiği) → N içeride tamsayı olarak tutuluyor olabilir. [AJAN çıkarımı]
- **Kesirli N (V34):** 10.5 girildiğinde hata yok; sonuç tam olarak N=11 ile aynı (Df=10, δ = 0.5·√11 = 1.6583124, güç 0.3232370). N=10.5 ile karışık hesap (δ=1.6201852) ekrandakiyle tutmuyor. → G*Power kesirli N'yi tamsayıya çeviriyor. Ceil mi yuvarlama mı ayırt etmek için V38 (10.2) planlandı.
- **Durum:** GUI-DOĞRULANDI

### G-06 Kesirli N kuralı ve post hoc alt sınırı (V38, V39)
- **V38:** N=10.2 → Df=9, δ=0.5·√10=1.5811388, güç 0.2931756 → **N=10** olarak hesaplandı.
- **V34 ile birlikte:** 10.5→11, 10.2→10. Bu "en yakın tamsayıya yuvarla, .5 yukarı" kuralıyla tutarlı. Ceil (10.2→11) çürütüldü; banker's rounding (10.5→10) çürütüldü. 10.7 ya da 10.49999 gibi değerler sınanmadı. [GUI-DOĞRULANDI, kural sınırlı vektörle]
- **V39:** N=3 → hesaplandı (Df=2, güç 0.0841071). Mesajda "(3, 2147483646)" yazmasına rağmen **3 kabul ediliyor**; alt sınır dahil. Mesajdaki parantez gösterimi gerçek davranışla birebir değil.
- **Çıkarım [AJAN]:** Mesaj aralıkları "kapalı" olabilir; α ve güç için "(1e-07, 1)" mesajında da 1e-07'nin kabul edilip edilmediği ayrıca sınanmadı.
- **Bağımsız karşılaştırma:** 2/2 aynı → toplam hesaplı vektör **27/27**.
- **Durum:** GUI-DOĞRULANDI

## E-02 Analiz araçlarının kurulumu (2026-10-19)
| Bileşen | Sürüm / durum | Kanıt |
|---|---|---|
| Node.js | v24.22.0 | `oracle/screenshots/S01a_kurulum.png` |
| JDK | Temurin 21.0.12.1 (java + javac) | aynı |
| Ghidra | 12.1.4 PUBLIC, `C:\tools\ghidra_12.1.4_PUBLIC`; indirilen `ghidra_12.1.4_PUBLIC_20260921.zip` SHA-256: `DDAC49F903DA9D5BAC833E5CC79395098B9C33CFD3279BE5F31BD00387D2D4DB` (release sayfasında yayımlanan değerle aynı) | Kurulum yolu ve sürüm: `rea_notes/doctor_ghidra.json` (`ghidra_12.1.4_PUBLIC`); REA oturumu da sürümü 12.1.4 olarak bildirdi (`rea_notes/REA_BULGULAR.md`). Zip hash'i `Get-FileHash` ile yeniden hesaplandı (2026-10-26). |
| REA (rea-agents) | CLI 6.7.0, skill 42, `npx rea-agents@latest` (resmi npm paketi) | `rea_notes/doctor_claude.json`, `rea_notes/doctor_ghidra.json` |
| REA → Ghidra sağlayıcısı | configured=true, available=true, version 12.1.4, analyzeHeadless ve native decompiler bulundu | `doctor_ghidra.json` → providerInspections[0] |
| REA → Claude masaüstü kaydı | registration state = aligned, healthy = true | `doctor_claude.json` |
| İncelenecek kopya | `C:\rea-work\GPowerNT.exe` (OneDrive dışında yerel kopya) | — |
| REA kontrol sorusu | Claude Code (öğrencinin bilgisayarında, `C:\rea-work`): "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" → Evet; Ghidra 12.1.4 available, analyzeHeadless + decompile.exe bulundu, JDK 21 | `oracle/screenshots/S01_rea_kontrol.png`, `rea_notes/doctor_claude_code.json` |
| Bulut sohbetleri | Claude masaüstündeki sohbetler (bu dahil) REA'ya erişemedi → H-10 | — |
- **Not:** `environment_healthy=false` yalnızca kurulmayan isteğe bağlı motorlardan (Hopper, IDA, JADX, Kuna) ve REA'nın kayıt yapılmayan diğer istemcilerden (VS Code, Gemini CLI vb.) kaynaklanıyor. IDA ticari lisanslı olduğu için ödev kuralına göre kullanılmayacak.

### G-07 REA iddialarının GUI ile sınanması (V40–V43)
| Vektör | Girdi | G*Power | REA iddiası | Sonuç |
|---|---|---|---|---|
| V40 | a priori, dz=20.1 | `Effect size d is outside the admissible range (-20, 20).` | R-07: dz ∈ [−20, 20], mesaj önekinde "d" | ✔ Doğrulandı (mesajda "dz" değil "d" yazıyor — REA bunu da öngörmüştü) |
| V43 | a priori, dz=20 | N=2, güç 0.9735240, δ=28.2842712 | R-07: uç dahil | ✔ |
| V41 | a priori, α=0.0000001 | N=167, güç 0.8048331, t_c=5.5716539 | R-02: 1e-07 dahil | ✔ |
| V42 | post hoc, N=2.6 | Hesaplandı; Df=2 (N=3) | R-15 + R-05: önce floor(x+0.5), sonra [3, …] kontrolü | ✔ |
- **Bağımsız karşılaştırma:** 3/3 hesaplı vektör 7 basamağa kadar aynı → toplam **30/30**.
- **Sayısal tuzak (H-11):** scipy `nct.cdf(−t_c)` (iki kuyrukta alt kuyruk) büyük δ'da NaN döndürüyor. Doğru değer ≈0. "NaN → 1" varsayımıyla V41 için N=95 bulunuyordu; G*Power 167 diyor. Düzeltme: alt kuyruk NaN ise 0.
- **Durum:** GUI-DOĞRULANDI; R-02, R-07, R-15 artık GUI ile de destekli.

---

## [DOK] satırları

### D-01 [DOK] Ödev kapsamı ve modlar
- **Kaynak:** `2026-10-16-odev-supp` ("Test aileleri", "Modlar")
- **İçerik:** K2 = "t testi, eşleştirilmiş ortalama (önce ve sonra tansiyon)". Modlar: a priori (N hesapla) ve post hoc (gücü hesapla).
- **Grup ataması:** `Ogrenciler_gruplar.pdf` → Grup 8 = K2 (Elif Hazar, Grup 8 üyesi).

### D-02 [DOK] CLI sözleşmesi (yalnızca t2-indep örneği verilmiş)
- **Kaynak:** ödev belgesi, "a) CLI SÖZLEŞMESİ"
- **İçerik:** tek satır JSON çıktı; geçersiz girdide `{"error":"<açıklama>"}` ve sıfırdan farklı çıkış kodu. Komut adı `gpower-clone`, `--test`, `--mode a-priori`, `--tails`, `--alpha`, `--power` bayrakları t2-indep örneğinde var.
- **Eksik:** Ödev metni t-paired parametre adları için `CONTRACT.md`'ye bağlantı veriyor; hocaya göre böyle bir dosya yok (2026-10-19). Adlar t2-indep örneğinden türetildi → H-01, SPEC §3.

### D-03 [DOK] Tolerans
- **Kaynak:** ödev belgesi, "e) TOLERANS"
- N TAM eşleşmeli; diğer değerler G*Power'ın ekranda gösterdiği basamak sayısına kadar.

### D-04 [DOK] A priori'de N yukarı yuvarlanır (genel kural)
- **Kaynak:** G*Power 3.1 kılavuzu (1 Mart 2017), Bölüm 1.2.3 — oir.umh.es kopyası üzerinden okundu. Kesirli örneklem büyüklükleri her zaman yukarı yuvarlanır; bu yüzden "actual power" çoğu zaman istenen gücün biraz üstündedir.
- **Sınırlama:** Genel kural; t-paired'e özgü uygulaması [REA] ile gösterilmeli. Ödev belgesi de "kütüphaneler N'yi kesirli verir, G*Power yukarı yuvarlar" diyor.
- **Not:** Kılavuzun matched-pairs bölümü (TOC: Bölüm 18, s. 45) bu oturumda okunamadı; öğrenci resmi kılavuzdan okumalı. → H-03 *(Kapandı: resmi sayfadaki 2023 kılavuzunun Bölüm 19'u okundu → D-07.)*

### D-05 [DOK] Yayımlanmış G*Power çıktıları (ikincil kaynak)
- **Kaynak:** UCLA OARC, "Power analysis for paired sample t-test" (G*Power ekran görüntülerine dayalı ders sayfası). *Kılavuz değil; G*Power arayüzünde yeniden üretilmeden kâhin sayılmaz.*

| Girdi | Yayımlanmış sonuç |
|---|---|
| a priori, dz=1, α=0.05, güç=0.80 | N=10 |
| aynı, güç=0.85 / 0.90 | N=12 / N=13 |
| aynı, α=0.01, güç=0.9107 | N=19 |
| post hoc, dz=0.5, N=35, iki kuyruk / tek kuyruk | güç 0.819536 / 0.894991 |
| grup parametreleri: sd 10/10, r=0.9, fark 5 → dz | dz=1.118034, N=9 |
| grup parametreleri: sd 7/12, r=0.5, fark 5 | N=37 |

- **Çıkarılan sonuç:** G*Power güç değerini en az 6 ondalıkla gösteriyor (0.819536). dz'nin σ_fark = √(σ₁²+σ₂²−2ρσ₁σ₂) ile hesaplandığı bu sayılarla tutarlı. → A-02

### D-06 [DOK] Bireysel çalışma serbest
- **Kaynak:** ödev belgesi ("Takım: En fazla 4 kişi (bireysel çalışma serbest)") ve ders kaydı dökümü (öğrencinin yüklediği metin, ~[60:00] civarı: dört kişilik takımlar belirlendiği, bireysel çalışmanın da serbest olduğu söyleniyor).
- **Sonuç:** Elif Hazar K2'yi bireysel yapıyor; hoca onayladı (2026-10-19, öğrencinin bildirimi). İki ayrı oturum kuralı iki ayrı sohbetle karşılanacak.
- **2026-10-19:** Öğrencinin bildirdiğine göre hoca bireysel çalışmayı kabul etti.
- **Not:** Ders kaydı CONTRACT.md değildir; CONTRACT.md hiç yok (H-01).

### D-07 [DOK] Kılavuzun matched-pairs bölümü (birincil kaynak)
- **Kaynak:** G*Power 3.1 kılavuzu (June 1, 2023), resmi sayfadan (psychologie.hhu.de) indirildi; Bölüm 19 "t test: Means - difference between two dependent means (matched pairs)", s. 48–49. (D-04'teki 2017 kopyasında bu bölüm Bölüm 18 olarak geçiyordu ve okunamamıştı → H-03.)
- **İçerik:** dz = |µx − µy| / √(σx² + σy² − 2ρxy σxσy); H0 dağılımı t(N−1, 0), H1 dağılımı t(N−1, δ), δ = dz√N. Örnek (§19.3, Cohen 1969 s. 48): post hoc, iki kuyruk, dz=0.421637, α=0.05, N=50 → δ 2.981424, kritik t 2.009575, df 49, güç 0.832114; aynı örnek dz=0.2828427 ile güç 0.500352.
- **Kılavuzda OLMAYANLAR:** N araması (başlangıç, yöntem, durma koşulu), kesirli N'nin yuvarlanması, girdi aralıkları ve hata mesajları kılavuzda yok → bunlar [REA] satırlarıyla gösterildi (R-02…R-07, R-12, R-15).
- **Karşılaştırma:** İki örnek `oracle/manual_vectors.csv`'ye eklendi; `tests/test_manual.py` 2/2 (kılavuzun 6 ondalığına kadar aynı).
- **Durum:** KAPANDI (A-01 ve D-05 birincil kaynakla da desteklendi)

---

## [AJAN] satırları (oturum başındaki hipotezler — her birinin kapanışı altında)

### A-01 [AJAN] Hesap modeli
- **İddia:** t-paired, tek-örneklem t testinin farklar üzerinde uygulanmasıdır: N = çift sayısı, df = N − 1, ncp δ = dz·√N, kritik t = t⁻¹(1−α/kuyruk; df), güç noncentral t'den.
- **Kanıt düzeyi:** Kanıt yok. Ancak D-05'teki 7 yayımlanmış sayının 7'si bu modelle (scipy) birebir tuttu → `tools/library_check.py`.
- **Tekrar üretme:** `python3 -I tools/library_check.py`
- **Belirsizlik:** İki kuyrukta alt kuyruk olasılığı (P(T' < −t_c)) toplanıyor mu? → GUI'de evet (G-02: V03 vs V11). REA ile kod düzeyinde gösterilecek.
- **Durum:** KAPANDI — 30/30 GUI vektörü (G-01…G-07) ve REA (R-08 df, R-09 δ, R-10 alt kuyruk) ile doğrulandı. İki kuyrukta alt kuyruk ekleniyor.

### A-02 [AJAN] dz'yi "Determine" penceresi hesaplar, motor yalnızca dz alır
- **İddia:** Ana hesap yalnızca dz'ye bakar; grup parametreleri (ortalamalar, SD'ler, r) yalnızca yardımcı penceredir.
- **Durum:** KAPSAM DIŞI (bilinçli karar). CLI yalnızca dz alır; ortalama/SD/korelasyondan dz hesaplayan yardımcı pencere uygulanmadı (SPEC §3). REA ile incelenmedi.

### A-03 [AJAN] N araması N=2'den başlar, ilk güç ≥ hedef değerinde durur
- **İddia:** Minimum N = 2 (df=1). Durma koşulu "güç ≥ hedef".
- **Belirsizlik:** G*Power ikili arama mı, doğrusal arama mı yapıyor? Eşitlik (güç tam hedefe eşit) nasıl ele alınıyor? Çok büyük dz'de minimum N 2 mi 3 mü? → V15–V17, REA.
- **Durum:** KAPANDI — REA R-12: arama sürekli N üzerinde Brent kök bulucu + yukarı yuvarlama, alt sınır 2 (doğrusal arama değil). Sonuç "güç ≥ hedef olan en küçük N" ile aynı: 23/23 a-priori vektör.

### A-04 [AJAN] Negatif dz
- **İddia:** İki kuyrukta |dz| kullanılır; tek kuyrukta negatif dz güç < α verebilir veya hata verilebilir.
- **Durum:** ÇÜRÜTÜLDÜ (tek kuyruk kısmı) — V23: tek kuyrukta negatif dz ayna gibi davranıyor, güç α'nın altına düşmüyor. → HALLUCINATIONS H-08, REA R-16.

### A-05 [AJAN] Geçersiz girdi davranışı
- **İddia:** α ∉ (0,1), güç ∉ (0,1), dz = 0, güç ≤ α durumlarında G*Power bir hata/uyarı gösterir.
- **Durum:** KAPANDI — G-04, G-07 ve REA R-02…R-07: 8 hata vektörünün mesajları birebir kayıtlı.

---

## [REA] satırları
Kaynak: `rea_notes/REA_BULGULAR.md` (Claude Code + REA 6.7.0 + Ghidra 12.1.4, 2026-10-19; prompt: `prompts/oturum1_rea_gorevi.md`).
Binary: GPowerNT.exe 3.1.9.7, SHA-256 C63E6A13…EFC812 (E-01; REA oturumu hash'i yeniden doğruladı). Adresler sanal adres, image base 0x400000.
"Doğrulama" sütunu, bulgunun bu oturumda GUI vektörleriyle ya da bağımsız hesapla nasıl sınandığını gösterir.

| ID | Davranış | Konum (adres) | Sonuç | Doğrulama |
|---|---|---|---|---|
| R-01 | Matched pairs ayrı bir sınıf (`PowerTPairedMean`), tek örneklem t (`PowerTOneMean`) sınıfından türüyor | vtable 0x5cac60; ad fonk. FUN_004dcf10 → dize 0x5cb56c; Calculate FUN_004dc2a0 | Hesap tek-örneklem t üzerinden; t2-indep kodu değil | — |
| R-02 | α kontrolü: `1e-07 ≤ α ≤ 0.9999999` (uçlar dahil); mesajdaki "1" setprecision(6) yuvarlaması | FUN_00487530; dize 0x5c6100 | α=0, α=1 hata; α=1e-07 geçerli | V24, V25, V41 ✔ |
| R-03 | Güç kontrolü: aynı sabitler | FUN_00488110; dize 0x5c60d8 | güç=1 hata | V26 ✔ |
| R-04 | "power ≥ alpha": `COMISD` + `JC` → yalnızca güç < α hata; sıra: α → güç → güç≥α | FUN_004880e0; dize 0x5c6220 | güç=α geçerli | V18, V19, V20 ✔ |
| R-05 | Post hoc (ve sensitivity/criterion/compromise) N kontrolü `3 ≤ N ≤ 2147483646`; a priori dalında yok | FUN_00488a10 (`N,3,0x7ffffffe`) çağrısı FUN_004dc2a0 içinde; dize 0x5c6524 | N=1,2 hata; N=3 geçerli | V32, V33, V39 ✔ |
| R-06 | Yalnızca a priori'de `\|dz\| < 1e-05` hata (1e-05 kabul) | FUN_004db990; dizeler 0x5cb24c + 0x5cb510 | dz=0 hata; mesajdaki dil bilgisi hatası binary'de de var | V21 ✔ |
| R-07 | Tüm modlarda `−20 ≤ dz ≤ 20`; dışı "… is outside the admissible range" | FUN_004db990 → FUN_00487b70 (sabitler 0xc0340000 / 0x40340000) | dz=20.1 hata, dz=20 geçerli | V40, V43 ✔ |
| R-08 | df = ARE[0]·N − 1 = N − 1 (ARE[0]=1.0) | FUN_004db950; tablo 0x6096a8 | df = N − 1 | 30/30 GUI ✔ |
| R-09 | δ = √N · dz (sqrt, işaret korunur) | FUN_004dbdc0; çağrı 0x4d39e1 | δ = dz√N | 30/30 GUI ✔ |
| R-10 | p = α/(1+[iki kuyruk]); dz≥0: t_c=t⁻¹(1−p); iki kuyrukta güç = 1 − (F(t_c;δ) − F(−t_c;δ)) | FUN_004d38b0 (0x4d398d–0x4d39ab) | Alt kuyruk ekleniyor | V03 vs V11 ✔ (iki kuyruk dalı yalnızca decompiler kanıtı) |
| R-11 | Noncentral t CDF programın kendi seri implementasyonu (yakınsama 5.55e-17, ≤50000 terim) | FUN_004fa7e0 → FUN_004f9fa0; vtable 0x5c4a20 | Harici DLL yok | scipy ile 7 basamak uyumu ✔ |
| R-12 | A priori arama: f(N)=güç(N)−hedef, N **sürekli**; aralık [2,100], üst sınır ×1.6 ile genişler; Brent (tol 1e-10, ≤300 iter); sonra `N = ceil(floor(x·1e10+0.5)/1e10)`, N<2 → 2 | FUN_00496aa0, FUN_004968d0, FUN_004962d0, FUN_004f9bb0, FUN_00496a20 | En küçük tamsayı N, güç ≥ hedef | Bu yöntemin taklidi 23/23 a priori GUI vektörüyle aynı (V41 ve V43 dahil); 400 rastgele girdide doğrusal aramayla aynı ✔ |
| R-15 | Post hoc N metinden okunurken `floor(x+0.5)` | FUN_0048b8d0 (FUN_0048ab70 üzerinden) | .5 yukarı yuvarlama, aralık kontrolü yuvarlanmış değerle | V34, V38, V42 ✔ |
| R-16 | Negatif dz: abs yalnızca doğrulamada; dz<0 iken t_c = t⁻¹(p) < 0, δ < 0; nct CDF simetriyle çeviriyor | FUN_004d38b0 @ 0x4d3956; FUN_004dbdc0 | δ ve t_c negatif, N ve güç \|dz\| ile aynı | V22, V23 ✔ |
| R-17 | Matched pairs'e özgü kod: df, δ, etki doğrulama, Calculate, ad; gerisi paylaşılan | 8 vtable'da FUN_004d38b0 | — | — |
| R-18 | A priori alt sınırı 2, post hoc alt sınırı 3 (tutarsızlık koddan geliyor) | FUN_0049a210, FUN_00496aa0, FUN_004dc2a0 | — | V18 + V32 ✔ |

[AJAN] olarak bırakılanlar (REA oturumunun kendi etiketi): R-13 (güç=α'da N=2'nin alt sınır sıkıştırmasından geldiği), R-14 (dz=0.01'de iterasyon sayısı tahmini).
