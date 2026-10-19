# YZM301 — YAZILIM GERÇEKLEŞTİRME VE TEST
# G*POWER t-paired TERSİNE MÜHENDİSLİK VE KANIT TOPLAMA

Sen deneyimli bir yazılım mühendisi, test mühendisi, tersine mühendislik araştırmacısı ve bilimsel hesaplama uzmanı gibi çalışacaksın.

Üniversitedeki YZM301 Yazılım Gerçekleştirme ve Test dersi için G*Power uygulamasının belirli bir test ailesini inceleyerek davranışını kanıtlarla belgelemem ve daha sonra temiz odada yeniden uygulamam gerekiyor.

Amacım yalnızca çalışan bir program yazmak değil; tersine mühendislikle elde edilen sonuçların doğru olduğunu testlerle ve gerçek kanıtlarla göstermek.

## 1. ÖDEVİN KAPSAMI

İncelenecek uygulama: G*Power 3.1.9.7 (Windows)

Seçtiğim test ailesi:
K2 — Paired samples t-test (t-paired).

Örnek kullanım:
Aynı kişilerin tedavi öncesi ve tedavi sonrası kan basınçlarının karşılaştırılması.

Bu test ailesini bağımsız iki grubun t-testinden kesinlikle ayır. t-paired için doğrulanmamış biçimde t2-indep davranışlarını kullanma.

Temel teslim CLI uygulamasıdır ve 85 puana kadar değerlendirilmektedir.
MCP sunucusu ek bonus, MCP üzerinden doğal dilde çalışan AI ajanı ise ek bonus sağlayabilir.

En önemli başarı koşulu, gizli test vektörlerinde hesaplanan N değerinin en az %90 oranında tam eşleşmesidir.

## 2. ÖNCE BELGELERİ İNCELE

Sana yüklediğim bütün ödev belgelerini ve ilgili dosyaları incele.

Özellikle şunları belirle:
- Ödevin zorunlu gereksinimleri.
- CLI sözleşmesi ve beklenen giriş/çıkış biçimleri.
- Etik kurallar ve temiz oda şartları.
- İstenen teslim dosyaları.
- Test ve puanlama ölçütleri.
- REA ile ilgili istenen kanıt biçimi.
- Varsa CONTRACT.md dosyasındaki kurallar.

Bir dosya eksikse bunu açıkça belirt.
Dosyada bulunmayan kuralları kendin uydurma.

## 3. GERÇEK ARAÇ ERİŞİMİNİ DOĞRULA

Gerçekten erişebildiğin araçları ve ortamı kontrol et.

Özellikle:
- G*Power uygulamasına erişimin var mı?
- Uygulamayı gerçekten çalıştırabiliyor musun?
- REA veya Ghidra kullanabiliyor musun?
- Uygulamanın arayüzünü gözlemleyebiliyor musun?
- Gerçek ekran görüntüsü alabiliyor musun?
- Hesaplamaları tekrarlayarak doğrulayabiliyor musun?

Erişimin yoksa bunu baştan söyle.

Görmediğin ekranları görmüş gibi davranma.
Çalıştırmadığın araçları çalıştırdığını söyleme.
Gerçek olmayan ekran görüntüleri, kanıtlar, sayısal sonuçlar veya REA bulguları üretme.

REA/Ghidra erişimi bulunmuyorsa, gerçek REA kanıtlarının toplanması için hangi adımları benim uygulamam gerektiğini ayrıntılı açıkla.

## 4. İLK AŞAMANIN AMACI

Bu aşamada henüz uygulama kodunu yazma.

Önceliğin davranışı araştırmak, kanıtları kaydetmek ve uygulamanın nasıl davranması gerektiğini kesin bir teknik şartnameye dönüştürmek.

Aşağıdaki dosyaları hazırlamaya odaklan:

### LEDGER.md
Her davranış için:
- Benzersiz kanıt kimliği.
- Araştırılan davranış.
- Gözlenen giriş.
- Gözlenen çıktı.
- Kanıtın kaynağı.
- İlgili ekran görüntüsü veya diğer kanıt dosyası.
- Sonucun nasıl tekrar üretileceği.
- Bulgudan çıkarılan sonuç.
- Belirsizlikler ve sınırlamalar.

REA ile doğrudan doğrulanmış kanıtları [REA] etiketiyle belirt.

Diğer kaynakları uygun şekilde [DOK] veya [AJAN] olarak etiketle.

