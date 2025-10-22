# 📈 AkTools MCP Server

基于 akshare 的 MCP (Model Context Protocol) 服务器，提供股票、加密货币的数据查询和分析功能。


## 功能

- **股票搜索**: 根据公司名称、股票名称等关键词查找股票代码
- **股票信息**: 获取股票的详细信息，包括价格、市值等
- **历史价格**: 获取股票、加密货币历史价格数据，包含技术分析指标
- **相关新闻**: 获取股票、加密货币相关的最新新闻资讯
- **财务指标**: 支持A股和港股的财务报告关键指标查询


## 安装

### 方式1: uvx
```json
{
  "mcpServers": {
    "mcp-aktools": {
      "command": "uvx",
      "args": ["mcp-aktools"]
    }
  }
}
```

### 方式2: Docker
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
