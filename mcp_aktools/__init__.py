import logging
import akshare as ak
import argparse
from fastmcp import FastMCP
from pydantic import Field
from datetime import datetime, timedelta
from .cache import CacheKey

_LOGGER = logging.getLogger(__name__)

mcp = FastMCP(name="mcp-aktools")

field_symbol = Field(description="股票代码")
field_market = Field("sh", description="股票市场，如: sh(上证), sz(深证), hk(港股), us(美股) 等")


@mcp.tool(
    title="查找股票代码",
    description="根据用户提供的股票名称、公司名称等关键词查找股票代码",
)
def search(
    keyword: str = Field(description="搜索关键词，公司名称、股票名称、股票代码、证券简称"),
    market: str = field_market,
):
    markets = [
        ["sh", ak.stock_info_a_code_name, ["code", "name"]],
        ["sh", ak.stock_info_sh_name_code, ["证券代码", "证券简称"]],
        ["sz", ak.stock_info_sz_name_code, ["A股代码", "A股简称"]],
        ["hk", ak.stock_hk_spot, ["代码", "中文名称"]],
        ["hk", ak.stock_hk_spot_em, ["代码", "名称"]],
        ["us", ak.stock_us_spot_em, ["代码", "名称"]],
    ]
    for m in markets:
        if m[0] != market:
            continue
        all = ak_cache(m[1], ttl=86400*7)
        if all is not None:
            suffix = f"证券市场: {market}"
            for _, v in all.iterrows():
                kws = [v[k] for k in m[2]]
                if keyword not in kws:
                    continue
                return "\n".join([v.to_string(), suffix])
            for _, v in all.iterrows():
                name = v[m[2][1]]
                if not name.startswith(keyword):
                    continue
                return "\n".join([v.to_string(), suffix])
    return f"Not Found for {keyword}"


@mcp.tool(
    title="获取股票信息",
    description="根据股票代码和市场获取股票基本信息",
)
def stock_info(
    symbol: str = field_symbol,
    market: str = field_market,
):
    markets = [
        ["sh", ak.stock_individual_info_em],
        ["sz", ak.stock_individual_info_em],
        ["hk", ak.stock_hk_security_profile_em],
    ]
    for m in markets:
        if m[0] != market:
            continue
        all = ak_cache(m[1], symbol=symbol, ttl=43200)
        if all is not None:
            return all.to_string()
    return f"Not Found for {symbol}.{market}"


@mcp.tool(
    title="获取股票历史价格",
    description="根据股票代码和市场获取股票历史价格及技术指标",
)
def stock_prices(
    symbol: str = field_symbol,
    market: str = field_market,
    period: str = Field("daily", description="周期，如: daily(日线), weekly(周线)"),
    price_count: int = Field(30),
):
    if period == "weekly":
        delta = {"weeks": price_count + 62}
    else:
        delta = {"days": price_count + 62}
    start_date = (datetime.now() - timedelta(**delta)).strftime("%Y%m%d")
    markets = [
        ["sh", ak.stock_zh_a_hist],
        ["sz", ak.stock_zh_a_hist],
        ["hk", ak.stock_hk_hist],
    ]
    for m in markets:
        if m[0] != market:
            continue
        dfs = ak_cache(m[1], symbol=symbol, period=period, start_date=start_date, ttl=3600)
        if dfs is None:
            continue
        add_technical_indicators(dfs, dfs["收盘"], dfs["最低"], dfs["最高"])
        columns = [
            "日期", "开盘", "收盘", "最高", "最低", "成交量", "换手率",
            "MACD", "DIF", "DEA", "KDJ.K", "KDJ.D", "KDJ.J", "RSI", "BOLL.U", "BOLL.M", "BOLL.L",
        ]
        all = dfs.to_csv(columns=columns, index=False, float_format="%.2f").strip().split("\n")
        return "\n".join([all[0], *all[-price_count:]])
    return f"Not Found for {symbol}.{market}"


@mcp.tool(
    title="获取股票相关新闻",
    description="根据股票代码和市场获取股票近期相关新闻",
)
def stock_news(
    symbol: str = field_symbol,
    market: str = field_market,
    news_count: int = Field(15),
):
    news = list(dict.fromkeys([
        v["新闻内容"]
        for v in ak_cache(ak.stock_news_em, symbol=symbol, ttl=3600).to_dict(orient="records")
        if isinstance(v, dict)
    ]))
    if news:
        return "\n".join(news[0:news_count])
    return f"Not Found for {symbol}.{market}"


@mcp.tool(
    title="A股关键指标",
    description="获取中国A股市场(上证、深证)的股票财务报告关键指标",
)
def stock_indicators_a(
    symbol: str = field_symbol,
):
    dfs = ak_cache(ak.stock_financial_abstract_ths, symbol=symbol)
    keys = dfs.to_csv(index=False).strip().split("\n")
    return "\n".join([keys[0], *keys[-15:]])


@mcp.tool(
    title="港股关键指标",
    description="获取港股市场的股票财务报告关键指标",
)
def stock_indicators_hk(
    symbol: str = field_symbol,
):
    dfs = ak_cache(ak.stock_financial_hk_analysis_indicator_em, symbol=symbol, indicator="报告期")
    keys = dfs.to_csv(index=False, float_format="%.3f").strip().split("\n")
    return "\n".join(keys[0:15])


def ak_cache(fun, *args, **kwargs):
    key = kwargs.pop("key", None)
    if not key:
        key = f"{fun.__name__}-{args}-{kwargs}"
    ttl1 = kwargs.pop("ttl", 86400)
    ttl2 = kwargs.pop("ttl2", None)
    cache = CacheKey.init(key, ttl1, ttl2)
    all = cache.get()
    if all is None:
        try:
            _LOGGER.info("Request akshare: %s", key)
            all = fun(*args, **kwargs)
            cache.set(all)
        except Exception as exc:
            _LOGGER.exception(str(exc))
    return all

def add_technical_indicators(df, clos, lows, high):
    # 计算MACD指标
    ema12 = clos.ewm(span=12, adjust=False).mean()
    ema26 = clos.ewm(span=26, adjust=False).mean()
    df["DIF"] = ema12 - ema26
    df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean()
    df["MACD"] = (df["DIF"] - df["DEA"]) * 2

    # 计算KDJ指标
    low_min  = lows.rolling(window=9, min_periods=1).min()
    high_max = high.rolling(window=9, min_periods=1).max()
    rsv = (clos - low_min) / (high_max - low_min) * 100
    df["KDJ.K"] = rsv.ewm(com=2, adjust=False).mean()
    df["KDJ.D"] = df["KDJ.K"].ewm(com=2, adjust=False).mean()
    df["KDJ.J"] = 3 * df["KDJ.K"] - 2 * df["KDJ.D"]

    # 计算RSI指标
    delta = clos.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # 计算布林带指标
    df["BOLL.M"] = clos.rolling(window=20).mean()
    std = clos.rolling(window=20).std()
    df["BOLL.U"] = df["BOLL.M"] + 2 * std
    df["BOLL.L"] = df["BOLL.M"] - 2 * std


def main():
    parser = argparse.ArgumentParser(description="AkTools MCP Server")
    parser.add_argument("--http", action="store_true", help="Use streamable HTTP mode instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=80, help="Port to listen on (default: 80)")

    args = parser.parse_args()
    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()
