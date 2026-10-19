"""SPEC.md §7 Gherkin senaryolarının pytest karşılığı.

Her Examples satırı ayrı bir test. Çıktı yalnızca CLI üzerinden (cli.main) okunur.
"""

import json

import pytest

from pairedpower.cli import main

# id, tails, dz, alpha, power, N, df, pw, tc, ncp
A_PRIORI_ROWS = [
    ("V01", 2, 0.5, 0.05, 0.80, 34, 33, 0.8078, 2.0345, 2.9155),
    ("V02", 2, 0.5, 0.05, 0.95, 54, 53, 0.9502, 2.0057, 3.6742),
    ("V03", 1, 0.5, 0.05, 0.80, 27, 26, 0.8118, 1.7056, 2.5981),
    ("V04", 2, 0.2, 0.05, 0.80, 199, 198, 0.8017, 1.9720, 2.8213),
    ("V10", 2, 0.5, 0.01, 0.80, 51, 50, 0.8094, 2.6778, 3.5707),
    ("V12", 1, 0.3, 0.01, 0.99, 244, 243, 0.9902, 2.3418, 4.6861),
    ("V14", 2, 0.01, 0.05, 0.80, 78491, 78490, 0.8000, 1.9600, 2.8016),
    ("V15", 2, 3, 0.05, 0.80, 4, 3, 0.9670, 3.1824, 6.0000),
    ("V16", 2, 5, 0.05, 0.95, 3, 2, 0.9755, 4.3027, 8.6603),
    ("V18", 2, 0.5, 0.05, 0.05, 2, 1, 0.0619, 12.7062, 0.7071),
    ("V20", 1, 0.5, 0.05, 0.05, 2, 1, 0.1058, 6.3138, 0.7071),
    ("V22", 2, -0.5, 0.05, 0.80, 34, 33, 0.8078, -2.0345, -2.9155),
    ("V23", 1, -0.5, 0.05, 0.80, 27, 26, 0.8118, -1.7056, -2.5981),
    ("V41", 2, 0.5, 0.0000001, 0.80, 167, 166, 0.8048, 5.5717, 6.4614),
    ("V43", 2, 20, 0.05, 0.80, 2, 1, 0.9735, 12.7062, 28.2843),
]

# id, tails, dz, alpha, n, N, df, pw, tc, ncp
POST_HOC_ROWS = [
    ("V27", 2, 0.5, 0.05, 35, 35, 34, 0.8195, 2.0322, 2.9580),
    ("V28", 1, 0.5, 0.05, 35, 35, 34, 0.8950, 1.6909, 2.9580),
    ("V29", 2, 0.5, 0.05, 20, 20, 19, 0.5645, 2.0930, 2.2361),
    ("V34", 2, 0.5, 0.05, 10.5, 11, 10, 0.3232, 2.2281, 1.6583),
    ("V38", 2, 0.5, 0.05, 10.2, 10, 9, 0.2932, 2.2622, 1.5811),
    ("V39", 2, 0.5, 0.05, 3, 3, 2, 0.0841, 4.3027, 0.8660),
    ("V42", 2, 0.5, 0.05, 2.6, 3, 2, 0.0841, 4.3027, 0.8660),
]

A_PRIORI_BASE = ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "0.80"]

