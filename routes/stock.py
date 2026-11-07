
import yfinance as yf

from fastapi import APIRouter
from services.indicators import calculate_indicators

router = APIRouter()


@router.get("/stock/{ticker}")
def get_stock(ticker: str):

    try:
        stock = yf.Ticker(ticker)

        hist = stock.history(period="3mo")

        if hist.empty:
            return {"error": "No data found for " + ticker}

        # Calculate indicators
        hist = calculate_indicators(hist)

        current = hist.iloc[-1]
        prev = hist.iloc[-2]

        return {
            "ticker": ticker.upper(),

            "price": round(float(current["Close"]), 2),

            "change_pct": round(
                (float(current["Close"]) -
                 float(prev["Close"])) /
                float(prev["Close"]) * 100, 2
            ),

            "rsi": (
                round(float(current["RSI"]), 1)
                if not hist["RSI"].isna().iloc[-1]
                else None
            ),

            "volume": int(current["Volume"]),

            "sma20": (
                round(float(current["SMA20"]), 2)
                if not hist["SMA20"].isna().iloc[-1]
                else None
            ),

            "history": [
                {
                    "date": str(d.date()),
                    "price": round(float(r["Close"]), 2)
                }
                for d, r in hist.tail(30).iterrows()
            ]
        }

    except Exception as e:
        return {"error": str(e)}
