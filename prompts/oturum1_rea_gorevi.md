# Oturum 1 — REA/Ghidra inceleme görevi (Claude Code)

Bu prompt, YZM301 "Teardown Sprint" ödevinin inceleme oturumunda REA + Ghidra ile çalışan Claude Code ajanına verildi.
Öğrenci: Elif Hazar (bireysel). Test ailesi: K2 — t testi, eşleştirilmiş örneklem (G*Power: "Means: Difference between two dependent means (matched pairs)").

---

## Rolün
Bir tersine mühendislik araştırmacısısın. Amacın kod kopyalamak değil, aşağıdaki davranışların binary içinde **nerede ve nasıl** gerçekleştiğini kanıtlamak.

## Hedef dosya
`C:\rea-work\GPowerNT.exe` — G*Power 3.1.9.7 (Windows), resmi sayfadan indirildi.
SHA-256: `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`
İşe başlamadan önce bu hash'i doğrula; tutmazsa dur ve bildir.

## Kurallar (çok önemli)
1. **Kanıt yoksa iddia yok.** Her bulgu için bir **fonksiyon adresi** ve/veya **dize adresi** ver. Adres veremiyorsan bulguyu `[AJAN]` (kanıtsız çıkarım) olarak işaretle.
2. **Decompile dökümü yazma.** Bulgu başına en fazla 5 satırlık kısa alıntı veya kendi cümlelerinle özet kullan. Bu notlar ödev klasörüne girecek; uzun decompile çıktısı ödev kuralına aykırı.
3. Bilmediğin şeyi tahmin edip kesin gibi yazma. "Bulunamadı" demek kabul edilebilir bir sonuçtur.
4. Binary'yi değiştirme, yamalama, çalıştırma. Yalnızca statik inceleme.
5. Yalnızca t testi / matched pairs ile ilgili kısımlara odaklan. Diğer test ailelerine (bağımsız iki grup, ANOVA, ki-kare) girme; ancak paylaşılan ortak bir fonksiyon bulursan bunu belirt.

## Arka plan: G*Power arayüzünden gözlenen davranışlar
Bunlar arayüzde gözlendi (GUI kanıtı). Senin görevin bunları binary'de bulmak, doğrulamak ya da çürütmek.

| Kod | Gözlem | Örnek vektör |
|---|---|---|
| G1 | df = N − 1, δ = dz·√N | dz=0.5, N=34 → Df=33, δ=2.9154759 |
| G2 | İki kuyrukta güç = P(T′>t_c) + P(T′<−t_c) (alt kuyruk ekleniyor), t_c = t⁻¹(1−α/2) | tek kuyruk α=.05 N=27: güç 0.8118316; iki kuyruk α=.10 N=27: 0.8118463 |
| G3 | A priori: güç ≥ hedef olan en küçük tamsayı N; en küçük sonuç N=2 | dz=0.5, güç=α=0.05 → N=2 |
| G4 | A priori çok küçük etkide hızlı bitiyor | dz=0.01 → N=78491 |
| G5 | Post hoc'ta kesirli N en yakın tamsayıya yuvarlanıyor (.5 yukarı) | 10.5→11, 10.2→10 |
| G6 | Negatif dz: N ve güç |dz| ile aynı, ama ekranda δ ve critical t negatif | dz=−0.5 → δ=−2.9154759 |
| G7 | Hata mesajları (birebir): | |
| | `Power must be greater than or equal to alpha.` | güç < α |
| | `In an a priori analysis, the absolute value of the effect size be greater than 0.00001.` | dz=0 |
| | `Alpha is outside the admissible range (1e-07, 1).` | α=0, α=1 |
| | `Power is outside the admissible range (1e-07, 1).` | güç=1 |
| | `Total sample size is outside the admissible range (3, 2147483646)` | post hoc N=2, N=1 (N=3 kabul ediliyor) |

## Görevler (öncelik sırasıyla)

**R1 — Dizeler.** Şu dizeleri binary'de ara; her biri için dize adresini ve ona referans veren (xref) fonksiyon adres(ler)ini yaz:
- G7'deki beş hata mesajı (parçalı arama yap: "admissible range", "greater than or equal to alpha", "absolute value of the effect size")
- "matched pairs", "dependent means", "Effect size dz", "Noncentrality parameter", "Total sample size"

**R2 — Girdi doğrulama.** R1'deki hata dizelerini kullanan fonksiyon(lar)da hangi sabitlerle ve hangi karşılaştırma operatörüyle (<, ≤, >, ≥) kontrol yapıldığını bul: 1e-07, 1, 0.00001, 3, 2147483646. Özellikle: alt sınırlar dahil mi hariç mi? "power ≥ alpha" kontrolü tam olarak nasıl?

**R3 — Hesap çekirdeği.** Matched pairs testinin güç hesabını yapan fonksiyonu bul. Şunları göster:
- df hesabı (N − 1 mi?)
- δ hesabı (sqrt çağrısı, dz ile çarpım)
- iki kuyruk için α/2 kullanımı ve alt kuyruğun eklenmesi (G2)
- noncentral t dağılım fonksiyonunun çağrıldığı yer (kendi yazdıkları bir fonksiyon mu?)

**R4 — A priori N araması.** N'yi bulan döngüyü/algoritmayı bul:
- başlangıç değeri (2 mi?)
- doğrusal artış mı, ikili arama (bisection) mı, başka bir yöntem mi?
- durma koşulu (güç ≥ hedef mi, > mı?), en fazla iterasyon sınırı var mı?
- sonuç tamsayıya nasıl çevriliyor (ceil / floor / round)?

**R5 — Post hoc N yuvarlaması.** Kesirli N'nin tamsayıya çevrildiği yeri bul (G5). Hangi yuvarlama fonksiyonu/ifadesi kullanılıyor?

**R6 — İşaret.** Negatif dz'de mutlak değerin nerede alındığını ve δ / critical t işaretinin nasıl korunduğunu göster (G6).

## Çıktı
Bulgularını şu dosyaya yaz (yoksa oluştur):
`C:\Users\ELİF HAZAAR\Downloads\k2-tpaired-asama1\k2-tpaired\rea_notes\REA_BULGULAR.md`

Her bulgu için bu şablonu kullan:
```
### R-xx [REA] (veya [AJAN]) <kısa başlık>
- Görev: R1/R2/...
- Konum: fonksiyon @ 0x........ ; dize "...." @ 0x........
- Gözlem: <en fazla 5 satır kısa alıntı veya kendi cümlelerinle özet>
- Sonuç: <davranış kuralı, bir cümle>
- Destekleyen GUI gözlemi: G1..G7
- Güven: yüksek / orta / düşük
- Açık kalan: <varsa>
```
Dosyanın başına: kullandığın REA ve Ghidra sürümü, analiz tarihi, hash doğrulama sonucu.
Dosyanın sonuna: "Bulunamayanlar" listesi ve "GUI gözlemiyle çelişen bulgular" listesi (varsa — bunlar çok değerli).

Bitirince bana kısa bir özet ver: kaç bulgu [REA], kaç bulgu [AJAN], hangi görevler tamamlanamadı.
