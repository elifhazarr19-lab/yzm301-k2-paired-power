# HALLUCINATIONS.md — Halüsinasyon ve Belirsizlik Günlüğü (K2 · t-paired)

> Ödev şartı: ajanın yanlış çıkardığı **en az 2 şey**, nasıl fark edildiği, hangi testin yakaladığı.
> Durum (son sürüm, 2026-10-19): kanıtlanmış yanlış varsayım / çelişki sayısı **7** (H-01 güncelleme 2, H-07, H-08, H-09, H-10, H-11, H-12). **Açık madde kalmadı.** Bölümler:
> - **KARAR / BİLGİ:** kanıtla kapatılamayan, gerekçeli kararla kapatılan maddeler (H-01, H-02, H-03, H-06).
> - **DOĞRULANDI:** ajanın varsayımı G*Power ve REA ile doğru çıktı (H-04, H-05).
> - **ÇÜRÜTÜLDÜ:** ajanın varsayımı yanlış çıktı ya da belgede çelişki bulundu (H-07 … H-12).

## Kayıt şablonu
```
### H-xx <başlık>
- Tür: Doğrulanmamış varsayım | Yanlış varsayım | Çelişki | Eksik kanıt
- Ajanın iddiası:
- Neden şüpheli:
- Nasıl fark edildi:
- Yakalayan test / vektör:
- Doğru davranış (kanıtıyla):
- LEDGER / SPEC'te yapılan değişiklik:
- Durum: AÇIK | KARAR | DOĞRULANDI | ÇÜRÜTÜLDÜ
```

## KARAR / BİLGİ

### H-01 CONTRACT.md eksik → yok
- **Tür:** Eksik kanıt / ajanın yanlış varsayımı
- **Durum bilgisi:** Ödev belgesi t-paired parametre adları için CONTRACT.md'ye bağlantı veriyor; dosya mevcut değil.
- **Risk:** Gizli test düzeneği farklı bayrak adı kullanırsa her vektör başarısız olur → kapı (%90) kaçar.
- **2026-10-19 güncelleme 1:** Öğrencinin "CONTRACT.md bu mu?" diye yüklediği dosya ders kaydının dökümü çıktı. Dökümde "contract", bayrak adı, JSON alanı veya "t-paired" geçmiyor. Madde AÇIK kalıyor.
- **2026-10-19 güncelleme 2:** Hocadan öğrenildi: CONTRACT.md diye bir dosya yok. Ajan (Oturum 1) ödev metnindeki "[LİNK: CONTRACT.md]" ifadesinden dosyanın var olduğunu varsaymış ve istemişti. **Ders:** Belgede adı geçen bir dosyanın var olduğunu doğrulamadan varsayma.
- **Alınan karar:** Bayrak ve alan adları t2-indep örneğinden türetildi (SPEC §3, §5). `--d`/`--dz` eş anlamlı kabul edilerek risk azaltıldı.
- **Kalan risk:** Gizli test düzeneği başka bir ad kullanırsa yakalanamaz.
- **Durum:** KARAR (kanıtla doğrulanamaz)

### H-02 "t2-indep ile aynı biçim" varsayımı
- **Tür:** Doğrulanmamış varsayım
- **İddia:** JSON çıktısı t2-indep örneğiyle aynı alanları, aynı 4 basamağı kullanır.
- **Neden şüpheli:** t-paired'de n1/n2 yok; UCLA kaynağı G*Power'ın 6 basamak gösterdiğini düşündürüyor.
- **Nasıl kapandı:** V01 ekran görüntüsü G*Power'ın 7 ondalık gösterdiğini ortaya koydu (LEDGER G-01). Karar: alan adları t2-indep örneğinden alındı (`n1`/`n2` yok), çıktı ödevdeki örnek biçime uygun olarak 4 ondalık; hesap 7 ondalığa kadar doğru (SPEC §6). Diferansiyel test 30/30 satırda 7 ondalık eşleşmeyi ayrıca doğruluyor (`tests/UYUM_RAPORU.md`).
- **Durum:** KARAR (CONTRACT.md olmadığından alan adları için kesin kaynak yok)

