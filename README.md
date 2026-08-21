# 📈 AkTools MCP Server

<!-- mcp-name: io.github.aahl/mcp-aktools -->
<!-- [![MCP Badge](https://lobehub.com/badge/mcp/aahl-mcp-aktools)](https://lobehub.com/mcp/aahl-mcp-aktools) -->
<!-- [![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/1dd74d48-e77b-49f9-8d67-8c99603336e1) -->

基于 akshare 的 MCP (Model Context Protocol) 服务器，提供股票、加密货币的数据查询和分析功能。


## 功能

- 🔍 **股票搜索**: 根据股票名称、公司简称等关键词查找股票代码
- ℹ️ **股票信息**: 获取股票的详细信息，包括价格、市值等
- 📊 **市场概况**: 获取A股市场的涨停板、龙虎榜、资金流向等
- 💹 **历史价格**: 获取股票、加密货币历史价格数据，包含技术分析指标
- 📰 **相关新闻**: 获取股票、加密货币相关的最新新闻资讯
- 💸 **财务指标**: 支持A股和港美股的财务报告关键指标查询


## 安装

### 方式1: uvx
```yaml
{
  "mcpServers": {
    "aktools": {
      "command": "uvx",
      "args": ["mcp-aktools"],
      "env": {
        # 全部可选
        "OKX_BASE_URL": "https://okx.4url.cn", # OKX地址，如果你的网络环境无法访问okx.com，可通过此选项配置反代地址
        "BINANCE_BASE_URL": "https://bian.4url.cn", # 币安地址，默认: https://www.binance.com
        "NEWSNOW_BASE_URL": "https://newsnow.busiyi.world", # Newsnow接口地址
        "NEWSNOW_CHANNELS": "wallstreetcn-quick,cls-telegraph,jin10", # Newsnow资讯来源
      }
    }
  }
}
```

### 方式2: [Smithery](https://smithery.ai/server/@aahl/mcp-aktools)
> 需要通过OAuth授权或Smithery key

```yaml
{
  "mcpServers": {
    "aktools": {
      "url": "https://server.smithery.ai/@aahl/mcp-aktools/mcp" # Streamable HTTP
    }
  }
}
```

### 方式3: Docker
```bash
mkdir /opt/mcp-aktools
cd /opt/mcp-aktools
wget https://raw.githubusercontent.com/aahl/mcp-aktools/refs/heads/main/docker-compose.yml
docker-compose up -d
```
```yaml
{
  "mcpServers": {
    "aktools": {
      "url": "http://0.0.0.0:8808/mcp" # Streamable HTTP
    }
  }
}
```

### 快速开始
- 在线体验: [![fastmcp.cloud](https://img.shields.io/badge/Cloud-+?label=FastMCP)](https://fastmcp.cloud/xiaomi/aktools/chat)
- 在线体验: [![Listed on Skillselion](https://skillselion.com/badge/mcp/tool/io.github.aahl/mcp-aktools.svg)](https://skillselion.com/mcp/tool/io.github.aahl/mcp-aktools)
- 添加到 Cursor [![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/zh/install-mcp?name=aktools&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtY3AtYWt0b29scyJdfQ%3D%3D)
- 添加到 VS Code [![Install MCP Server](https://img.shields.io/badge/VS_Code-+?label=Add+MCP+Server&color=0098FF)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install%3F%7B%22name%22%3A%22aktools%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-aktools%22%5D%7D)
- 添加到 Cherry Studio [![Install MCP Server](https://img.shields.io/badge/Cherry_Studio-+?label=Add+MCP+Server&color=FF5F5F)](https://gitee.com/link?target=cherrystudio%3A%2F%2Fmcp%2Finstall%3Fservers%3DeyJtY3BTZXJ2ZXJzIjp7ImFrdG9vbHMiOnsiY29tbWFuZCI6InV2eCIsImFyZ3MiOlsibWNwLWFrdG9vbHMiXX19fQ%3D%3D)
- 添加到 Claude Code, 执行命令: `claude mcp add aktools -- uvx mcp-aktools`
- 添加到 OpenAI CodeX, 执行命令: `codex mcp add aktools -- uvx mcp-aktools`

------

## 🛠️ 可用工具

<details>
<summary><strong>个股相关</strong></summary>

- `search` - 查找股票代码，支持A股、港股、美股
- `stock_info` - 获取股票信息
- `stock_prices` - 获取股票历史价格
- `stock_indicators_a` - A股关键指标
- `stock_indicators_hk` - 港股关键指标
- `stock_indicators_us` - 美股关键指标
- `trading_suggest` - 给出投资建议

</details>

<details>
<summary><strong>A股市场</strong></summary>

- `get_current_time` - 获取当前时间及A股交易日信息
- `stock_zt_pool_em` - A股涨停股池
- `stock_zt_pool_strong_em` - A股强势股池
- `stock_lhb_ggtj_sina` - A股龙虎榜统计
- `stock_sector_fund_flow_rank` - A股概念资金流向

</details>

<details>
<summary><strong>财经资讯</strong></summary>

- `stock_news` - 获取个股/加密货币相关新闻
- `stock_news_global` - 全球财经快讯

</details>

<details>
<summary><strong>加密货币</strong></summary>

- `okx_prices` - 获取加密货币历史价格
- `okx_loan_ratios` - 获取加密货币杠杆多空比
- `okx_taker_volume` - 获取加密货币主动买卖情况
- `binance_ai_report` - 获取加密货币AI分析报告

</details>


------

<a href="https://glama.ai/mcp/servers/@al-one/mcp-aktools">
  <img width="400" src="https://glama.ai/mcp/servers/@al-one/mcp-aktools/badge">
</a>

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/aahl-mcp-aktools-badge.png)](https://mseep.ai/app/aahl-mcp-aktools)