# id, argüman listesi (--test t-paired dışında)
INVALID_ROWS = [
    ("V19", ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "0.04"]),
    ("V21", ["--mode", "a-priori", "--tails", "2", "--dz", "0", "--alpha", "0.05", "--power", "0.80"]),
    ("V24", ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0", "--power", "0.80"]),
    ("V25", ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "1", "--power", "0.80"]),
    ("V26", ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "1"]),
    ("V32", ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--n", "2"]),
    ("V33", ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--n", "1"]),
    ("V40", ["--mode", "a-priori", "--tails", "2", "--dz", "20.1", "--alpha", "0.05", "--power", "0.80"]),
    ("G-tails-3", ["--mode", "a-priori", "--tails", "3", "--dz", "0.5", "--alpha", "0.05", "--power", "0.80"]),
    ("G-power-eksik", ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05"]),
    ("G-dz-abc", ["--mode", "a-priori", "--tails", "2", "--dz", "abc", "--alpha", "0.05", "--power", "0.80"]),
]


def run_cli(capsys, args):
    code = main(["--test", "t-paired", *args])
    out = json.loads(capsys.readouterr().out)
    return code, out


@pytest.mark.parametrize(
    "tails, dz, alpha, power, n, df, pw, tc, ncp",
    [pytest.param(*row[1:], id=row[0]) for row in A_PRIORI_ROWS],
)
def test_a_priori(capsys, tails, dz, alpha, power, n, df, pw, tc, ncp):
    args = [
        "--mode", "a-priori",
        "--tails", str(tails),
        "--dz", str(dz),
        "--alpha", str(alpha),
        "--power", str(power),
    ]
    code, out = run_cli(capsys, args)

    assert code == 0
    assert out["n_total"] == n
    assert out["df"] == df
    assert out["actual_power"] == pw
    assert out["critical"] == tc
    assert out["ncp"] == ncp


@pytest.mark.parametrize(
    "tails, dz, alpha, n, N, df, pw, tc, ncp",
    [pytest.param(*row[1:], id=row[0]) for row in POST_HOC_ROWS],
)
def test_post_hoc(capsys, tails, dz, alpha, n, N, df, pw, tc, ncp):
    args = [
        "--mode", "post-hoc",
        "--tails", str(tails),
        "--dz", str(dz),
        "--alpha", str(alpha),
        "--n", str(n),
    ]
    code, out = run_cli(capsys, args)

    assert code == 0
    assert out["n_total"] == N
    assert out["df"] == df
    assert out["actual_power"] == pw
    assert out["critical"] == tc
    assert out["ncp"] == ncp


@pytest.mark.parametrize("args", [pytest.param(a, id=i) for i, a in INVALID_ROWS])
def test_invalid_input(capsys, args):
    code, out = run_cli(capsys, args)

    assert code != 0
    assert set(out) == {"error"}


def test_test_family_does_not_mix(capsys):
    code, out = run_cli(capsys, A_PRIORI_BASE)

    assert code == 0
    assert "n1" not in out
    assert "n2" not in out
    assert out["df"] == out["n_total"] - 1


# SPEC §3.1 (v1.1) kararları.

def test_error_goes_to_stdout_only(capsys):
    code = main(["--test", "t-paired", "--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "0.04"])
    captured = capsys.readouterr()

    assert code != 0
    assert json.loads(captured.out).keys() == {"error"}
    assert captured.err == ""


@pytest.mark.parametrize("value", ["inf", "-inf", "+inf", "nan", "NaN", "Infinity"])
def test_non_finite_numbers_are_rejected(capsys, value):
    code, out = run_cli(capsys, ["--mode", "a-priori", "--tails", "2", "--dz", value, "--alpha", "0.05", "--power", "0.80"])

    assert code != 0
    assert set(out) == {"error"}


def test_tails_is_checked_before_missing_flags(capsys):
    # tails geçersiz ve --power eksik: §3.1 (3) gereği önce tails hatası.
    code, out = run_cli(capsys, ["--mode", "a-priori", "--tails", "3", "--dz", "0.5", "--alpha", "0.05"])

    assert code != 0
    assert "Tails" in out["error"]


def test_n_aliases_with_different_values_are_error(capsys):
    code, out = run_cli(capsys, ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--n", "35", "--n-total", "30"])

    assert code != 0
    assert set(out) == {"error"}


def test_n_aliases_with_same_value_are_accepted(capsys):
    code, out = run_cli(capsys, ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--n", "35", "--n_total", "35"])

    assert code == 0
    assert out["n_total"] == 35


def test_apriori_n_above_limit_is_error(capsys):
    # dz çok küçük: gerekli N 2147483646'yı aşıyor (§3.1 (5)).
    code, out = run_cli(capsys, ["--mode", "a-priori", "--tails", "2", "--dz", "0.00005", "--alpha", "0.05", "--power", "0.80"])

    assert code != 0
    assert set(out) == {"error"}


def test_non_finite_n_is_error_in_engine():
    from pairedpower import engine

    with pytest.raises(engine.InputError):
        engine.post_hoc(2, 0.5, 0.05, float("inf"))


# Ek testler: SPEC §3'teki eş ad ve yok sayma kuralları.

def test_dz_alias_d_is_accepted(capsys):
    args = ["--mode", "post-hoc", "--tails", "2", "--d", "0.5", "--alpha", "0.05", "--n", "35"]
    code, out = run_cli(capsys, args)

    assert code == 0
    assert out["actual_power"] == 0.8195


def test_conflicting_dz_and_d_is_error(capsys):
    args = ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--d", "0.3", "--alpha", "0.05", "--n", "35"]
    code, out = run_cli(capsys, args)

    assert code != 0
    assert set(out) == {"error"}


def test_n_flag_is_ignored_in_a_priori(capsys):
    code, out = run_cli(capsys, [*A_PRIORI_BASE, "--n", "999"])

    assert code == 0
    assert out["n_total"] == 34


def test_power_flag_is_ignored_in_post_hoc(capsys):
    args = ["--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--n", "35", "--power", "0.99"]
    code, out = run_cli(capsys, args)

    assert code == 0
    assert out["n_total"] == 35
