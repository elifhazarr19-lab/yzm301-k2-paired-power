"""Komut satırı arayüzü: argüman okuma, doğrulama, JSON çıktısı (SPEC §3, §6)."""

import argparse
import json
import math
import sys

from pairedpower import engine

TEST_NAME = "t-paired"
MODES = ("a-priori", "post-hoc")
DECIMALS = 4
EXIT_OK = 0
EXIT_ERROR = 2


class ArgError(Exception):
    """Argüman okuma ya da bayrak düzeyindeki hata."""


class _Parser(argparse.ArgumentParser):
    # argparse varsayılan olarak usage'ı stderr'e basıp çıkar; SPEC'in {"error": ...} sözleşmesi için istisna fırlatıyoruz.
    def error(self, message):
        raise ArgError(message)


def _number(text):
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}")
    # SPEC §3.1 (2): inf, -inf, nan sayı olarak kabul edilmez.
    if not math.isfinite(value):
        raise argparse.ArgumentTypeError(f"not a finite number: {text!r}")
    return value


def _precision(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an integer: {text!r}")
    if value < 0:
        raise argparse.ArgumentTypeError(f"must be non-negative: {text!r}")
    return value


def _build_parser():
    parser = _Parser(prog="gpower-clone", allow_abbrev=False)
    parser.add_argument("--test", required=True, choices=[TEST_NAME])
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument("--tails", required=True, type=_number)
    parser.add_argument("--dz", type=_number)
    parser.add_argument("--d", dest="d", type=_number)
    parser.add_argument("--alpha", required=True, type=_number)
    parser.add_argument("--power", type=_number)
    parser.add_argument("--n", type=_number)
    parser.add_argument("--n-total", dest="n_total", type=_number)
    parser.add_argument("--n_total", dest="n_total_underscore", type=_number)
    # Gizli: diferansiyel test için ondalık basamak sayısı; varsayılan çıktıyı değiştirmez.
    parser.add_argument("--precision", type=_precision, default=DECIMALS, help=argparse.SUPPRESS)
    return parser


def _pick(values, label):
    """Eş adlardan verilenleri toplar; birden çok ve farklı değer varsa hata verir."""
    given = {flag: value for flag, value in values.items() if value is not None}
    if not given:
        return None
    # SPEC §3.1 (4): eş adlar farklı değerle verilirse hata (dz/d ile aynı kural).
    if len(set(given.values())) > 1:
        conflict = ", ".join(f"{flag}={value}" for flag, value in given.items())
        raise ArgError(f"Conflicting values given for {label}: {conflict}")
    return next(iter(given.values()))


def _require(value, flag):
    if value is None:
        raise ArgError(f"the following arguments are required: {flag}")
    return value


def _run(args):
    # SPEC §3.1 (3): tails kontrolü bayrak okumasının parçası; §4'ten önce yapılır.
    engine.check_tails(args.tails)
    alpha = args.alpha
    # SPEC §3.1 (7): --dz (veya --d) her iki modda zorunlu.
    dz = _require(_pick({"--dz": args.dz, "--d": args.d}, "--dz/--d"), "--dz")
    if args.mode == "a-priori":
        # Moda ait olmayan bayrak (--n) yok sayılır (SPEC §3).
        power = _require(args.power, "--power")
        return engine.a_priori(args.tails, dz, alpha, power)
    # Moda ait olmayan bayrak (--power) yok sayılır (SPEC §3).
    n = _require(
        _pick(
            {"--n": args.n, "--n-total": args.n_total, "--n_total": args.n_total_underscore},
            "--n/--n-total/--n_total",
        ),
        "--n",
    )
    return engine.post_hoc(args.tails, dz, alpha, n)


def _round(value, decimals):
    # + 0.0, -0.0 değerinin JSON'da "-0.0" olarak çıkmasını önler.
    return round(value, decimals) + 0.0


def _format(result, decimals):
    return {
        "n_total": result.n_total,
        "actual_power": _round(result.actual_power, decimals),
        "critical": _round(result.critical, decimals),
        "df": result.df,
        "ncp": _round(result.ncp, decimals),
    }


def main(argv=None):
    try:
        args = _build_parser().parse_args(argv)
        result = _run(args)
    except (ArgError, engine.InputError) as exc:
        # SPEC §3.1 (1): hata JSON'u stdout'a yazılır; stderr boş kalır.
        print(json.dumps({"error": str(exc)}))
        return EXIT_ERROR
    print(json.dumps(_format(result, args.precision), separators=(",", ":")))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
