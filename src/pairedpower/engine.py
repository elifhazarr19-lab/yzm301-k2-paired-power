"""Eşleştirilmiş örneklem t testi için saf hesap motoru.

G/Ç yok; CLI (cli.py) ve MCP sunucusu (mcp_server.py) aynı `calculate`/`solve`
yolunu çağırır. Doğrulama sırası ve hesap modeli SPEC.md §4, §5 ve §5.1–§5.3'e
birebir uyar. `Result` tam hassasiyetle döner; yuvarlama `to_dict` içinde yapılır.
"""

import math
from dataclasses import dataclass

from scipy import stats
from scipy.optimize import brentq

ALPHA_MIN = 1e-7
ALPHA_MAX = 0.9999999
POWER_MIN = 1e-7
POWER_MAX = 0.9999999
DZ_LIMIT = 20.0
DZ_ZERO_TOLERANCE = 0.00001
N_MIN = 3
N_MAX = 2147483646
TAILS_VALUES = (1, 2)
MODES = ("a-priori", "post-hoc")
DECIMALS = 4  # SPEC §6: çıktı 4 ondalık

# A-priori N araması (SPEC §5.2)
SEARCH_START = 2.0
SEARCH_INITIAL_HI = 100.0
SEARCH_GROWTH = 1.6
SEARCH_XTOL = 1e-10
SEARCH_ROUND_DIGITS = 10


class InputError(ValueError):
    """Girdi SPEC §4 doğrulama kurallarından birini ihlal ediyor."""


@dataclass(frozen=True)
class Result:
    n_total: int
    actual_power: float
    critical: float
    df: int
    ncp: float


def a_priori(tails, dz, alpha, power):
    """Hedef güç için gereken N'yi ve gerçekleşen gücü hesaplar (SPEC §2, §4, §5.2)."""
    check_tails(tails)
    _check_alpha(alpha)  # §4 kontrol 1
    _check_power(power)  # §4 kontrol 2
    if power < alpha:  # §4 kontrol 3
        raise InputError("Power must be greater than or equal to alpha.")
    _check_dz(dz)  # §4 kontrol 4
    if abs(dz) < DZ_ZERO_TOLERANCE:  # §4 kontrol 5
        raise InputError(
            "In an a priori analysis, the absolute value of the effect size must be greater than 0.00001."
        )
    n = _solve_n(dz, alpha, tails, power)
    return _result(dz, alpha, tails, n)


def post_hoc(tails, dz, alpha, n):
    """Verilen N için gücü hesaplar; N en yakın tamsayıya yuvarlanır (SPEC §2, §4, §5.1)."""
    check_tails(tails)
    _check_alpha(alpha)  # §4 kontrol 1
    _check_dz(dz)  # §4 kontrol 4
    n_int = _round_n(n)  # §4 kontrol 6
    if not (N_MIN <= n_int <= N_MAX):
        raise InputError("Total sample size is outside the admissible range (3, 2147483646).")
    return _result(dz, alpha, tails, n_int)


def solve(mode, tails, dz, alpha, power=None, n=None):
    """Mod seçimi ve zorunlu alan kontrolü; CLI ve MCP bu tek yolu kullanır (SPEC §3.1 (3), (7))."""
    check_tails(tails)  # §3.1 (3): tails kontrolü önce
    for label, value in (("tails", tails), ("dz", dz), ("alpha", alpha), ("power", power), ("n", n)):
        # §3.1 (2): inf, -inf, nan sayı olarak kabul edilmez.
        if value is not None and not math.isfinite(value):
            raise InputError(f"{label}: not a finite number: {value!r}")
    if mode not in MODES:
        raise InputError(f"mode must be one of: {', '.join(MODES)}")
    if dz is None:
        raise InputError("the following arguments are required: --dz")
    if alpha is None:
        raise InputError("the following arguments are required: --alpha")
    if mode == "a-priori":
        # Moda ait olmayan alan (n) yok sayılır (SPEC §3).
        if power is None:
            raise InputError("the following arguments are required: --power")
        return a_priori(tails, dz, alpha, power)
    # Moda ait olmayan alan (power) yok sayılır (SPEC §3).
    if n is None:
        raise InputError("the following arguments are required: --n")
    return post_hoc(tails, dz, alpha, n)


