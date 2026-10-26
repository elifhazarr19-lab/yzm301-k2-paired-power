# REA Bulguları — K2 / t testi, eşleştirilmiş örneklem (matched pairs)

- **Hedef:** `C:\rea-work\GPowerNT.exe` (G*Power 3.1.9.7, PE x86, 2 287 616 bayt)
- **Hash doğrulama:** SHA-256 `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` → **TUTTU** (PowerShell `Get-FileHash` ve REA `open_binary` aynı değeri verdi)
- **Araçlar:** REA (`rea-agents`) 6.7.0, Ghidra 12.1.4 (headless, varsayılan auto-analysis), Claude Code 2.1.303
- **Analiz tarihi:** 2026-10-19
- **Yöntem:** Yalnızca statik inceleme. Binary çalıştırılmadı, değiştirilmedi. Ghidra PDB yüklemedi; fonksiyon adları `FUN_xxxxxxxx` biçiminde. Sınıf adları Ghidra'nın RTTI'den çıkardığı vtable etiketleri.
- **Adres notu:** Tüm adresler sanal adres (image base 0x400000).
- **Sonradan yapılan GUI doğrulaması (aynı gün):** Bu rapordaki açık noktalar G*Power arayüzünde ayrıca sınandı (LEDGER G-07): R-07 (V40 dz=20.1 hata, V43 dz=20 geçerli), R-02 (V41 α=1e-07 geçerli), R-15 (V42 post hoc N=2.6 → N=3). Aşağıdaki bulgu metinleri REA oturumunun ilk çıktısıdır; bu doğrulamalar ilgili maddelere "Sonradan" notu olarak eklendi.

---

## R1 — Dize tablosu

| Dize (parça) | Dize adresi | Xref (talimat) → fonksiyon |
|---|---|---|
| `Power must be greater than or equal to alpha.` | 0x5c6220 | 0x4880f9 → **FUN_004880e0** |
| `Alpha is outside the admissible range (` | 0x5c6100 | 0x4874ec → FUN_00487460 ; 0x4875b4 → **FUN_00487530** |
| `Power is outside the admissible range (` | 0x5c60d8 | 0x48809c → FUN_00488010 ; 0x488194 → **FUN_00488110** |
| `Total sample size is outside the admissible range (` | 0x5c6524 | 0x488a3c → **FUN_00488a10** |
| `In an a priori analysis, the absolute value of the\n` | 0x5cb24c | 6 xref; matched pairs için 0x4db9c2 → **FUN_004db990** |
| `effect size be greater than 0.00001.` | 0x5cb510 | 0x4db9b7 → **FUN_004db990** ; 0x4da5f7 → FUN_004da5d0 (regresyon) |
| `Means: Difference between two dependent means (matched pairs)` | 0x5cb56c | 0x4dcf4a → **FUN_004dcf10** (test adı döndürür) |
| `Effect size dz` | 0x5c5ba0 | 0x609540 (veri tablosu; koddan doğrudan xref yok) |
| `Noncentrality parameter $\delta$` | 0x5c567c | xref bulunamadı |
| `Total sample size` (alan adı) | 0x5c54e0 | 49 xref; bunlardan biri 0x6093c8 = alan-adı tablosu `0x6093c0[2]` |

Not: Hata mesajlarındaki sayılar (`1e-07`, `1`, `3`, `2147483646`) dizenin içinde yazılı değil. Çalışma anında `ostream <<` ile ekleniyorlar (bkz. R-02, R-05).

---

