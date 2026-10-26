"""G*Power 3.1 kılavuzundaki matched-pairs örneklerine karşı test.

Kaynak: oracle/manual_vectors.csv (kılavuz §19.3, s. 48).
Kılavuz değerleri 6 ondalıkla veriyor; CLI çıktısı 6 ondalığa yuvarlanıp karşılaştırılır.
N ve df tam eşleşmeli. Kılavuzun vermediği alanlar (boş hücre) karşılaştırılmaz.
"""

import csv
import json
from pathlib import Path

import pytest

from pairedpower.cli import main

ORACLE = Path(__file__).resolve().parent.parent / "oracle" / "manual_vectors.csv"

with ORACLE.open(encoding="utf-8", newline="") as fh:
    ROWS = list(csv.DictReader(fh))


@pytest.mark.parametrize("row", [pytest.param(r, id=r["id"]) for r in ROWS])
def test_manual_example(capsys, row):
    args = [
        "--test", "t-paired",
        "--mode", row["mode"],
        "--tails", row["tails"],
        "--dz", row["dz"],
        "--alpha", row["alpha"],
        "--n", row["n_input"],
        "--precision", "7",
    ]
    assert main(args) == 0
    out = json.loads(capsys.readouterr().out)

    assert out["n_total"] == int(row["m_n_total"])
    if row["m_df"]:
        assert out["df"] == int(row["m_df"])
    for field, column in (
        ("actual_power", "m_actual_power"),
        ("critical", "m_critical_t"),
        ("ncp", "m_ncp"),
    ):
        if row[column]:
            assert round(out[field], 6) == float(row[column])