### H-03 Kılavuz bölümü okunamadı
- **Tür:** Eksik kanıt
- **Durum bilgisi:** G*Power 3.1 kılavuzunun matched-pairs bölümü (TOC'a göre Bölüm 18) bu oturumda erişilen kopyada yer almıyordu. [DOK] satırları ikincil kaynağa (UCLA) dayanıyor.
- **Nasıl kapandı:** Kılavuzun anlatacağı hesap modeli birincil kanıtla gösterildi: 30/30 G*Power vektörü ve REA bulguları (R-08 df, R-09 δ, R-10 güç, R-12 N araması). Kılavuz bölümüne bu yüzden ihtiyaç kalmadı.
- **Durum:** KARAR (kılavuz bölümü okunmadı; birincil kanıtla ikame edildi)

### H-06 Belgeler arası küçük çelişkiler
- **Tür:** Çelişki (bilgi için)
- Ödev metni süreyi "1 hafta" diyor; slayt "2 saat ders + 48–72 saat teslim" diyor.
- Slayt halüsinasyon günlüğü için "rubrikte %20" diyor; ödev metninde 85 puandan 15 puan (~%17.6).
- **Durum:** BİLGİ (iki belge arasındaki fark yalnızca kayıt için not edildi)

## DOĞRULANDI (ajanın varsayımı doğru çıktı)

### H-04 Hesap modeli (df = N−1, δ = dz√N)
- **Tür:** Doğrulanmamış varsayım (LEDGER A-01)
- **Lehte (başlangıçta):** 7 yayımlanmış sayının 7'si tuttu.
- **Aleyhte risk (başlangıçta):** Yayımlanmış sayılar az ve "kolay" bölgeden; sınırlarda (dz çok küçük/büyük) sapma olabilirdi.
- **Nasıl sınandı:** Sınır vektörleri V13–V17, V22–V23, V40–V43 dahil 30 hesaplı G*Power vektörü; REA'da df ve δ hesap blokları.
- **Sonuç:** 30/30 vektör 7 ondalığa kadar aynı. REA: df = N − 1 (R-08, FUN_004db950), δ = dz·√N (R-09, FUN_004dbdc0), iki kuyrukta alt kuyruk ekleniyor (R-10).
- **Durum:** DOĞRULANDI

### H-05 Minimum N ve durma koşulu
- **Tür:** Doğrulanmamış varsayım (LEDGER A-03)
- **Nasıl sınandı:** V15–V17 (büyük dz), V18–V20 (güç ≤ α) ve REA'da a priori arama fonksiyonu.
- **Sonuç:** En küçük N = 2 (V18, V20). Arama doğrusal değil: sürekli N üzerinde Brent kök bulucu, ardından yukarı yuvarlama ve N < 2 ise 2 (R-12). Sonuç "güç ≥ hedef olan en küçük N" ile aynı: 23/23 a priori vektör.
- **Durum:** DOĞRULANDI

## ÇÜRÜTÜLDÜ

### H-12 SPEC içinde eski sayı (çelişki)
- **Tür:** Çelişki — inceleme oturumunun kendi belgesinde
- **İddia:** SPEC §7 sonunda "Tam vektör listesi (27 hesaplı + 7 hatalı)" yazıyordu; aynı belgenin başında ve CSV'de 30 hesaplı + 8 hatalı var.
- **Nasıl fark edildi:** Yazım oturumu (Oturum 2) CSV ile SPEC'i karşılaştırırken bildirdi.
- **Yakalayan test:** Diferansiyel testin satır sayımı (38 = 30 + 8).
- **Düzeltme:** SPEC §7 sonundaki cümle "30 hesaplı + 8 hatalı" olarak düzeltildi; `tests/UYUM_RAPORU.md`'deki not da "düzeltildi" olarak güncellendi. Etkisi yok (hesap kuralı değil, yalnızca sayım).
- **Durum:** ÇÜRÜTÜLDÜ (çelişki bulundu ve düzeltildi)

### H-11 "scipy nct NaN verirse güç ≈ 1'dir" varsayımı (SPEC v0.9'a yazılmıştı)
- **Tür:** Yanlış varsayım — ajan (Oturum 1) kendi SPEC'ine yanlış bir sayısal kural yazdı
- **Ajanın iddiası:** "scipy.stats.nct büyük δ'da NaN döndürebilir; güç bu bölgede pratikte 1'dir; NaN → 1.0."
- **Gerçek:** NaN, iki kuyruklu gücün **alt kuyruk** terimi `nct.cdf(−t_c)`'den geliyor; doğru değeri ≈0 (ör. 1e-16 mertebesi). Üst kuyruk `nct.sf` doğru sonuç veriyor. NaN → 1 kuralı gücü yapay olarak 1 yapıyor ve N aramasını erken bitiriyordu.
- **Nasıl fark edildi:** V41 (α=1e-07) için G*Power N=167 verdi; bağımsız hesap NaN → 1 kuralıyla N=95 buldu. Değerler tek tek yazdırılınca NaN'ın alt kuyruktan geldiği görüldü.
- **Yakalayan test:** REA iddiasını sınamak için eklenen sınır vektörü V41 (ve V43: dz=20).
- **Düzeltme:** SPEC §5.3: alt kuyruk NaN ise 0 kabul edilir. Düzeltilmiş hesap 30/30 vektörde 7 basamak uyumlu.
- **Ders:** Sayısal "güvenlik" kuralları da kanıtla sınanmalı; sınır vektörleri burada iki işe yaradı.
- **Bağımsız teyit (Oturum 2, 2026-10-19):** statsmodels `TTestPower` aynı NaN sorununa düşüyor: 1000 kütüphane vektörünün 81 post-hoc satırında NaN, 9 a-priori satırında yanlış kök (ör. L-A046: statsmodels 7.48 → ceil 8; doğru N=10). Bkz. `tests/UYUM_RAPORU.md`.
- **Durum:** ÇÜRÜTÜLDÜ

### H-10 "REA, Claude masaüstüne kurulursa bulut sohbetinden kullanılabilir" varsayımı
- **Tür:** Doğrulanmamış varsayım → yanlış çıktı
- **Ajanın iddiası:** REA `--client claude_desktop` ile kurulursa, öğrencinin bilgisayarına bağlı bu sohbetten REA araçları kullanılabilir.
- **Gerçek:** Kurulum sağlıklı (doctor: healthy=true, claude_desktop=aligned) ama bu oturumda yerel MCP sunucusu listesi boş ve araç aramasında REA çıkmadı. Claude masaüstünde açılan yeni sohbet de Linux bulut ortamında çalıştığını ve REA/Ghidra aracının olmadığını bildirdi.
- **Nasıl fark edildi:** Ödevin kontrol sorusu ("REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?") iki ayrı sohbette soruldu; ajan `get_device_info` ve araç aramasıyla doğruladı.
- **Yakalayan test:** README kontrol sorusu.
- **Düzeltme:** REA, öğrencinin bilgisayarında yerel çalışan bir ajan istemcisiyle (Claude Code) kullanılacak.
- **Durum:** ÇÜRÜTÜLDÜ

### H-09 "Post hoc'ta N ≥ 2 geçerlidir" varsayımı
- **Tür:** Yanlış varsayım (SPEC §3 tablosu: "N (post-hoc): tamsayı ≥ 2 ?")
- **Ajanın iddiası:** a priori'de en küçük N=2 olduğu için post hoc'ta da N=2 kabul edilir; vektör listesinde V32 "SINIR en küçük N (df=1)" diye planlandı.
- **Gerçek:** Post hoc'ta N=2 hata veriyor: "Total sample size is outside the admissible range (3, 2147483646)". A priori ise N=2 sonucunu üretebiliyor (V18). İki mod farklı alt sınır kullanıyor.
- **Nasıl fark edildi:** V32 ekran görüntüsü.
- **Yakalayan test:** Sınır vektörü V32 (ve V33).
- **Düzeltme:** SPEC'te post hoc için N < 3 hata; a priori arama N=2'den başlıyor. V39 ile N=3'ün kabul edildiği (alt sınırın dahil olduğu) gösterildi; REA bunu kod düzeyinde doğruladı (R-05: `3 ≤ N ≤ 2147483646`).
- **Durum:** ÇÜRÜTÜLDÜ

### H-08 Negatif dz tek kuyrukta "güç < α" verir varsayımı
- **Tür:** Yanlış varsayım (LEDGER A-04)
- **Ajanın iddiası:** "İki kuyrukta |dz| kullanılır; tek kuyrukta negatif dz güç < α verebilir veya hata verilebilir."
- **Gerçek:** G*Power tek kuyrukta da negatif dz'yi ayna gibi ele alıyor: V23 (dz=−0.5, tek kuyruk) → N=27, actual power 0.8118316, V03 (dz=+0.5) ile aynı. Yalnızca δ ve critical t negatif gösteriliyor.
- **Nasıl fark edildi:** V23 ekran görüntüsü, V03 ile karşılaştırıldı.
- **Yakalayan test:** Sınır vektörü V23.
- **Düzeltme:** SPEC'te hesap |dz| ile yapılır; çıktıdaki `critical` ve `ncp` işareti dz'nin işaretini alır.
- **Durum:** ÇÜRÜTÜLDÜ

### H-07 Binary'nin adı "GPower.exe" değil
- **Tür:** Belge ile gerçek arasında çelişki (ajan da ödev metnindeki adı tekrarlamıştı)
- **İddia:** Ödev metni ve ajanın ilk talimatları programın adını `GPower.exe` olarak verdi; ajan kurulum dosyası olacağını ve `C:\Program Files\G*Power\` altına kurulacağını varsaydı.
- **Gerçek:** Resmi 3.1.9.7 Windows paketinde kurulum dosyası yok; program `GPowerNT.exe`. Ayrıca Windows klasör adlarında `*` karakteri kullanılamaz, yani ajanın verdiği örnek yol baştan geçersizdi.
- **Nasıl fark edildi:** Öğrenci paketi açtığında kurulum dosyası bulamadı ve klasörün ekran görüntüsünü paylaştı.
- **Yakalayan test:** Elle kurulum adımı (Adım 3).
- **Düzeltme:** Hash `GPowerNT.exe` için alındı (LEDGER E-01). README'de iki ad birlikte anılacak; `.gitignore` tüm `*.exe` dosyalarını dışarıda tutuyor.
- **Durum:** ÇÜRÜTÜLDÜ