### R-01 [REA] Matched pairs sınıfı: `PowerTPairedMean`, vtable 0x5cac60
- Görev: R1 / R3
- Konum: vtable 0x5cac60 ; klon fonksiyonu FUN_004dc9d0 @ 0x4dc9d0 ; ad fonksiyonu FUN_004dcf10 @ 0x4dcf10 → dize @ 0x5cb56c ; Calculate FUN_004dc2a0 @ 0x4dc2a0 (vtable +0xc8)
- Gözlem: FUN_004dc9d0 içinde `*puVar2 = PowerTPairedMean::vftable;` yazıyor. Temel sınıf kurucusu FUN_004db820, önce `PowerT::vftable` (0x5ca2d8), sonra `PowerTOneMean::vftable` (0x5ca8d0) atıyor. FUN_004dc2a0, `switch(analiz tipi)` ile 5 dala ayrılıyor: 0 = a priori (vtable+0x48), 1 = sensitivity (+0x28), 2 = post hoc (+0x30), 3 = criterion (+0x38), 4 = compromise (+0x40).
- Sonuç: Matched pairs testi, tek örneklem t testinden (`PowerTOneMean`) türeyen ayrı bir sınıf. Hesap fonksiyonlarının çoğunu üst sınıflardan devralıyor.
- Destekleyen GUI gözlemi: G1–G7 (genel çerçeve)
- Güven: yüksek
- Açık kalan: 0x5cab30'daki benzer vtable **Linear multiple regression** sınıfına ait (ad fonksiyonu 0x4dada0). İlk taramada karıştırılabilir; matched pairs'e ait değil.

