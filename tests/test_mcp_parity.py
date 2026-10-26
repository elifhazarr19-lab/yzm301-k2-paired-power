"""CLI = MCP eşitlik testi.

Aynı girdi iki yoldan çalıştırılır ve iki JSON'un birebir aynı olduğu doğrulanır:
- CLI: `python -m pairedpower.cli` alt süreç olarak (stdout'taki tek satır JSON).
- MCP: `python -m pairedpower.mcp_server` stdio sunucusu, resmi `mcp` istemcisiyle
  gerçek MCP protokolü üzerinden `t_paired_power` aracı çağrılır.

Girdiler: oracle/gpower_vectors.csv'deki 38 satır (30 hesaplı + 8 hata) ve
oracle/library_vectors.csv'den eşit aralıklı 60 satır (30 a-priori + 30 post-hoc).
"""

import csv
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anyio
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
GPOWER = ROOT / "oracle" / "gpower_vectors.csv"
LIBRARY = ROOT / "oracle" / "library_vectors.csv"
TOOL = "t_paired_power"
LIBRARY_PER_MODE = 30
GPOWER_STATUSES = ("GUI-TOPLANDI", "GUI-TOPLANDI-HATA")
CLI_WORKERS = 8


def _env():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _read(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _spread(rows, k):
    step = len(rows) / k
    return [rows[int(i * step)] for i in range(k)]


def load_cases():
    cases = [r for r in _read(GPOWER) if r["status"] in GPOWER_STATUSES]
    library = _read(LIBRARY)
    for mode in ("a-priori", "post-hoc"):
        cases += _spread([r for r in library if r["mode"] == mode], LIBRARY_PER_MODE)
    return cases


def cli_args(row):
    args = ["--test", "t-paired", "--mode", row["mode"], "--tails", row["tails"],
            "--dz", row["dz"], "--alpha", row["alpha"]]
    if row["mode"] == "a-priori":
        args += ["--power", row["power"]]
    else:
        args += ["--n", row["n_input"]]
    return args


def mcp_args(row):
    args = {"mode": row["mode"], "tails": float(row["tails"]),
            "dz": float(row["dz"]), "alpha": float(row["alpha"])}
    if row["mode"] == "a-priori":
        args["power"] = float(row["power"])
    else:
        args["n"] = float(row["n_input"])
    return args


def run_cli(row):
    proc = subprocess.run(
        [sys.executable, "-m", "pairedpower.cli", *cli_args(row)],
        capture_output=True, text=True, encoding="utf-8", env=_env(), cwd=ROOT,
    )
    return proc.returncode, json.loads(proc.stdout)


async def _run_mcp_all(rows):
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "pairedpower.mcp_server"], env=_env(), cwd=str(ROOT),
    )
    results = {}
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert TOOL in [t.name for t in tools.tools]
            for row in rows:
                res = await session.call_tool(TOOL, mcp_args(row))
                assert not res.isError, res.content
                assert len(res.content) == 1
                results[row["id"]] = json.loads(res.content[0].text)
    return results


CASES = load_cases()


@pytest.fixture(scope="module")
def outputs():
    with ThreadPoolExecutor(max_workers=CLI_WORKERS) as pool:
        cli = dict(zip([r["id"] for r in CASES], pool.map(run_cli, CASES)))
    mcp = anyio.run(_run_mcp_all, CASES)
    return cli, mcp


def test_case_counts():
    gpower = [c for c in CASES if c["id"].startswith("V")]
    library = [c for c in CASES if c["id"].startswith("L-")]
    assert len(gpower) == 38
    assert len(library) == 2 * LIBRARY_PER_MODE


@pytest.mark.parametrize("row", [pytest.param(r, id=r["id"]) for r in CASES])
def test_cli_equals_mcp(outputs, row):
    cli, mcp = outputs
    code, cli_out = cli[row["id"]]
    mcp_out = mcp[row["id"]]

    # Birebir aynı: aynı anahtarlar, aynı değerler, aynı tipler (int / float).
    assert mcp_out == cli_out
    assert {k: type(v) for k, v in mcp_out.items()} == {k: type(v) for k, v in cli_out.items()}

    if row.get("status") == "GUI-TOPLANDI-HATA":
        assert code == 2 and set(cli_out) == {"error"}
    else:
        assert code == 0
        assert list(cli_out) == ["n_total", "actual_power", "critical", "df", "ncp"]