def to_dict(result, decimals=DECIMALS):
    """SPEC §6 çıktı sözlüğü; ondalıklar `decimals` basamağa yuvarlanır."""
    return {
        "n_total": result.n_total,
        "actual_power": _round(result.actual_power, decimals),
        "critical": _round(result.critical, decimals),
        "df": result.df,
        "ncp": _round(result.ncp, decimals),
    }


def calculate(mode, tails, dz, alpha, power=None, n=None, decimals=DECIMALS):
    """Girdi → sonuç sözlüğü. Hatada {"error": ...} döner (SPEC §6)."""
    try:
        return to_dict(solve(mode, tails, dz, alpha, power, n), decimals)
    except InputError as exc:
        return {"error": str(exc)}


def _round(value, decimals):
    # + 0.0, -0.0 değerinin JSON'da "-0.0" olarak çıkmasını önler.
    return round(value, decimals) + 0.0


def _result(dz, alpha, tails, n):
    df = n - 1
    tc = stats.t.isf(alpha / tails, df)
    return Result(
        n_total=n,
        actual_power=_power(dz, alpha, tails, n),
        critical=float(tc if dz >= 0 else -tc),  # SPEC §6: dz < 0 ise negatif
        df=df,
        ncp=dz * math.sqrt(n),
    )


def _power(dz, alpha, tails, n):
    """Güç(N) — SPEC §5. df = N − 1, δ = dz·√N; N kesirli olabilir."""
    df = n - 1
    tc = stats.t.isf(alpha / tails, df)  # t_c'nin mutlak değeri
    delta = dz * math.sqrt(n)
    if tails == 1:
        if dz >= 0:
            return float(stats.nct.sf(tc, df, delta))
        return float(stats.nct.cdf(-tc, df, delta))
    upper = stats.nct.sf(tc, df, delta)
    lower = stats.nct.cdf(-tc, df, delta)
    if math.isnan(lower):  # SPEC §5.3 sayısal tuzak: alt kuyruk NaN ise gerçek değeri ≈0
        lower = 0.0
    return float(upper + lower)


def _solve_n(dz, alpha, tails, target):
    """SPEC §5.2: güç(x) = target kökünü bulup tamsayıya yukarı yuvarlar."""

    def gap(x):
        g = _power(dz, alpha, tails, x) - target
        # SPEC §3.1 (6): arama NaN üretirse hata.
        if math.isnan(g):
            raise InputError("Power could not be computed during the sample size search.")
        return g

    if gap(SEARCH_START) >= 0:
        return 2

    hi = SEARCH_INITIAL_HI
    while gap(hi) < 0:
        # SPEC §3.1 (5): kök admissible aralığın dışındaysa hata.
        if hi > N_MAX:
            raise InputError("Required sample size is outside the admissible range (3, 2147483646).")
        hi *= SEARCH_GROWTH

    root = brentq(gap, SEARCH_START, hi, xtol=SEARCH_XTOL)
    n = max(math.ceil(round(root, SEARCH_ROUND_DIGITS)), 2)
    # SPEC §3.1 (5): bulunan N 2147483646'yı aşarsa hata.
    if n > N_MAX:
        raise InputError("Required sample size is outside the admissible range (3, 2147483646).")
    return n


def _round_n(n):
    # SPEC §3.1 (6): sonsuz ya da NaN N hatadır; metin önemsiz.
    if not math.isfinite(n):
        raise InputError("Total sample size is outside the admissible range (3, 2147483646).")
    return math.floor(n + 0.5)


def check_tails(tails):
    """SPEC §3.1 (3): tails bayrak okumasının parçası; §4 kontrollerinden önce yapılır."""
    if tails not in TAILS_VALUES:
        raise InputError("Tails must be 1 or 2.")


def _check_alpha(alpha):
    if not (ALPHA_MIN <= alpha <= ALPHA_MAX):
        raise InputError("Alpha is outside the admissible range (1e-07, 1).")


def _check_power(power):
    if not (POWER_MIN <= power <= POWER_MAX):
        raise InputError("Power is outside the admissible range (1e-07, 1).")


def _check_dz(dz):
    if not (-DZ_LIMIT <= dz <= DZ_LIMIT):
        raise InputError("Effect size d is outside the admissible range (-20, 20).")
