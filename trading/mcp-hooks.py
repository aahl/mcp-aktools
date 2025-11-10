import os
import json
import logging
import base64
from datetime import datetime
from fastmcp import FastMCP
from pydantic import Field

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)

mcp = FastMCP(name="mcp-hooks")

assets_schema = """资产明细，json格式，键为币种值为美元价值，结构如下:
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
    trades: list | str = Field("[]", description="本次新增的交易记录，如: [\"买入0.1BTC，花费1000USDT\"]"),
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
    data["balances"] = balances[-1000:]

    if isinstance(assets, str):
        try:
            assets = json.loads(assets)
        except ValueError:
            assets = {}
    if assets and isinstance(assets, dict):
        data["assets"] = {
            k: round(float(v), 1)
            for k, v in assets.items()
        }

    if isinstance(trades, str):
        try:
            trades = json.loads(trades)
        except ValueError:
            trades = None
    if trades and isinstance(trades, list):
        lst = data.setdefault("trades", [])
        for trade in trades:
            lst.insert(0, {
                "time": datetime.now().isoformat(),
                "text": str(trade),
            })
        data["trades"] = trades[0:100]

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    line = ",".join([str(x["balance"]) for x in data["balances"]])
    mermaid = f"""
xychart
    title "模拟盘余额"
    line [{line}]
""".strip()
    if os.path.exists("./README.tpl.md"):
        with open("./README.tpl.md", "r", encoding="utf-8") as file:
            content = file.read()
        content = content.replace("{mermaid}", mermaid)
        content = content.replace("{assets}", "\n".join([
            f"**{k}**: {v}"
            for k, v in data.get("assets", {}).items()
        ]))
        content = content.replace("{trades}", "\n".join([
            f"{trade['time']} - {trade['text']}"
            for trade in data.get("trades", [])[0:10]
        ]))
        with open("./README.md", "w", encoding="utf-8") as file:
            file.write(content)

    return {
        "path": os.path.abspath(path),
        "mermaid_image": "https://mermaid.ink/img/" + base64.urlsafe_b64encode(mermaid.encode()).decode(),
    }


mcp.run()