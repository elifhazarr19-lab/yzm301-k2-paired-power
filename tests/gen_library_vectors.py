"""statsmodels ile kütüphane referans vektörleri üretir → oracle/library_vectors.csv.

Eşleştirilmiş t testi, statsmodels'ta tek örneklem t testi olarak modellenir
(fark puanları üzerinde; effect_size = dz, nobs = çift sayısı).

Çalıştırma (proje kökünden):
    python tests/gen_library_vectors.py
"""

import csv
import random
from pathlib import Path

from statsmodels.stats.power import TTestPower

SEED = 20261019
N_PER_MODE = 500
DZ_RANGE = (0.05, 2.5)
ALPHAS = (0.001, 0.01, 0.05, 0.10)
POWER_RANGE = (0.5, 0.99)
POSTHOC_N_RANGE = (3, 500)
TAILS_VALUES = (1, 2)

OUT = Path(__file__).resolve().parent.parent / "oracle" / "library_vectors.csv"
FIELDS = ["id", "mode", "tails", "dz", "alpha", "power", "n_input", "sm_n_frac", "sm_power", "sm_status"]

# statsmodels: iki kuyrukta "two-sided", tek kuyrukta dz > 0 için "larger".
ALTERNATIVE = {1: "larger", 2: "two-sided"}


def apriori_inputs(rng):
    for i in range(N_PER_MODE):
        yield {
            "id": f"L-A{i + 1:03d}",
            "mode": "a-priori",
            "tails": rng.choice(TAILS_VALUES),
            "dz": round(rng.uniform(*DZ_RANGE), 6),
            "alpha": rng.choice(ALPHAS),
            "power": round(rng.uniform(*POWER_RANGE), 6),
            "n_input": "",
        }


def posthoc_inputs(rng):
    for i in range(N_PER_MODE):
        yield {
            "id": f"L-P{i + 1:03d}",
            "mode": "post-hoc",
            "tails": rng.choice(TAILS_VALUES),
            "dz": round(rng.uniform(*DZ_RANGE), 6),
            "alpha": rng.choice(ALPHAS),
            "power": "",
            "n_input": rng.randint(*POSTHOC_N_RANGE),
        }


def solve_apriori(row, model):
    try:
        n_frac = model.solve_power(
            effect_size=row["dz"],
            power=row["power"],
            alpha=row["alpha"],
            alternative=ALTERNATIVE[row["tails"]],
        )
        return float(n_frac), "", "OK"
    except Exception as exc:  # statsmodels kökü bulamazsa kaydı düşürmek yerine işaretle
        return "", "", f"SM-HATA: {type(exc).__name__}"


def power_posthoc(row, model):
    try:
        pw = model.power(
            effect_size=row["dz"],
            nobs=row["n_input"],
            alpha=row["alpha"],
            alternative=ALTERNATIVE[row["tails"]],
        )
        return "", float(pw), "OK"
    except Exception as exc:
        return "", "", f"SM-HATA: {type(exc).__name__}"


def main():
    rng = random.Random(SEED)
    model = TTestPower()
    rows = []
    for row in apriori_inputs(rng):
        n_frac, _, status = solve_apriori(row, model)
        rows.append({**row, "sm_n_frac": n_frac, "sm_power": "", "sm_status": status})
    for row in posthoc_inputs(rng):
        _, pw, status = power_posthoc(row, model)
        rows.append({**row, "sm_n_frac": "", "sm_power": pw, "sm_status": status})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} satır yazıldı: {OUT}")


if __name__ == "__main__":
    main()