Belgelere dayanan bir bilgiyle REA üzerinden gözlemlenmiş bir bulguyu birbirine karıştırma.

### SPEC.md
Bağımsız bir geliştiricinin yalnızca bu dosyayı okuyarak uygulamayı yazabilmesini sağlayacak kadar açık bir teknik şartname oluştur.

Şu konuları ele al:
- Test ailesinin kesin tanımı.
- Desteklenen analiz türleri.
- Giriş parametreleri.
- Parametrelerin aralıkları ve doğrulama kuralları.
- Etki büyüklüğü, alfa ve güç gibi istatistiksel parametreler.
- Örneklem büyüklüğü N'nin anlamı.
- Beklenen çıktı alanları.
- Hata davranışları.
- Sayısal toleranslar.
- Yuvarlama ve tam sayı örneklem büyüklüğü kuralları.
- CLI sözleşmesi.
- Test senaryoları.
- Sınır durumları.
- Henüz doğrulanmamış davranışlar.

Hiçbir davranışı yalnızca tahmin ederek kesin kural olarak yazma.
Belirsiz davranışları açıkça işaretle ve nasıl araştırılmaları gerektiğini açıkla.

### HALLUCINATIONS.md
Araştırma sırasında ortaya çıkan:
- Doğrulanmamış varsayımlar.
- Yanlış olduğu anlaşılan varsayımlar.
- Çelişkili sonuçlar.
- Eksik kanıtlar.
- Ek araştırma gerektiren noktalar.

Bu dosyayı sonraki aşamada güncellenebilecek biçimde hazırla.

### ORACLE VE KANIT DOSYALARI
G*Power ile gerçek karşılaştırmalar yapmak için bir test vektörü düzeni oluştur.

Her vektörde mümkün olduğunda:
- Vektör kimliği.
- Analiz türü.
- Parametreler.
- G*Power'dan alınan gerçek sonuç.
- Hesaplanan N.
- İlgili kanıtın yolu.
- Doğrulama durumu.

Hedef en az 30 gerçek G*Power arayüz referans vektörü oluşturmaktır.

Ancak gerçekten G*Power üzerinde çalıştırılmayan bir vektörü gerçek referans olarak gösterme.

Sentetik veya bağımsız hesaplama kütüphanesinden üretilen vektörleri gerçek G*Power sonuçlarından ayrı tut.

## 5. TEMİZ ODA KURALI

Bu ilk aşama araştırma ve şartname aşamasıdır.

İkinci aşamada başka bir oturum kodu yalnızca SPEC.md üzerinden yazacak.

Bu nedenle SPEC.md, uygulamayı geliştirecek kişinin gizli tersine mühendislik notlarını görmeden doğru davranışı uygulamasına yetecek ayrıntıda olmalı.

Decompile edilmiş kodları teslim edilecek projeye koyma.
G*Power.exe dosyasını GitHub deposuna ekleme.
Lisans ve ödev etik kurallarına uy.

## 6. BENDEN BEKLEDİĞİN ÇALIŞMA ŞEKLİ

Ben yazılım mühendisliği birinci sınıf öğrencisiyim. Bu yüzden açıklamaları anlaşılır, aşamalı ve uygulanabilir şekilde yap.

Her aşamada şunları belirt:
1. Ne yapılacak?
2. Neden yapılacak?
3. Nasıl yapılacak?
4. Hangi dosya oluşturulacak?
5. Başarılı olup olmadığını nasıl anlayacağım?
6. Hangi kanıtı saklamalıyım?

Benden bir işlem yapmamı istiyorsan adımları tek tek yaz.

Bilgisayarımda bulunan araçlara erişimin olduğunu varsayma.

## 7. İLK YANITIN

İlk olarak:
- Belgelerden anladığın ödev kapsamını özetle.
- Eksik belgeleri ve erişim gereksinimlerini belirt.
- G*Power/REA/Ghidra erişiminin gerçekten doğrulanıp doğrulanmadığını açıkla.
- t-paired için araştırılması gereken kritik davranışları listele.
- İlk olarak benim yapmam gereken işlemleri sırala.

Ardından araştırmayı yürüt.

Kanıt toplanmadan tamamlanmış gibi görünen sahte bir LEDGER veya SPEC üretme.

Önceliğimiz doğruluk, izlenebilirlik ve gizli testlerde başarılı olacak bir uygulamanın temelini oluşturmaktır.