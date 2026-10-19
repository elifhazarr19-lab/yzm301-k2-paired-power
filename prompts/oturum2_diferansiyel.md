# Oturum 2 — ikinci görev: SPEC v1.1 güncellemesi + diferansiyel test

> Aynı yazım oturumuna (Claude Code, `C:\paired-power`) verildi. Bu klasöre yalnızca güncellenmiş `SPEC.md` ve G*Power arayüzünden toplanmış kara kutu değerleri (`oracle/gpower_vectors.csv`) eklendi. Tersine mühendislik içeriği yoktur.

---

## 1. SPEC v1.1
`SPEC.md` güncellendi. Yeni bölüm **§3.1**, senin sorduğun 6 belirsizliğe verilen kararları içeriyor. Kodunu §3.1'e göre gözden geçir; uymayan bir yer varsa düzelt ve `# SPEC-BELIRSIZ:` işaretlerini kaldır. SPEC testleri yine geçmeli.

## 2. G*Power diferansiyel testi
`oracle/gpower_vectors.csv`, G*Power 3.1.9.7 arayüzünden elle toplanmış referans değerlerdir. Sütunlar:
- girdiler: `id, mode, tails, dz, alpha, power, n_input`
- G*Power çıktısı: `gp_n_total, gp_actual_power, gp_critical_t, gp_df, gp_ncp` (7 ondalık) ve `gp_error_message`
- `status`: `GUI-TOPLANDI` (hesaplı), `GUI-TOPLANDI-HATA` (G*Power hata verdi), `IPTAL` (kullanma)

`tests/test_differential.py` yaz:
- Her `GUI-TOPLANDI` satırı için CLI'yı çalıştır (CLI üzerinden; motoru doğrudan çağırma).
- Karşılaştırma kuralları (ödev): **N ve df tam eşleşmeli.** Diğer değerler G*Power'ın 7 basamağına göre: motorun tam hassasiyetli değeri 7 ondalığa yuvarlanınca G*Power'la aynı olmalı. Bunun için CLI'ya, varsayılan çıktıyı değiştirmeyen gizli bir `--precision` seçeneği ekleyebilirsin (varsayılan 4) ya da motoru ikinci bir testte doğrudan çağırabilirsin — hangisini seçtiğini raporla.
- Post-hoc satırlarında `gp_n_total` boştur; N_int'i `n_input`'tan SPEC §5.1'e göre hesaplayıp df ile karşılaştır.
- Her `GUI-TOPLANDI-HATA` satırı için CLI'nın `error` döndürdüğünü ve çıkış kodunun 0 olmadığını doğrula.

## 3. Kütüphane vektörleri (500+)
`statsmodels` kur (`pip install statsmodels`) ve `tests/gen_library_vectors.py` yaz:
- En az 500 rastgele (sabit tohumlu) girdi: tails ∈ {1,2}, dz ∈ [0.05, 2.5], alpha ∈ {0.001, 0.01, 0.05, 0.10}, power ∈ [0.5, 0.99]; ayrıca post-hoc için N ∈ [3, 500].
- `statsmodels.stats.power.TTestPower` (tek örneklem/eşleştirilmiş t) ile: a-priori için **kesirli** N (`solve_power`), post-hoc için güç.
- Sonucu `oracle/library_vectors.csv` olarak kaydet (G*Power vektörlerinden ayrı dosya).

`tests/test_library.py`:
- Post-hoc: bizim gücümüz ile statsmodels gücü 1e-6 içinde mi?
- A-priori: `ceil(statsmodels_N)` ile bizim N'miz kaç vektörde aynı? Farklı olanları listele ve nedenini açıkla (ödev bu farkın açıklanmasını ayrıca istiyor: kütüphaneler N'yi kesirli verir, G*Power yukarı yuvarlar).
- statsmodels'ın iki kuyrukta alt kuyruğu dahil edip etmediğini kendin kontrol et ve raporda yaz.

## 4. Uyum raporu
`tests/UYUM_RAPORU.md` oluştur:
- G*Power vektörleri: N/df tam eşleşme oranı (x/30), 7 basamak eşleşme oranı, hata vektörleri (x/8).
- Kütüphane vektörleri: kaç vektör, post-hoc uyum, a-priori ceil uyumu ve farkların açıklaması.
- Her uyuşmazlık için tek satır açıklama.
- Testlerin nasıl çalıştırılacağı (`pytest -q`).

Bitince kısa bir özet ver: test sayıları, uyum oranları, uyuşmazlıklar.
