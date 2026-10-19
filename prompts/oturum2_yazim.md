# Oturum 2 — Temiz oda yazım oturumu (ilk prompt)

> Bu oturum, YZM301 "Teardown Sprint" ödevinin yazım oturumudur. Temiz oda kuralı gereği bu oturum **yalnızca `SPEC.md`** ile başlar. Tersine mühendislik notlarını, Ghidra/REA çıktılarını ve inceleme oturumunun konuşmasını görmez.

---

Sen deneyimli bir Python geliştiricisi ve test mühendisisin.

Bu klasördeki `SPEC.md` dosyası, eşleştirilmiş örneklem t testi (t-paired) için bir güç analizi hesaplayıcısının tam şartnamesidir. Görevin bu şartnameyi **yalnızca SPEC.md'ye dayanarak** uygulamak.

## Kurallar
1. Kaynak olarak yalnızca `SPEC.md`'yi kullan. Başka bir güç analizi programının kaynak kodunu, decompile çıktısını ya da tersine mühendislik notlarını arama ve kullanma.
2. SPEC'te açık olmayan bir nokta görürsen kendi kafana göre karar verme: önce bana sor ya da kodda `# SPEC-BELIRSIZ:` yorumuyla işaretleyip bana listele.
3. Programın adı ya da çıktısı "G*Power" olarak sunulmayacak. CLI komutunun adı SPEC'teki gibi `gpower-clone` olacak (ödev sözleşmesi bunu istiyor), ama paket adı farklı olmalı (öneri: `pairedpower`).
4. Dağılım fonksiyonları için `scipy` kullanabilirsin. Puan çözücüden (N arama), yuvarlamadan ve df hesabından geliyor; bunları SPEC'e birebir uy.

## Yapılacaklar
1. Proje yapısı:
   ```
   src/pairedpower/engine.py   # saf hesap motoru (G/Ç yok)
   src/pairedpower/cli.py      # argüman okuma, doğrulama, JSON çıktı
   pyproject.toml              # `gpower-clone` konsol komutu
   tests/test_spec.py          # SPEC §7'deki Gherkin senaryolarının pytest karşılığı
   README_dev.md               # kurulum ve çalıştırma
   ```
2. Motor: SPEC §4 (doğrulama sırası), §5 (hesap modeli, §5.2 N araması, §5.3 sayısal tuzak) ve §6 (çıktı) birebir uygulanacak. Motor, CLI'dan bağımsız çağrılabilir olmalı (ileride MCP sunucusu aynı motoru kullanacak).
3. CLI: SPEC §3'teki bayraklar ve eş adlar; başarıda tek satır JSON ve çıkış kodu 0; hatada `{"error": "..."}` ve sıfırdan farklı çıkış kodu.
4. Testler: SPEC §7'deki her Examples satırı ayrı bir test olsun. Hepsi geçmeli.
5. Bitince bana şunları raporla: kaç test geçti, SPEC'te belirsiz bulduğun noktalar, ve örnek iki çağrının çıktısı:
   ```
   gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
   gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 35
   ```

## Sonraki adım (bu oturumda, yazım bittikten sonra verilecek)
Yazım ve SPEC testleri tamamlandıktan sonra sana G*Power arayüzünden toplanmış kara kutu referans değerlerini içeren `gpower_vectors.csv` dosyası verilecek. Onunla diferansiyel test (`tests/test_differential.py`) ve uyum raporu yazacaksın. Bu dosya yalnızca girdi/çıktı değerleri içerir; tersine mühendislik içeriği yoktur.
