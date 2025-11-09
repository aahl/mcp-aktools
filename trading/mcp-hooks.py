import os
import json
import logging
import re
from datetime import datetime
from fastmcp import FastMCP
from pydantic import Field

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)

mcp = FastMCP(name="mcp-hooks")

assets_schema = """资产明细，json格式，健为币种，值为美元价值，结构如下:
{
  "BTC": <float>,
  "ETH": <float>,
  ...
}
"""

@mcp.tool(
    description="保存交易结果",
)
def save_trading_result(
    balance: float = Field(description="账户总余额美元价值，单位: USD"),
    assets: dict | str = Field("{}", description=assets_schema),
):
    if not balance:
        return "Balance is empty"

    path = "./demo.json"
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    balances = data.setdefault("balances", [])
    balances.append({
        "time": datetime.now().isoformat(),
        "balance": round(float(balance), 1),
    })
    if isinstance(assets, str):
        try:
            assets = json.loads(assets)
            if assets:
                data["assets"] = assets
        except ValueError:
            pass

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    line = ",".join([str(x["balance"]) for x in balances])
    readme = "./README.md"
    if os.path.exists(readme):
        with open(readme, "r", encoding="utf-8") as file:
            content = file.read()
        content = re.sub(r"(\s+line\s+)\[[^]]*]", rf"\1[{line}]", content)
        with open(readme, "w", encoding="utf-8") as file:
            file.write(content)

    return f"Saved to {os.path.abspath(path)}"


mcp.run()