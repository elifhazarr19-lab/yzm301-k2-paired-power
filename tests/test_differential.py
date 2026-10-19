"""G*Power kara kutu vektörlerine karşı diferansiyel test.

Kaynak: oracle/gpower_vectors.csv (G*Power 3.1.9.7 arayüzünden elle toplandı).
Her satır CLI üzerinden çalıştırılır; motor doğrudan çağrılmaz.

Karşılaştırma kuralı: N ve df tam eşleşmeli. Diğer değerler motorun tam
hassasiyetli çıktısının 7 ondalığa yuvarlanmış hali ile G*Power'ın 7 ondalık
değerine tam eşit olmalı (CLI'nın gizli --precision 7 seçeneği).
"""

import csv
import json
import math
from pathlib import Path

import pytest

from pairedpower.cli import main

ORACLE = Path(__file__).resolve().parent.parent / "oracle" / "gpower_vectors.csv"
PRECISION = "7"

STATUS_OK = "GUI-TOPLANDI"
STATUS_ERROR = "GUI-TOPLANDI-HATA"


def load_rows():
    with ORACLE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_args(row):
    args = [
        "--test", "t-paired",
        "--mode", row["mode"],
        "--tails", row["tails"],
        "--dz", row["dz"],
        "--alpha", row["alpha"],
        "--precision", PRECISION,
    ]
    if row["mode"] == "a-priori":
        args += ["--power", row["power"]]
    else:
        args += ["--n", row["n_input"]]
    return args


def run_cli(capsys, args):
    code = main(args)
    out = capsys.readouterr().out
    return code, json.loads(out)


def expected_n_int(n_input):
    # SPEC §5.1: N_int = floor(N + 0.5)
    return math.floor(float(n_input) + 0.5)


OK_ROWS = [r for r in load_rows() if r["status"] == STATUS_OK]
ERROR_ROWS = [r for r in load_rows() if r["status"] == STATUS_ERROR]


@pytest.mark.parametrize("row", [pytest.param(r, id=r["id"]) for r in OK_ROWS])
def test_gui_vector(capsys, row):
    code, out = run_cli(capsys, build_args(row))

    assert code == 0

    if row["mode"] == "a-priori":
        assert out["n_total"] == int(row["gp_n_total"])
        assert out["df"] == int(row["gp_df"])
    else:
        n_int = expected_n_int(row["n_input"])
        assert out["n_total"] == n_int
        assert out["df"] == int(row["gp_df"])
        assert out["df"] == n_int - 1

    assert out["actual_power"] == float(row["gp_actual_power"])
    assert out["critical"] == float(row["gp_critical_t"])
    assert out["ncp"] == float(row["gp_ncp"])


@pytest.mark.parametrize("row", [pytest.param(r, id=r["id"]) for r in ERROR_ROWS])
def test_gui_error_vector(capsys, row):
    code, out = run_cli(capsys, build_args(row))

    assert code != 0
    assert set(out) == {"error"}
    assert out["error"]
