# SPEC.md — Eşleştirilmiş örneklem t testi güç hesaplayıcısı (K2 · t-paired)

> **Durum: v1.1 — 2026-10-19** (v1.0 + yazım oturumunun sorduğu 6 belirsizliğe karar, §3.1). Hesap çekirdeği ve doğrulama kuralları G*Power arayüzü (30 hesaplı + 8 hatalı vektör) ve REA/Ghidra bulgularıyla doğrulandı. Kod yazımına (Oturum 2) hazır.
>
> Etiketler:
> - **[KESİN]** ödev belgesinden gelir.
> - **[DOĞRULANDI]** G*Power ekranında gözlendi (vektör kimliği verilir) ve/veya binary'de bulundu (LEDGER R-xx).
> - **[KARAR]** kanıtla belirlenemeyen, gerekçesiyle seçilmiş tasarım tercihi.
> - **[HİPOTEZ]** henüz doğrulanmadı.
>
> Bu belge kendi başına yeterli olacak şekilde yazıldı. Uygulayıcı G*Power'ın iç kodunu görmez; aşağıdaki kurallar davranışı tanımlar.

## 1. Test ailesinin tanımı
Aynı N deneğin iki ölçümü (örn. tedavi öncesi/sonrası tansiyon) karşılaştırılır. Hesap, fark puanları üzerinde **tek örneklem t testi** olarak yapılır. [DOĞRULANDI R-01, R-08, R-09]

**Bağımsız iki grup t testi (t2-indep) ile karıştırmayın:** bu ailede n1/n2, oran (ratio) ve df = n1+n2−2 yoktur. N, **çift (denek) sayısıdır**.

G*Power karşılığı: Test family "t tests" → Statistical test "Means: Difference between two dependent means (matched pairs)". [DOĞRULANDI V01 ekranı]

## 2. Analiz türleri [KESİN]
| Mod | Girdiler | Hesaplanan |
|---|---|---|
| `a-priori` | tails, dz, alpha, power | N (n_total) ve gerçekleşen güç |
| `post-hoc` | tails, dz, alpha, N | güç |

## 3. CLI sözleşmesi
Komut adı ve JSON biçimi ödevde sabittir [KESİN]. t-paired'e özel bayrak adlarını veren CONTRACT.md mevcut değil; aşağıdakiler ödevdeki t2-indep örneğinden türetildi [KARAR — HALLUCINATIONS H-01].

```
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 35
```

| Bayrak | Değer | Not |
|---|---|---|
| `--test` | `t-paired` | zorunlu |
| `--mode` | `a-priori` veya `post-hoc` | zorunlu |
| `--tails` | `1` veya `2` | zorunlu |
| `--dz` | ondalık sayı | **eş ad: `--d`** (t2-indep örneği `--d` kullanıyor). İkisi birden verilirse ve farklıysa hata. |
| `--alpha` | ondalık sayı | zorunlu |
| `--power` | ondalık sayı | yalnızca a-priori'de zorunlu |
| `--n` | ondalık sayı | yalnızca post-hoc'ta zorunlu; **eş adlar: `--n-total`, `--n_total`** |

- Ondalık ayraç noktadır. Sayı olarak okunamayan değer → hata. [KARAR]
- Bilinmeyen bayrak ya da bu ailede anlamsız bayrak (`--ratio`, `--n1`, `--n2`) → hata. [KARAR]
- Moda ait olmayan bayrak (a-priori'de `--n`, post-hoc'ta `--power`) → yok sayılır. [KARAR]