### R-02 [REA] Alfa aralık kontrolü: iki uç dahil, üst sınır aslında 0.9999999
- Görev: R2
- Konum: FUN_00487530 @ 0x487530 (Calculate'ten çağrılan sürüm) ; dize "Alpha is outside the admissible range (" @ 0x5c6100
- Gözlem: `if ((1e-07 <= param_1) && (param_1 <= 0.9999999)) return 1;`. Hata durumunda `std::setprecision(6)` ile `1e-07` ve `0.9999999` yazdırılıyor. 6 anlamlı basamakta 0.9999999 ekrana "1" olarak çıkıyor.
- Sonuç: α, ancak 1e-07 ≤ α ≤ 0.9999999 ise kabul ediliyor. Mesajdaki "(1e-07, 1)" gösterimi yuvarlanmış; iki uç da kodda dahil.
- Destekleyen GUI gözlemi: G7 (α=0 ve α=1 reddediliyor)
- Güven: yüksek
- Açık kalan: FUN_00487460 @ 0x487460 aynı kontrolün vtable üzerinden çağrılan ikizi (önce vtable+0xf8'i çağırıyor). Matched pairs Calculate akışında doğrudan çağrılmıyor.

### R-03 [REA] Güç aralık kontrolü: alfa ile aynı sabitler
- Görev: R2
- Konum: FUN_00488110 @ 0x488110 ; ikizi FUN_00488010 @ 0x488010 ; dize @ 0x5c60d8
- Gözlem: Gövde R-02 ile aynı: `1e-07 <= p && p <= 0.9999999`. Mesaj aynı biçimde `setprecision(6)` ile yazdırılıyor.
- Sonuç: Güç = 1 reddediliyor, çünkü 1 > 0.9999999. Mesajdaki "1" de aslında 0.9999999.
- Destekleyen GUI gözlemi: G7 (güç=1)
- Güven: yüksek
- Açık kalan: —

### R-04 [REA] "Power ≥ alpha" kontrolü: eşitlik kabul ediliyor
- Görev: R2
- Konum: FUN_004880e0 @ 0x4880e0 ; dize @ 0x5c6220
- Gözlem: `MOVSD XMM0,[ESP+0xc]` (güç), `COMISD XMM0,[ESP+0x4]` (α), `JC hata`. Hataya yalnızca güç < α (CF=1) iken gidiliyor. Çağrı sırası (FUN_004dc2a0, a priori dalı): α kontrolü → güç kontrolü → güç≥α kontrolü.
- Sonuç: Güç = α geçerli bir girdi; yalnızca güç < α hata veriyor.
- Destekleyen GUI gözlemi: G3 (güç=α=0.05 kabul edildi), G7
- Güven: yüksek
- Açık kalan: —

### R-05 [REA] Toplam örneklem kontrolü: 3 ≤ N ≤ 2147483646, iki uç dahil
- Görev: R2
- Konum: FUN_00488a10 @ 0x488a10 ; çağrı FUN_004dc2a0 @ 0x4dc2a0 ; dize @ 0x5c6524
- Gözlem: Matched pairs Calculate'in 1–4 numaralı dallarında `FUN_00488a10(N, 3, 0x7ffffffe)` çağrılıyor (0x7ffffffe = 2147483646). FUN_00488a10: `if ((lo <= N) && (N <= hi)) return 1;`, aksi halde lo ve hi tamsayı olarak mesaja ekleniyor.
- Sonuç: Post hoc, sensitivity, criterion ve compromise analizlerinde N ∈ [3, 2147483646]. A priori dalında bu kontrol yok.
- Destekleyen GUI gözlemi: G7 (N=1 ve N=2 reddedildi, N=3 kabul edildi)
- Güven: yüksek
- Açık kalan: FUN_00488a10'un 99 çağrı noktası var; diğer testler başka alt sınırlar veriyor (örneğin regresyon `(int)(k+2)`).

### R-06 [REA] Etki büyüklüğü (a priori): |dz| < 0.00001 kesin eşitsizlikle reddediliyor
- Görev: R2 / R6
- Konum: FUN_004db990 @ 0x4db990 (PowerTPairedMean vtable+0x104) ; dizeler @ 0x5cb24c + @ 0x5cb510
- Gözlem: `if ((param_1 == 0) && (ABS(dz) <= 1e-05 && ABS(dz) != 1e-05))` → mesaj. param_1, analiz tipi; 0 = a priori. Mesaj iki ayrı dizenin birleştirilmesiyle oluşuyor.
- Sonuç: Yalnızca a priori'de |dz| < 1e-05 hata veriyor. |dz| = 1e-05 kabul ediliyor; post hoc'ta dz=0 bu kontrole takılmıyor.
- Destekleyen GUI gözlemi: G7 (dz=0)
- Güven: yüksek
- Açık kalan: GUI'de `in ... size be greater` ifadesindeki dil bilgisi hatası binary'deki dizeyle birebir aynı ("must" kelimesi eksik).

### R-07 [REA] Ek bulgu: dz için [−20, 20] aralık kontrolü
- Görev: R2
- Konum: FUN_004db990 @ 0x4db990 → FUN_00487b70 @ 0x487b70 ; dize " is outside the admissible range (" @ 0x5c61d8
- Gözlem: `FUN_00487b70(100,0,0,0,1,0xf, dz, 0,0xc0340000, 0,0x40340000)` çağrılıyor. 0xc034…=−20.0, 0x4034…=20.0. İlk argümanlar 1 karakterlik bir std::string ('d' = 100) oluşturuyor. FUN_00487b70: `if (x < lo || hi < x)` → hata.
- Sonuç: Her analiz tipinde −20 ≤ dz ≤ 20 olmalı (uçlar dahil). Aksi halde "… is outside the admissible range (-20, 20)" benzeri bir mesaj çıkıyor.
- Destekleyen GUI gözlemi: — (rapor yazılırken GUI'de test edilmemişti)
- Güven: orta (mesajın tam metni ve "d" önekinin nasıl birleştiği FUN_00485390 içinde, izlenmedi)
- Açık kalan: GUI'de dz=20.1 ile doğrulanmalı.
- Sonradan: V40 (dz=20.1) `Effect size d is outside the admissible range (-20, 20).` hatası verdi, V43 (dz=20) hesaplandı. Uçlar dahil ve mesaj öneki "d" — bulgu doğrulandı (LEDGER G-07).

### R-08 [REA] df = N − 1
- Görev: R3
- Konum: FUN_004db950 @ 0x4db950 (vtable+0x124) ; ARE tablosu @ 0x6096a8 ; kurucu FUN_004db820 @ 0x4db8c1, 0x4db8d8, 0x4db8f7
- Gözlem: `df = ARE[idx] * N; if (flag_0x358 == 0) df = df - 1.0;`. ARE[0] = 1.0 (bayt `000000000000f03f` @ 0x6096a8). Kurucu idx (0x35c) = 0 ve flag (0x358) = 0 atıyor. N = n1+n2; Calculate n1 = n2 = N·0.5 yazıyor (FUN_004d38b0 @ 0x4d38cf'te tekrar toplanıyor).
- Sonuç: Matched pairs varsayılanında df = 1.0·N − 1 = N − 1.
- Destekleyen GUI gözlemi: G1 (N=34 → Df=33)
- Güven: yüksek
- Açık kalan: idx ≠ 0 (ARE tablosu: 1.5, 0.955…) ve flag 0x358 ≠ 0 durumlarını hangi kodun açtığı izlenmedi. Olasılıkla Wilcoxon/ARE türevi sınıflar için.

### R-09 [REA] δ = dz · √N (sqrt çağrısı)
- Görev: R3
- Konum: FUN_004dbdc0 @ 0x4dbdc0 (vtable+0x50) ; çağıran FUN_004d38b0 @ 0x4d39e1
- Gözlem: `v = ARE[idx]; if (0 < field_0x360) v = v/(1 - N/field_0x360); v = v*N; return SQRT(v) * dz;`. Kurucu field_0x360 = −1 atıyor (0x4db8b7, 0x4db931), yani düzeltme dalı varsayılan olarak kapalı.
- Sonuç: δ = √(1·N)·dz = dz·√N. dz'nin işareti korunuyor (abs yok).
- Destekleyen GUI gözlemi: G1 (dz=0.5, N=34 → δ=2.9154759), G6
- Güven: yüksek
- Açık kalan: field_0x360'ı > 0 yapan yol bulunamadı (sonlu popülasyon düzeltmesi olabilir; [AJAN] tahmini).

### R-10 [REA] Güç formülü: α/2 bölünmesi ve iki kuyrukta alt kuyruğun eklenmesi
- Görev: R3
- Konum: FUN_004d38b0 @ 0x4d38b0 (PowerT tabanı, vtable+0x34) ; giriş FUN_004bdee0 @ 0x4bdee0 (vtable+0x30)
- Gözlem: `p = α / ((one_tailed==0) + 1.0)` (0x4d398d–0x4d39ab). dz ≥ 0 ise `t_c = t⁻¹(1−p)`, dz < 0 ise `t_c = t⁻¹(p)` (merkezi t, ncp=0). Sonra ncp=δ atanıyor. Tek kuyrukta güç = `1 − F(t_c;δ)` (dz≥0). İki kuyrukta güç = `1 − (F(t_c;δ) − F(−t_c;δ))`.
- Sonuç: İki kuyrukta t_c = t⁻¹(1−α/2), güç = P(T′>t_c) + P(T′<−t_c). Alt kuyruk ekleniyor.
- Destekleyen GUI gözlemi: G2 (iki kuyruk α=.10 sonucu, tek kuyruk α=.05'ten ≈1.5e-5 büyük)
- Güven: tek kuyruk yüksek (assembly ile doğrulandı); iki kuyruk orta-yüksek (yalnızca decompiler; Ghidra assembly listesi 0x4d3a31'de kesiliyor)
- Açık kalan: Bayrak 0x2a9 = `(kuyruk seçimi == 0)`, FUN_004dc2a0'da atanıyor. "0 = One" eşlemesi GUI liste sırasından çıkarım ([AJAN]).

### R-11 [REA] Noncentral t CDF: gömülü, programın kendi implementasyonu
- Görev: R3
- Konum: TDistribution vtable @ 0x5c4a20 (CDF +4 = FUN_004fa7e0, ters CDF +8 = FUN_004fb8c0, ncp atama +0x2c) ; noncentral seri FUN_004f9fa0 @ 0x4f9fa0 ; merkezi t FUN_004514f0
- Gözlem: FUN_004fa7e0: `|ncp| >= 1e-100` ise FUN_004f9fa0, değilse merkezi FUN_004514f0. FUN_004f9fa0: t<0 için simetriyle işaret çeviriyor. floor(δ²/2)'den ileri ve geri toplam yapıyor; tamamlanmamış beta (FUN_005a74a0) ve normal CDF (FUN_005a7c30) kullanıyor. Yakınsama 5.55e-17, en fazla 50000 terim. Hata dizeleri: "TDist-Cdf: answer below lower search bound" vb.
- Sonuç: Noncentral t dağılımı harici bir DLL'den değil, binary içindeki kendi seri implementasyonundan hesaplanıyor.
- Destekleyen GUI gözlemi: G2
- Güven: yüksek (kendi kodu olduğu) / düşük (algoritmanın adı)
- Açık kalan: [AJAN] Yapı Lenth AS 243 / Benton–Krishnamoorthy (2003) tipi seriye benziyor; kaynakla karşılaştırılmadı. Hata dizeleri DCDFLIB `cdft` tarzında.

### R-12 [REA] A priori N araması: aralık genişletme + Brent kök bulucu + ceil
- Görev: R4
- Konum: FUN_00496aa0 @ 0x496aa0 (vtable+0x48) ; amaç FUN_004968d0 @ 0x4968d0 ; aralık FUN_0049a210 @ 0x49a210 → FUN_004962d0 @ 0x4962d0 ; kök FUN_004f9bb0 @ 0x4f9bb0 ; yuvarlama FUN_00496a20 @ 0x496a20
- Gözlem: Amaç fonksiyonu f(N) = güç(dz, α, N) − hedef_güç; N sürekli (kesirli) değer alıyor. FUN_004962d0(2.0, 100.0) önce f(100)'ü hesaplıyor: f<0 ise üst sınırı ×1.6 ile f≥0 olana kadar büyütüyor (sayaç yok); değilse alt sınırı 2'ye doğru daraltıyor. Sonra Brent kök bulucu çalışıyor: tolerans 1e-10 (0x3ddb7cdfd9d7bdbb), en fazla 300 iterasyon, EPS 1.11e-16. Son adımda `N = ceil(floor(x·1e10+0.5)/1e10)`; N < 2 ise N = 2. Güç bu tamsayı N'de yeniden hesaplanıyor.
- Sonuç: Başlangıç aralığı [2, 100]. Yöntem ne doğrusal artış ne bisection; geometrik aralık genişletme + Brent. Sonuç tavana yuvarlanan en küçük N, yani güç(N) ≥ hedef. Alt sınır 2.
- Destekleyen GUI gözlemi: G3, G4
- Güven: yüksek
- Açık kalan: Aralık genişletmede üst sınır yok; pratikte güç monoton olduğu için döngü sonlanıyor ([AJAN]).

### R-13 [AJAN] G3: güç = α iken neden N = 2 çıkıyor
- Görev: R4
- Konum: FUN_004f9bb0 @ 0x4f9bb0 (işaret değişimi yoksa `status=1; return 0`) ; FUN_00496aa0 @ 0x496aa0 (`N < 2` ise `N = 2`)
- Gözlem: Güç ≈ α olduğunda f(N) aralık boyunca ≥ 0 olur ve kök aranmaz. Brent 0 döndürür, ceil(0)=0 < 2 olduğundan N = 2'ye yükseltilir.
- Sonuç: N=2 sonucu, kökün bulunmasından değil alt sınır sıkıştırmasından geliyor (çıkarım).
- Destekleyen GUI gözlemi: G3
- Güven: orta
- Açık kalan: Bu girdi için akış dinamik olarak izlenmedi.

### R-14 [AJAN] G4: dz=0.01'de aramanın hızlı bitmesi
- Görev: R4
- Konum: FUN_004962d0 @ 0x4962d0 (×1.6 genişletme) ; FUN_004f9bb0 @ 0x4f9bb0 (≤300 iterasyon)
- Gözlem: 100·1.6^k ≥ 78491 için k ≈ 15 genişletme gerekir. Ardından Brent birkaç düzine iterasyonda yakınsar.
- Sonuç: Arama doğrusal olmadığı için büyük N değerleri de birkaç düzine güç hesabıyla bulunuyor (çıkarım).
- Destekleyen GUI gözlemi: G4
- Güven: orta
- Açık kalan: Gerçek iterasyon sayısı ölçülmedi.

### R-15 [REA] Post hoc N okuma: `floor(x + 0.5)` (yarım yukarı)
- Görev: R5
- Konum: FUN_004dc2a0 → FUN_0048ab70(…, 2) @ 0x48ab70 → FUN_0048b8d0 @ 0x48b8d0 ; alan adı tablosu @ 0x6093c0[2] = 0x6093c8 → "Total sample size" @ 0x5c54e0 ; ayraç "=" @ 0x5c3aec
- Gözlem: FUN_0048b8d0'da bir dal, metni double olarak okuyup `iVar2 = (int)floor(x + 0.5);` döndürüyor (bayrak DAT_00609659 açık ve metinde "=" varsa). Diğer dal, alan nesnesinde önbelleğe alınmış int'i döndürüyor (FUN_00439bd0: `return *(this+0x4c)`).
- Sonuç: Kesirli N, `floor(x+0.5)` ile en yakın tamsayıya yuvarlanıyor (.5 yukarı). Bu, G5 ile birebir uyumlu.
- Destekleyen GUI gözlemi: G5 (10.5→11, 10.2→10)
- Güven: orta
- Açık kalan: Normal yazılan sayının hangi dala girdiği ve önbellekteki int'in (+0x4c) nerede hesaplandığı bulunamadı. Bu yüzden G5 davranışının kesin olarak bu satırdan geldiği kanıtlanmadı.
- Sonradan: V42 (post hoc, N=2.6) hesaplandı ve Df=2 verdi; yani N önce 3'e yuvarlanıyor, aralık kontrolü yuvarlanmış değerle yapılıyor. V34 (10.5→11) ve V38 (10.2→10) ile birlikte `floor(x+0.5)` kuralıyla tutarlı (LEDGER G-06, G-07).

### R-16 [REA] Negatif dz: abs yalnızca doğrulamada; δ ve t_c işaretini koruyor
- Görev: R6
- Konum: FUN_004db990 @ 0x4db990 (tek ABS) ; FUN_004d38b0 @ 0x4d3956 (`COMISD dz, 0.0; JC`) ; FUN_004dbdc0 @ 0x4dbdc0 ; FUN_004f9fa0 @ 0x4f9fa0
- Gözlem: Güç zincirinde dz'ye abs uygulanmıyor. dz<0 iken p = α/k ve t_c = t⁻¹(p) < 0 seçiliyor; δ = dz·√N negatif kalıyor. Tek kuyrukta güç F(t_c;δ) (alt kuyruk). nct CDF, t<0 için simetriyle (t,δ)→(−t,−δ) çeviriyor.
- Sonuç: Gösterilen δ ve kritik t negatif; güç ve N, |dz| ile aynı. Matematiksel olarak F(−c;−δ) = 1 − F(c;δ) ayna simetrisi var.
- Destekleyen GUI gözlemi: G6 (dz=−0.5 → δ=−2.9154759)
- Güven: yüksek
- Açık kalan: —

### R-17 [REA] Paylaşılan ortak fonksiyonlar
- Görev: R1 / R3 (kural 5)
- Konum: FUN_004d38b0 (8 vtable'da: 0x5ca30c, 0x5ca440, 0x5ca574, 0x5ca6a4, 0x5ca7d4, 0x5ca904, 0x5cab64, 0x5cac94) ; FUN_00488a10 (99 çağrı) ; FUN_00496aa0 ; FUN_004f9bb0
- Gözlem: t-tabanlı güç fonksiyonu, Linear multiple regression (0x5cab30) ve PowerTOneMean dahil 8 sınıfın vtable'ında. Alfa/güç/N doğrulayıcıları ve a priori Brent araması testlerden bağımsız, genel kod. Etki büyüklüğü mesajı regresyon (FUN_004da5d0) ile ortak.
- Sonuç: Matched pairs'e özgü kod yalnızca df (0x4db950), δ (0x4dbdc0), etki doğrulama (0x4db990), Calculate (0x4dc2a0) ve ad (0x4dcf10). Gerisi paylaşılıyor.
- Destekleyen GUI gözlemi: —
- Güven: yüksek
- Açık kalan: Diğer 6 vtable'ın hangi testlere ait olduğu tek tek eşlenmedi.

### R-18 [REA] A priori ile post hoc arasında N alt sınırı farkı
- Görev: R4 / R2
- Konum: FUN_0049a210 @ 0x49a210 (alt sınır 2.0) ; FUN_00496aa0 @ 0x496aa0 (N<2 → 2) ; FUN_004dc2a0 @ 0x4dc2a0 (`FUN_00488a10(N,3,…)`)
- Gözlem: A priori en küçük N = 2 üretebiliyor; post hoc ise N < 3'ü reddediyor.
- Sonuç: A priori'nin verdiği N=2 sonucu post hoc'a girildiğinde "Total sample size is outside the admissible range" hatası alınır.
- Destekleyen GUI gözlemi: G3 + G7 (ikisi birlikte)
- Güven: yüksek
- Açık kalan: —

---

## Bulunamayanlar
1. Mesajlardaki `1e-07`, `1`, `3` ve `2147483646` sayıları düz dize olarak yok; çalışma anında `ostream <<` ile ekleniyorlar (R-02, R-05). Yalnızca `0.00001` mesaj dizesinin içinde yazılı (0x5cb510).
2. `Noncentrality parameter $\delta$` (0x5c567c) dizesine koddan doğrudan xref bulunamadı (dolaylı tablo erişimi olabilir).
3. `Effect size dz` (0x5c5ba0) yalnızca 0x609540'taki veri tablosundan referanslanıyor; tabloyu okuyan kod izlenmedi.
4. Post hoc'ta normal yazılan kesirli N'nin hangi kod yolunda tamsayıya çevrildiği (R-15'teki önbellek int'i, +0x4c) bulunamadı.
5. FUN_004d38b0'ın iki kuyruk dalı için Ghidra assembly listesi yok (gövde 0x4d3a31'de bitiyor); kanıt yalnızca decompiler çıktısı.
6. ARE indeksinin (0x35c) ve df bayrağının (0x358) sıfır dışı değere getirildiği yer izlenmedi.
7. A priori aralık genişletme döngüsünde en fazla iterasyon sınırı **yok** (FUN_004962d0 içinde sayaç bulunamadı). Brent'te ise 300 sınırı var.

## GUI gözlemiyle çelişen bulgular
Doğrudan çelişki bulunamadı. G1–G7'nin tamamı kodla tutarlı. İnce farklar:
- **Mesajdaki aralık gösterimi yanıltıcı:** `(1e-07, 1)` ve `(3, 2147483646)` açık aralık gibi görünse de kodda tüm uçlar **dahil** (≤). α=1e-07 ve N=3 kabul ediliyor.
- **"1" aslında 0.9999999:** Alfa/güç üst sınırı kodda 0.9999999. Mesajdaki "1", `setprecision(6)` yuvarlamasından geliyor. Örneğin güç = 0.99999995 reddedilmeli; bu değer GUI'de test edilmedi.
- **dz için [−20, 20] sınırı** (R-07) ilk GUI gözlem listesinde yoktu. Sonradan V40 ve V43 ile doğrulandı (LEDGER G-07).
