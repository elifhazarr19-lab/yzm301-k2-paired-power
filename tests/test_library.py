"""statsmodels kütüphane vektörlerine karşı test.

Kaynak: oracle/library_vectors.csv (tests/gen_library_vectors.py ile üretildi).

- Post-hoc: motorun gücü ile statsmodels gücü 1e-6 içinde olmalı. statsmodels NaN
  döndürdüğü satırlarda (alt kuyruk NaN sorunu, SPEC §5.3) ayrı bir test, motorun
  değerini bağımsız bir referansla (alt kuyruk ≈ 0) doğrular.
- A-priori: ceil(statsmodels N) ile bizim N karşılaştırılır. Farklı çıkan satırlarda
  statsmodels'in kökü gerçek bir kök değildir; bu, kütüphanenin kök bulucusunun
  hatasıdır, yuvarlama farkı değildir. Her satırda bizim N'in sınır koşulunu
  (güç(N) ≥ hedef, güç(N−1) < hedef) sağladığı da ayrıca doğrulanır.
- statsmodels iki kuyruklu gücün alt kuyruğunu dahil ediyor mu, bunu ölçer.
"""

import csv
import math
from pathlib import Path

import pytest
from scipy import stats

from pairedpower import engine

ORACLE = Path(__file__).resolve().parent.parent / "oracle" / "library_vectors.csv"
POWER_TOL = 1e-6
ROOT_TOL = 1e-6  # statsmodels kökü gerçek kök mu: güç(sm_N) hedeften bu kadar sapıyorsa değil


def load_rows():
    with ORACLE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def is_nan_value(text):
    return text == "" or math.isnan(float(text))


def ref_power(dz, alpha, tails, n):
    """Bağımsız referans: SPEC §5 formülü, scipy ile doğrudan (motor fonksiyonu kullanılmaz)."""
    df = n - 1
    tc = stats.t.isf(alpha / tails, df)
    d = dz * math.sqrt(n)
    if tails == 1:
        return float(stats.nct.sf(tc, df, d))
    lower = stats.nct.cdf(-tc, df, d)
    if math.isnan(lower):
        lower = 0.0
    return float(stats.nct.sf(tc, df, d) + lower)


POSTHOC_ROWS = [r for r in load_rows() if r["mode"] == "post-hoc"]
APRIORI_ROWS = [r for r in load_rows() if r["mode"] == "a-priori"]

POSTHOC_FINITE = [r for r in POSTHOC_ROWS if not is_nan_value(r["sm_power"])]
POSTHOC_NAN = [r for r in POSTHOC_ROWS if is_nan_value(r["sm_power"])]
APRIORI_FINITE = [r for r in APRIORI_ROWS if not is_nan_value(r["sm_n_frac"])]
APRIORI_NAN = [r for r in APRIORI_ROWS if is_nan_value(r["sm_n_frac"])]


def row_id(row):
    return row["id"]


@pytest.mark.parametrize("row", [pytest.param(r, id=row_id(r)) for r in POSTHOC_FINITE])
def test_posthoc_power_matches_statsmodels(row):
    n = int(row["n_input"])
    ours = engine.post_hoc(int(row["tails"]), float(row["dz"]), float(row["alpha"]), n).actual_power

    assert abs(ours - float(row["sm_power"])) <= POWER_TOL


@pytest.mark.parametrize("row", [pytest.param(r, id=row_id(r)) for r in POSTHOC_NAN])
def test_posthoc_statsmodels_nan_rows(row):
    # statsmodels NaN döndürüyor; motorun değeri alt kuyruğu 0 sayan referansla eşleşmeli.
    n = int(row["n_input"])
    ours = engine.post_hoc(int(row["tails"]), float(row["dz"]), float(row["alpha"]), n).actual_power

    assert abs(ours - ref_power(float(row["dz"]), float(row["alpha"]), int(row["tails"]), n)) <= POWER_TOL


def boundary_holds(tails, dz, alpha, power, n):
    if n == 2:
        return ref_power(dz, alpha, tails, 2) >= power
    return ref_power(dz, alpha, tails, n) >= power and ref_power(dz, alpha, tails, n - 1) < power


@pytest.mark.parametrize("row", [pytest.param(r, id=row_id(r)) for r in APRIORI_FINITE])
def test_apriori_ceil_matches_statsmodels_or_root_is_invalid(row):
    tails = int(row["tails"])
    dz = float(row["dz"])
    alpha = float(row["alpha"])
    power = float(row["power"])
    sm_n = float(row["sm_n_frac"])

    ours = engine.a_priori(tails, dz, alpha, power).n_total

    assert boundary_holds(tails, dz, alpha, power, ours)
    if ours == math.ceil(sm_n):
        return
    # Farklılık varsa statsmodels'in kökü gerçek kök olmamalı.
    assert abs(ref_power(dz, alpha, tails, sm_n) - power) > ROOT_TOL


@pytest.mark.parametrize("row", [pytest.param(r, id=row_id(r)) for r in APRIORI_NAN])
def test_apriori_statsmodels_nan_rows(row):
    # statsmodels kök bulamadı (NaN); bizim N yine sınır koşulunu sağlamalı.
    tails = int(row["tails"])
    dz = float(row["dz"])
    alpha = float(row["alpha"])
    power = float(row["power"])

    ours = engine.a_priori(tails, dz, alpha, power).n_total

    assert boundary_holds(tails, dz, alpha, power, ours)


def test_statsmodels_two_sided_includes_lower_tail():
    # Alt kuyruğun etkisinin belirgin olduğu bir girdi: küçük N ve küçük dz (alt kuyruk ≈ 0.022).
    dz, alpha, n = 0.05, 0.05, 3
    tc = stats.t.isf(alpha / 2, n - 1)
    d = dz * math.sqrt(n)
    upper_only = float(stats.nct.sf(tc, n - 1, d))
    with_lower = ref_power(dz, alpha, 2, n)

    from statsmodels.stats.power import TTestPower

    sm_two = float(TTestPower().power(effect_size=dz, nobs=n, alpha=alpha, alternative="two-sided"))

    assert with_lower - upper_only > 1e-4  # alt kuyruk önemli
    assert abs(sm_two - with_lower) <= POWER_TOL  # statsmodels iki kuyruk = üst + alt
    assert abs(sm_two - upper_only) > 1e-4  # ve alt kuyruğu atlamıyor
