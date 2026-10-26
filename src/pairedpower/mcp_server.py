"""MCP sunucusu (stdio): motoru çağıran ince adaptör.

Hesap, doğrulama ve yuvarlama `engine.calculate` içindedir; bu dosyada formül yoktur.
Çıktı alanları CLI ile birebir aynıdır (SPEC §6).
"""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from pairedpower import engine

SERVER_NAME = "pairedpower"
TOOL_NAME = "t_paired_power"

mcp = FastMCP(SERVER_NAME, log_level="WARNING")


@mcp.tool(name=TOOL_NAME)
def t_paired_power(
    mode: Annotated[str, Field(description='"a-priori" (N hesapla) ya da "post-hoc" (gücü hesapla)')],
    tails: Annotated[float, Field(description="1 (tek kuyruk) ya da 2 (iki kuyruk)")],
    dz: Annotated[float, Field(description="Etki büyüklüğü dz = farkların ortalaması / farkların SD'si; -20..20")],
    alpha: Annotated[float, Field(description="I. tip hata; 1e-07..0.9999999")],
    power: Annotated[Optional[float], Field(description="Hedef güç; yalnızca a-priori'de zorunlu")] = None,
    n: Annotated[Optional[float], Field(description="Çift (denek) sayısı; yalnızca post-hoc'ta zorunlu")] = None,
) -> dict:
    """Eşleştirilmiş örneklem t testi (t-paired, önce/sonra ölçüm) için güç analizi.

    mode: "a-priori" (hedef güç için gereken çift sayısı N) ya da "post-hoc" (verilen N için güç).
    tails: 1 (tek kuyruk) ya da 2 (iki kuyruk).
    dz: etki büyüklüğü = farkların ortalaması / farkların standart sapması.
    alpha: I. tip hata (ör. 0.05).
    power: hedef güç; yalnızca a-priori'de zorunlu.
    n: çift (denek) sayısı; yalnızca post-hoc'ta zorunlu.

    Başarıda {n_total, actual_power, critical, df, ncp}; hatada {error} döner.
    """
    # Tipler bilerek geniş tutuldu (mode: str, tails: float): geçersiz değerler şema katmanında
    # değil, CLI ile aynı motor doğrulamasında yakalanır ve aynı {"error": ...} döner.
    return engine.calculate(mode, tails, dz, alpha, power=power, n=n)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
