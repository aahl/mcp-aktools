# 📈 AkTools MCP Server

基于 akshare 的 MCP (Model Context Protocol) 服务器，提供股票、加密货币的数据查询和分析功能。
<!-- mcp-name: io.github.aahl/mcp-aktools -->


## 功能

- **股票搜索**: 根据公司名称、股票名称等关键词查找股票代码
- **股票信息**: 获取股票的详细信息，包括价格、市值等
- **历史价格**: 获取股票、加密货币历史价格数据，包含技术分析指标
- **相关新闻**: 获取股票、加密货币相关的最新新闻资讯
- **财务指标**: 支持A股和港股的财务报告关键指标查询


## 安装

### 方式1: uvx
```yaml
{
  "mcpServers": {
    "mcp-aktools": {
      "command": "uvx",
      "args": ["mcp-aktools"],
      "env": {
        "OKX_BASE_URL": "https://okx.4url.cn", # OKX地址，如果你的网络环境无法访问okx.com，可通过此选项配置反代地址
        "BINANCE_BASE_URL": "https://bian.4url.cn" # 币安地址，默认: https://www.binance.com
      }
    }
  }
}
```

### 方式2: Smithery
使用 [Smithery](https://smithery.ai/server/@aahl/mcp-aktools) 来安装，需要通过OAuth授权或Smithery key。
```yaml
{
  "mcpServers": {
    "mcp-aktools": {
      "url": "https://server.smithery.ai/@upstash/context7-mcp/mcp" # Streamable HTTP
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
    "mcp-aktools": {
      "url": "http://0.0.0.0:8808/mcp" # Streamable HTTP
    }
  }
}
```

### 快速开始
- 在线体验: [fastmcp.cloud](https://fastmcp.cloud/xiaomi/aktools/chat)
- 在线体验: [![smithery badge](https://smithery.ai/badge/@aahl/mcp-aktools)](https://smithery.ai/server/@aahl/mcp-aktools)
- 添加到 Cursor [![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/zh/install-mcp?name=aktools&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtY3AtYWt0b29scyJdfQ%3D%3D)
- 添加到 VS Code [<img alt="Install in VS Code" src="https://img.shields.io/badge/VS_Code-VS_Code?style=flat-square&label=Install+MCP+Server&color=0098FF">](https://insiders.vscode.dev/redirect?url=vscode:mcp/install%3F%7B%22name%22%3A%22aktools%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-aktools%22%5D%7D)
- 添加到 Claude code, 执行命令: `claude mcp add --transport stdio aktools -- uvx mcp-aktools`
- 添加到 OpenAI CodeX, 执行命令: `codex mcp add aktools -- uvx mcp-aktools`
- 添加到 [Cherry Studio](https://gitee.com/link?target=cherrystudio%3A%2F%2Fmcp%2Finstall%3Fservers%3DeyJtY3BTZXJ2ZXJzIjp7ImFrdG9vbHMiOnsiY29tbWFuZCI6InV2eCIsImFyZ3MiOlsibWNwLWFrdG9vbHMiXX19fQ%3D%3D)
