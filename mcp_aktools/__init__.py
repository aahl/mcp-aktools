import os
import time
import logging
import akshare as ak
import argparse
import requests
import pandas as pd
from fastmcp import FastMCP
from pydantic import Field
from datetime import datetime, timedelta
from starlette.middleware.cors import CORSMiddleware
from .cache import CacheKey

_LOGGER = logging.getLogger(__name__)

mcp = FastMCP(name="mcp-aktools")

field_symbol = Field(description="股票代码")
field_market = Field("sh", description="股票市场，如: sh(上证), sz(深证), hk(港股), us(美股) 等")

OKX_BASE_URL = os.getenv("OKX_BASE_URL") or "https://www.okx.com"
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL") or "https://www.binance.com"


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
    title="获取股票/加密货币相关新闻",
    description="根据股票代码或关键词获取近期相关新闻",
)
def stock_news(
    keyword: str = Field(description="关键词"),
    news_count: int = Field(15),
):
    news = list(dict.fromkeys([
        v["新闻内容"]
        for v in ak_cache(ak.stock_news_em, symbol=keyword, ttl=3600).to_dict(orient="records")
        if isinstance(v, dict)
    ]))
    if news:
        return "\n".join(news[0:news_count])
    return f"Not Found for {keyword}"


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


@mcp.tool(
    title="获取加密货币历史价格",
    description="获取OKX加密货币K线数据",
)
def okx_prices(
    instId: str = Field("BTC-USDT", description="产品ID，格式: BTC-USDT"),
    bar: str = Field("1h", description="K线时间粒度，仅支持: [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/2D/3D/1W/1M/3M] 注意大小写，仅分钟为小写m"),
    limit: int = Field(100, description="返回数量，最大300，最小建议30"),
):
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/market/candles",
        params={
            "instId": instId,
            "bar": bar,
            "limit": max(300, limit + 62),
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "开盘", "最高", "最低", "收盘", "成交量", "成交额", "成交额USDT", "K线已完结"]
    dfs.sort_values("时间", inplace=True)
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["开盘"] = pd.to_numeric(dfs["开盘"], errors="coerce")
    dfs["最高"] = pd.to_numeric(dfs["最高"], errors="coerce")
    dfs["最低"] = pd.to_numeric(dfs["最低"], errors="coerce")
    dfs["收盘"] = pd.to_numeric(dfs["收盘"], errors="coerce")
    dfs["成交量"] = pd.to_numeric(dfs["成交量"], errors="coerce")
    dfs["成交额"] = pd.to_numeric(dfs["成交额"], errors="coerce")
    add_technical_indicators(dfs, dfs["收盘"], dfs["最低"], dfs["最高"])
    columns = [
        "时间", "开盘", "收盘", "最高", "最低", "成交量", "成交额",
        "MACD", "DIF", "DEA", "KDJ.K", "KDJ.D", "KDJ.J", "RSI", "BOLL.U", "BOLL.M", "BOLL.L",
    ]
    all = dfs.to_csv(columns=columns, index=False, float_format="%.2f").strip().split("\n")
    return "\n".join([all[0], *all[-limit:]])


@mcp.tool(
    title="获取加密货币杠杆多空比",
    description="获取OKX加密货币借入计价货币与借入交易货币的累计数额比值",
)
def okx_loan_ratios(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    period: str = Field("1h", description="时间粒度，仅支持: [5m/1H/1D] 注意大小写，仅分钟为小写m"),
):
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/rubik/stat/margin/loan-ratio",
        params={
            "ccy": symbol,
            "period": period,
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "多空比"]
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["多空比"] = pd.to_numeric(dfs["多空比"], errors="coerce")
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="获取加密货币主动买卖情况",
    description="获取OKX加密货币主动买入和卖出的交易量",
)
def okx_taker_volume(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    period: str = Field("1h", description="时间粒度，仅支持: [5m/1H/1D] 注意大小写，仅分钟为小写m"),
    instType: str = Field("SPOT", description="产品类型 SPOT:现货 CONTRACTS:衍生品"),
):
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/rubik/stat/taker-volume",
        params={
            "ccy": symbol,
            "period": period,
            "instType": instType,
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "卖出量", "买入量"]
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["卖出量"] = pd.to_numeric(dfs["卖出量"], errors="coerce")
    dfs["买入量"] = pd.to_numeric(dfs["买入量"], errors="coerce")
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="获取加密货币分析报告",
    description="获取币安对加密货币的AI分析报告",
)
def binance_ai_report(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
):
    res = requests.post(
        f"{BINANCE_BASE_URL}/bapi/bigdata/v3/friendly/bigdata/search/ai-report/report",
        json={
            'lang': 'zh-CN',
            'token': symbol,
            'symbol': f'{symbol}USDT',
            'product': 'web-spot',
            'timestamp': int(time.time() * 1000),
            'translateToken': None,
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10) AppleWebKit/537.36 Chrome/139',
            'Referer': f'https://www.binance.com/zh-CN/trade/{symbol}_USDT?type=spot',
            'lang': 'zh-CN',
        },
        timeout=20,
    )
    resp = res.json() or {}
    data = resp.get('data') or {}
    modules = data.get('report', {}).get('translated', {}).get('modules', [])
    txts = []
    for module in modules:
        if tit := module.get('overview'):
            txts.append(tit)
        for point in module.get('points', []):
            txts.append(point.get('content', ''))
    return '\n'.join(txts)



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
    port = int(os.getenv("PORT", 0)) or 80
    parser = argparse.ArgumentParser(description="AkTools MCP Server")
    parser.add_argument("--http", action="store_true", help="Use streamable HTTP mode instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=port, help=f"Port to listen on (default: {port})")

    args = parser.parse_args()
    if args.http:
        app = mcp.streamable_http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()
