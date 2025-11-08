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

@mcp.tool(
    description="保存交易结果",
)
def save_trading_result(
    balance: str = Field(description="账户余额，单位: USD"),
    workdir: str = Field(".", description="工作目录，默认当前目录"),
):
    path = os.path.join(workdir or ".", "demo.json")
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
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    readme = os.path.join(workdir or ".", "README.md")
    if os.path.exists(readme):
        with open(readme, "r", encoding="utf-8") as file:
            content = file.read()
        line = ",".join(balances)
        re.sub(r"(\s+line\s+)\[[^]]*]", rf"\1[{line}]", content)
        with open(readme, "w", encoding="utf-8") as file:
            file.write(content)

    return f"Saved to {path}"


mcp.run()