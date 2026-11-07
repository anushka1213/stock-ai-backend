
import time

import yfinance as yf

from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter

router = APIRouter()

_market_cache = {
    "t": 0,
    "data": None
}

MARKET_SECONDS = 120

INDICES = [
    ("^GSPC", "S&P 500"),
    ("^IXIC", "Nasdaq"),
    ("^NSEI", "Nifty 50"),
    ("^BSESN", "Sensex"),
]

US_STOCKS = [
    "AAPL", "MSFT", "NVDA", "TSLA",
    "AMZN", "GOOGL", "META"
]

INDIA_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS",
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"
]


def _quote(symbol):

    try:

        closes = (
            yf.Ticker(symbol)
            .history(period="5d")["Close"]
            .dropna()
        )

        if len(closes) < 2:

            return {
                "symbol": symbol,
                "price": None,
                "change_pct": None
            }

        price = float(closes.iloc[-1])
        prev = float(closes.iloc[-2])

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change_pct": round(
                (price - prev) / prev * 100, 2
            )
        }

    except Exception:

        return {
            "symbol": symbol,
            "price": None,
            "change_pct": None
        }


@router.get("/market")
def market():

    if (
        _market_cache["data"]
        and time.time() - _market_cache["t"] < MARKET_SECONDS
    ):
        return _market_cache["data"]

    try:

        symbols = (
            [s for s, _ in INDICES]
            + US_STOCKS
            + INDIA_STOCKS
        )

        with ThreadPoolExecutor(max_workers=8) as pool:

            quotes = {
                q["symbol"]: q
                for q in pool.map(_quote, symbols)
            }

        data = {

            "indices": [
                {
                    **quotes[s],
                    "name": n
                }
                for s, n in INDICES
            ],

            "us": [
                quotes[s]
                for s in US_STOCKS
            ],

            "india": [
                quotes[s]
                for s in INDIA_STOCKS
            ]
        }

        _market_cache["t"] = time.time()
        _market_cache["data"] = data

        return data

    except Exception as e:
        return {"error": str(e)}