### 3.1 Yazım oturumunun sorularına verilen kararlar (v1.1) [KARAR]
1. Hem başarı hem hata JSON'u **standart çıktıya (stdout)** yazılır; stderr boş kalır. Hatada çıkış kodu 2.
2. `inf`, `-inf`, `nan` (her yazımıyla) sayı olarak kabul edilmez → hata.
3. `--tails` kontrolü (1 veya 2) bayrak okumasının parçasıdır ve §4'teki kontrollerden **önce** yapılır.
4. `--n`, `--n-total`, `--n_total` birden fazla verilirse ve değerleri farklıysa hata (`--dz`/`--d` ile aynı kural).
5. A-priori'de bulunan N 2147483646'yı aşarsa ya da arama NaN üretirse hata döner (G*Power'da bu bölge gözlenmedi).
6. Sonsuz/NaN N değeri için kullanılan hata metni önemsizdir; `error` alanı ve sıfırdan farklı çıkış kodu yeterlidir.
7. `--dz` (veya `--d`) her iki modda zorunludur. Moda ait olmayan bayraklar sessizce yok sayılır (§3).

## 4. Girdi doğrulama [DOĞRULANDI]
Kontroller aşağıdaki sırayla yapılır; ilk başarısız kontrol hata döndürür. Uçlar **dahildir**.

| # | Mod | Koşul (geçerli olması için) | Hata açıklaması (önerilen metin) | Kanıt |
|---|---|---|---|---|
| 1 | ikisi | `1e-07 ≤ alpha ≤ 0.9999999` | `Alpha is outside the admissible range (1e-07, 1).` | V24, V25, V41, R-02 |
| 2 | a-priori | `1e-07 ≤ power ≤ 0.9999999` | `Power is outside the admissible range (1e-07, 1).` | V26, R-03 |
| 3 | a-priori | `power ≥ alpha` (eşitlik geçerli) | `Power must be greater than or equal to alpha.` | V18, V19, V20, R-04 |
| 4 | ikisi | `−20 ≤ dz ≤ 20` | `Effect size d is outside the admissible range (-20, 20).` | V40, V43, R-07 |
| 5 | a-priori | `|dz| ≥ 0.00001` | `In an a priori analysis, the absolute value of the effect size must be greater than 0.00001.` | V21, R-06 |
| 6 | post-hoc | `N_int = floor(N + 0.5)`; `3 ≤ N_int ≤ 2147483646` (kontrol yuvarlanmış değerle) | `Total sample size is outside the admissible range (3, 2147483646).` | V32, V33, V39, V42, R-05 |

Notlar:
- Mesajlarda "(1e-07, 1)" yazmasına rağmen sınırlar 1e-07 ve 0.9999999'dur ve **dahildir** (G*Power mesajı 6 anlamlı basamakla yuvarlıyor). [DOĞRULANDI R-02]
- Post-hoc'ta dz = 0 geçerlidir (5. kontrol yalnızca a-priori). [DOĞRULANDI R-06]
- Kontrollerin hata mesajının **tam metni** puanlanmıyor varsayılır; `error` alanının varlığı ve çıkış kodu esastır. [KARAR]
- Kontrol 2–3 ile 4–5'in kendi aralarındaki sırası G*Power'da ölçülmedi; birden çok hatalı girdide hangi mesajın çıktığı garanti edilmez. [KARAR]

## 5. Hesap modeli [DOĞRULANDI — 27/27 GUI vektörü 7 basamağa kadar; R-08…R-12, R-16]
Girdi: `dz`, `alpha`, `tails ∈ {1,2}`, N (gerçek sayı olabilir; aşağıya bakın).

```
df    = N − 1
δ     = dz · √N                     (işaret korunur)
p     = alpha / tails               (tek kuyruk: α, iki kuyruk: α/2)
t_c   = t⁻¹(1 − p; df)              merkezi t dağılımının ters CDF'si, dz ≥ 0 için
t_c   = t⁻¹(p; df) = −t⁻¹(1 − p; df) dz < 0 için (negatif)
```
Güç, T′ ~ noncentral t(df, δ) için:
- dz ≥ 0, tek kuyruk: `P(T′ > t_c)`
- dz < 0, tek kuyruk: `P(T′ < t_c)`
- iki kuyruk (her işaret): `P(T′ > |t_c|) + P(T′ < −|t_c|)` — **alt kuyruk eklenir** [DOĞRULANDI V03/V11, R-10]

Sonuç: N ve güç |dz| ile aynıdır; yalnızca raporlanan `critical` ve `ncp` dz'nin işaretini alır. [DOĞRULANDI V22, V23, R-16]

### 5.1 Post-hoc
`N_int = floor(N + 0.5)` (en yakın tamsayı, .5 yukarı) ve **tüm hesap N_int ile** yapılır (df = N_int − 1, δ = dz·√N_int). [DOĞRULANDI V34: 10.5→11, V38: 10.2→10, R-15]

### 5.2 A-priori N araması [DOĞRULANDI R-12; 23/23 a-priori vektör]
G*Power N'yi **sürekli** bir değişken olarak ele alır (df ve δ kesirli N ile hesaplanır):
1. `f(x) = güç(x) − power`, x gerçek sayı, x ≥ 2.
2. `f(2) ≥ 0` ise sonuç **N = 2**. [DOĞRULANDI V18, V20]
3. Aksi halde kökü içeren bir üst sınır bul: `hi = 100`; `f(hi) < 0` olduğu sürece `hi = hi · 1.6`.
4. `[2, hi]` aralığında `f(x) = 0` kökünü en az 1e-10 mutlak toleransla bul (Brent önerilir; bisection da olur).
5. `N = ceil( round(x, 10 ondalık) )`; `N < 2` ise `N = 2`. (10 ondalığa yuvarlama, köke çok yakın tamsayıların bir fazlasına sıçramayı önler.)
6. `actual_power = güç(N)` tamsayı N ile yeniden hesaplanır.

Eşdeğerlik notu: güç N'de monoton arttığı için bu yöntem, "güç(N) ≥ power olan en küçük tamsayı N ≥ 2" ile 400 rastgele girdide aynı sonucu verdi. Ancak çok büyük N'lerde (V14: N = 78491) tek tek artırma yavaştır; kök bulma yöntemini kullanın.

### 5.3 Sayısal gereksinimler
- Merkezi t ters CDF ve noncentral t CDF, 7 ondalığa kadar doğru olmalı. scipy (`scipy.stats.t`, `scipy.stats.nct`) yeterlidir. [DOĞRULANDI 27/27]
- **Dikkat (sayısal tuzak):** scipy 1.18'de iki kuyruklu gücün **alt kuyruk** terimi `nct.cdf(−t_c; df, δ)` büyük δ'da `NaN` döndürebilir (ör. dz=1, N=100; dz=20, N=2). Bu terimin gerçek değeri ≈0'dır. **Alt kuyruk NaN ise 0 kullanın.** Üst kuyruğu `nct.sf(t_c)` ile hesaplayın (`1 − cdf` yerine). Gücü NaN için 1 kabul etmek YANLIŞTIR: V41'de N=167 yerine 95 verir. [DOĞRULANDI V41, V43; HALLUCINATIONS H-11]
- Doğrulama için: V41 (α=1e-07, dz=0.5, iki kuyruk, power 0.80) → N=167, güç 0.8048331; V43 (dz=20) → N=2, güç 0.9735240.
- Kesirli df ile t ve noncentral t hesaplanabilmeli (5.2 için).

## 6. Çıktı
Tek satır JSON, standart çıktıya; başarıda çıkış kodu 0. [KESİN]

```
{"n_total":34,"actual_power":0.8078,"critical":2.0345,"df":33,"ncp":2.9155}
```
| Alan | a-priori | post-hoc |
|---|---|---|
| `n_total` | bulunan N | N_int (yuvarlanmış girdi) |
| `actual_power` | güç(N) | hesaplanan güç |
| `critical` | t_c (dz<0 ise negatif) | aynı |
| `df` | N − 1 (tamsayı) | N_int − 1 |
| `ncp` | δ (dz<0 ise negatif) | aynı |

- Alan adları t2-indep örneğinden alındı; t-paired'de `n1`/`n2` yoktur. [KARAR — H-01]
- Ondalık değerler **4 basamağa yuvarlanır** (ödevdeki örnek çıktı biçimi). G*Power ekranı 7 basamak gösterir; değerler 7 basamağa kadar doğru hesaplanmalı ki 4 basamak yuvarlaması da doğru olsun. [KARAR — H-02]
- Hata: `{"error":"<açıklama>"}` ve sıfırdan farklı çıkış kodu (öneri: 2). [KESİN]

## 7. Kabul kriterleri (Gherkin)
Beklenen değerler G*Power 3.1.9.7 ekranından alınmıştır (`oracle/gpower_vectors.csv`). Gerçek sayılar 4 ondalıkta karşılaştırılır; tamsayılar tam eşleşmelidir.

```gherkin
Feature: Eşleştirilmiş örneklem t testi — örneklem büyüklüğü ve güç

  Scenario Outline: A priori N hesabı
    Given test "t-paired" ve mod "a-priori"
    When tails <tails>, dz <dz>, alpha <alpha>, power <power> verilir
    Then n_total <N>, df <df> olmalı
    And actual_power <pw>, critical <tc>, ncp <ncp> olmalı (4 ondalık)

    Examples:
      | id  | tails | dz   | alpha | power | N     | df    | pw     | tc      | ncp     |
      | V01 | 2     | 0.5  | 0.05  | 0.80  | 34    | 33    | 0.8078 | 2.0345  | 2.9155  |
      | V02 | 2     | 0.5  | 0.05  | 0.95  | 54    | 53    | 0.9502 | 2.0057  | 3.6742  |
      | V03 | 1     | 0.5  | 0.05  | 0.80  | 27    | 26    | 0.8118 | 1.7056  | 2.5981  |
      | V04 | 2     | 0.2  | 0.05  | 0.80  | 199   | 198   | 0.8017 | 1.9720  | 2.8213  |
      | V10 | 2     | 0.5  | 0.01  | 0.80  | 51    | 50    | 0.8094 | 2.6778  | 3.5707  |
      | V12 | 1     | 0.3  | 0.01  | 0.99  | 244   | 243   | 0.9902 | 2.3418  | 4.6861  |
      | V14 | 2     | 0.01 | 0.05  | 0.80  | 78491 | 78490 | 0.8000 | 1.9600  | 2.8016  |
      | V15 | 2     | 3    | 0.05  | 0.80  | 4     | 3     | 0.9670 | 3.1824  | 6.0000  |
      | V16 | 2     | 5    | 0.05  | 0.95  | 3     | 2     | 0.9755 | 4.3027  | 8.6603  |
      | V18 | 2     | 0.5  | 0.05  | 0.05  | 2     | 1     | 0.0619 | 12.7062 | 0.7071  |
      | V20 | 1     | 0.5  | 0.05  | 0.05  | 2     | 1     | 0.1058 | 6.3138  | 0.7071  |
      | V22 | 2     | -0.5 | 0.05  | 0.80  | 34    | 33    | 0.8078 | -2.0345 | -2.9155 |
      | V23 | 1     | -0.5 | 0.05  | 0.80  | 27    | 26    | 0.8118 | -1.7056 | -2.5981 |
      | V41 | 2     | 0.5  | 0.0000001 | 0.80 | 167 | 166   | 0.8048 | 5.5717  | 6.4614  |
      | V43 | 2     | 20   | 0.05  | 0.80  | 2     | 1     | 0.9735 | 12.7062 | 28.2843 |

  Scenario Outline: Post hoc güç hesabı
    Given test "t-paired" ve mod "post-hoc"
    When tails <tails>, dz <dz>, alpha <alpha>, n <n> verilir
    Then n_total <N>, df <df>, actual_power <pw>, critical <tc>, ncp <ncp> olmalı

    Examples:
      | id  | tails | dz  | alpha | n    | N  | df | pw     | tc     | ncp    |
      | V27 | 2     | 0.5 | 0.05  | 35   | 35 | 34 | 0.8195 | 2.0322 | 2.9580 |
      | V28 | 1     | 0.5 | 0.05  | 35   | 35 | 34 | 0.8950 | 1.6909 | 2.9580 |
      | V29 | 2     | 0.5 | 0.05  | 20   | 20 | 19 | 0.5645 | 2.0930 | 2.2361 |
      | V34 | 2     | 0.5 | 0.05  | 10.5 | 11 | 10 | 0.3232 | 2.2281 | 1.6583 |
      | V38 | 2     | 0.5 | 0.05  | 10.2 | 10 | 9  | 0.2932 | 2.2622 | 1.5811 |
      | V39 | 2     | 0.5 | 0.05  | 3    | 3  | 2  | 0.0841 | 4.3027 | 0.8660 |
      | V42 | 2     | 0.5 | 0.05  | 2.6  | 3  | 2  | 0.0841 | 4.3027 | 0.8660 |

  Scenario Outline: Geçersiz girdi
    Given test "t-paired" ve mod "<mode>"
    When <girdi> verilir
    Then çıktı yalnızca "error" alanı içermeli ve çıkış kodu 0 olmamalıdır

    Examples:
      | id  | mode     | girdi                                    |
      | V19 | a-priori | tails 2, dz 0.5, alpha 0.05, power 0.04  |
      | V21 | a-priori | tails 2, dz 0, alpha 0.05, power 0.80    |
      | V24 | a-priori | tails 2, dz 0.5, alpha 0, power 0.80     |
      | V25 | a-priori | tails 2, dz 0.5, alpha 1, power 0.80     |
      | V26 | a-priori | tails 2, dz 0.5, alpha 0.05, power 1     |
      | V32 | post-hoc | tails 2, dz 0.5, alpha 0.05, n 2         |
      | V33 | post-hoc | tails 2, dz 0.5, alpha 0.05, n 1         |
      | V40 | a-priori | tails 2, dz 20.1, alpha 0.05, power 0.80 |
      | -   | a-priori | tails 3, dz 0.5, alpha 0.05, power 0.80  |
      | -   | a-priori | --power eksik                            |
      | -   | a-priori | dz "abc"                                 |

  Scenario: Test ailesi karışmaz
    Given test "t-paired", mod "a-priori", tails 2, dz 0.5, alpha 0.05, power 0.80
    Then çıktıda "n1" ve "n2" alanları bulunmamalı
    And df, n_total − 1'e eşit olmalı
```
Tam vektör listesi (30 hesaplı + 8 hatalı; §7 tabloları bunların bir alt kümesidir): `oracle/gpower_vectors.csv`. Diferansiyel test hepsini kullanmalıdır.

## 8. Sınır durumları özeti
| Durum | Beklenen | Kanıt |
|---|---|---|
| power = alpha | Geçerli; a-priori N = 2 | V18, V20 |
| Çok büyük dz | Küçük N (≥ 2), actual_power hedefin çok üstünde olabilir | V15, V16, V17 |
| Çok küçük dz (0.01) | Büyük N (78491); arama hızlı bitmeli | V14 |
| Negatif dz | N ve güç pozitifle aynı; critical ve ncp negatif | V22, V23 |
| Kesirli N (post-hoc) | En yakın tamsayı, .5 yukarı | V34, V38 |
| N = 3 (post-hoc) | Geçerli | V39 |
| a-priori'nin N=2 sonucu post-hoc'a girilirse | Hata (alt sınır 3) — G*Power'ın kendi tutarsızlığı, aynen taklit edilir | V18 + V32, R-18 |

## 9. Açık kalan noktalar
Kod yazımını engelleyen açık madde yok. Aşağıdakiler bilinçli tasarım kararlarıdır:
1. Bayrak adları ve JSON alanları: CONTRACT.md yok; t2-indep örneğinden türetildi ve eş adlar kabul ediliyor (§3, H-01).
2. Çıktı 4 ondalık (§6, H-02).
3. Birden fazla hatalı girdide hangi mesajın önce çıktığı yalnızca kısmen bilinir (§4).
