# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import yfinance as yf
# import time
# from concurrent.futures import ThreadPoolExecutor
# from groq import Groq
# import os
# from dotenv import load_dotenv
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# load_dotenv()
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# @app.get("/")
# def home():
#     return {"message": "Backend is running"}

# @app.get("/stock/{ticker}")
# def get_stock(ticker: str):
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="3mo")

#         if hist.empty:
#             return {"error": "No data found for " + ticker}

#         hist["SMA20"] = hist["Close"].rolling(20).mean()
#         delta = hist["Close"].diff()
#         gain = delta.clip(lower=0).rolling(14).mean()
#         loss = -delta.clip(upper=0).rolling(14).mean()
#         hist["RSI"] = 100 - (100 / (1 + gain / loss))

#         current = hist.iloc[-1]
#         prev = hist.iloc[-2]

#         return {
#             "ticker": ticker.upper(),
#             "price": round(float(current["Close"]), 2),
#             "change_pct": round(
#                 (float(current["Close"]) - float(prev["Close"])) / float(prev["Close"]) * 100, 2
#             ),
#             "rsi": round(float(current["RSI"]), 1) if not hist["RSI"].isna().iloc[-1] else None,
#             "volume": int(current["Volume"]),
#             "sma20": round(float(current["SMA20"]), 2) if not hist["SMA20"].isna().iloc[-1] else None,
#             "history": [
#                 {"date": str(d.date()), "price": round(float(r["Close"]), 2)}
#                 for d, r in hist.tail(30).iterrows()
#             ],
#         }
#     except Exception as e:
#         return {"error": str(e)}

# class ChatRequest(BaseModel):
#     question: str
#     stock_context: dict

# @app.post("/chat")
# def chat(req: ChatRequest):
#     try:
#         prompt = f"""You are a helpful stock market analyst AI.
# Here is the current data for {req.stock_context.get('ticker')}:
# Price: ${req.stock_context.get('price')}
# Change: {req.stock_context.get('change_pct')}%
# RSI: {req.stock_context.get('rsi')}
# SMA20: {req.stock_context.get('sma20')}
# Volume: {req.stock_context.get('volume')}

# User question: {req.question}

# Give a short helpful answer in 3-4 sentences. Always remind the user this is not financial advice."""

#         response = groq_client.chat.completions.create(
#             model="openai/gpt-oss-20b",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=200,
#         )
#         return {"answer": response.choices[0].message.content}
#     except Exception as e:
#         return {"error": str(e)}
# _market_cache = {"t": 0, "data": None}
# MARKET_SECONDS = 120

# INDICES = [
#     ("^GSPC", "S&P 500"),
#     ("^IXIC", "Nasdaq"),
#     ("^NSEI", "Nifty 50"),
#     ("^BSESN", "Sensex"),
# ]
# US_STOCKS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]
# INDIA_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"]


# def _quote(symbol):
#     try:
#         closes = yf.Ticker(symbol).history(period="5d")["Close"].dropna()
#         if len(closes) < 2:
#             return {"symbol": symbol, "price": None, "change_pct": None}
#         price, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
#         return {
#             "symbol": symbol,
#             "price": round(price, 2),
#             "change_pct": round((price - prev) / prev * 100, 2),
#         }
#     except Exception:
#         return {"symbol": symbol, "price": None, "change_pct": None}


# @app.get("/market")
# def market():
#     if _market_cache["data"] and time.time() - _market_cache["t"] < MARKET_SECONDS:
#         return _market_cache["data"]
#     try:
#         symbols = [s for s, _ in INDICES] + US_STOCKS + INDIA_STOCKS
#         with ThreadPoolExecutor(max_workers=8) as pool:
#             quotes = {q["symbol"]: q for q in pool.map(_quote, symbols)}
#         data = {
#             "indices": [{**quotes[s], "name": n} for s, n in INDICES],
#             "us": [quotes[s] for s in US_STOCKS],
#             "india": [quotes[s] for s in INDIA_STOCKS],
#         }
#         _market_cache["t"] = time.time()
#         _market_cache["data"] = data
#         return data
#     except Exception as e:
#         return {"error": str(e)}
# import math
# import os
# import time
# from concurrent.futures import ThreadPoolExecutor

# import yfinance as yf
# from dotenv import load_dotenv
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from groq import Groq
# from pydantic import BaseModel

# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


# @app.get("/")
# def home():
#     return {"message": "Backend is running"}


# @app.get("/stock/{ticker}")
# def get_stock(ticker: str):
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="3mo")

#         if hist.empty:
#             return {"error": "No data found for " + ticker}

#         hist["SMA20"] = hist["Close"].rolling(20).mean()
#         delta = hist["Close"].diff()
#         gain = delta.clip(lower=0).rolling(14).mean()
#         loss = -delta.clip(upper=0).rolling(14).mean()
#         hist["RSI"] = 100 - (100 / (1 + gain / loss))

#         current = hist.iloc[-1]
#         prev = hist.iloc[-2]

#         return {
#             "ticker": ticker.upper(),
#             "price": round(float(current["Close"]), 2),
#             "change_pct": round(
#                 (float(current["Close"]) - float(prev["Close"])) / float(prev["Close"]) * 100, 2
#             ),
#             "rsi": round(float(current["RSI"]), 1) if not hist["RSI"].isna().iloc[-1] else None,
#             "volume": int(current["Volume"]),
#             "sma20": round(float(current["SMA20"]), 2) if not hist["SMA20"].isna().iloc[-1] else None,
#             "history": [
#                 {"date": str(d.date()), "price": round(float(r["Close"]), 2)}
#                 for d, r in hist.tail(30).iterrows()
#             ],
#         }
#     except Exception as e:
#         return {"error": str(e)}


# class ChatRequest(BaseModel):
#     question: str
#     stock_context: dict


# @app.post("/chat")
# def chat(req: ChatRequest):
#     try:
#         prompt = f"""You are a helpful stock market analyst AI.
# Here is the current data for {req.stock_context.get('ticker')}:
# Price: {req.stock_context.get('price')}
# Change: {req.stock_context.get('change_pct')}%
# RSI: {req.stock_context.get('rsi')}
# SMA20: {req.stock_context.get('sma20')}
# Volume: {req.stock_context.get('volume')}

# User question: {req.question}

# Give a short helpful answer in 3-4 sentences. Always remind the user this is not financial advice."""

#         response = groq_client.chat.completions.create(
#             model=GROQ_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=600,
#         )
#         return {"answer": response.choices[0].message.content}
#     except Exception as e:
#         return {"error": str(e)}


# # ---------------------------------------------------------------
# # Fundamentals (Screener-style)
# # ---------------------------------------------------------------
# _cache = {}
# CACHE_SECONDS = 600


# def clean(v):
#     try:
#         if v is None:
#             return None
#         f = float(v)
#         return None if math.isnan(f) or math.isinf(f) else f
#     except (TypeError, ValueError):
#         return None


# def build_table(df, rows, limit=5):
#     """Turn a yfinance statement DataFrame into {periods, rows}, oldest -> newest."""
#     if df is None or df.empty:
#         return {"periods": [], "rows": []}
#     cols = list(df.columns[:limit])
#     periods = [c.strftime("%b %Y") for c in cols][::-1]
#     out = []
#     for label, names, kind in rows:
#         for name in names:
#             if name in df.index:
#                 vals = [clean(df.loc[name, c]) for c in cols][::-1]
#                 if any(v is not None for v in vals):
#                     out.append({"label": label, "values": vals, "kind": kind})
#                 break
#     return {"periods": periods, "rows": out}


# def row_values(table, label):
#     for r in table["rows"]:
#         if r["label"] == label:
#             return r["values"]
#     return None


# def add_margin(table, num_label, den_label, new_label):
#     num = row_values(table, num_label)
#     den = row_values(table, den_label)
#     if not num or not den:
#         return
#     vals = [
#         round(n / d * 100, 2) if n is not None and d not in (None, 0) else None
#         for n, d in zip(num, den)
#     ]
#     if any(v is not None for v in vals):
#         table["rows"].append({"label": new_label, "values": vals, "kind": "pct"})


# def cagr(vals):
#     v = [x for x in (vals or []) if x is not None]
#     if len(v) < 2 or v[0] <= 0 or v[-1] <= 0:
#         return None
#     return ((v[-1] / v[0]) ** (1 / (len(v) - 1)) - 1) * 100


# def latest(df, names):
#     if df is None or df.empty:
#         return None
#     for n in names:
#         if n in df.index:
#             return clean(df.loc[n].iloc[0])
#     return None


# @app.get("/fundamentals/{ticker}")
# def fundamentals(ticker: str):
#     key = ticker.upper()
#     hit = _cache.get(key)
#     if hit and time.time() - hit[0] < CACHE_SECONDS:
#         return hit[1]

#     try:
#         t = yf.Ticker(key)
#         info = t.info or {}
#         if not (info.get("longName") or info.get("shortName")):
#             return {
#                 "error": f"No fundamentals found for {key}. "
#                 "For Indian stocks add .NS or .BO, e.g. RELIANCE.NS"
#             }

#         price = clean(
#             info.get("currentPrice")
#             or info.get("regularMarketPrice")
#             or info.get("previousClose")
#         )

#         income = build_table(
#             t.financials,
#             [
#                 ("Sales", ["Total Revenue", "Operating Revenue"], "money"),
#                 ("Expenses", ["Total Expenses"], "money"),
#                 ("Operating profit", ["Operating Income", "EBIT"], "money"),
#                 ("Profit before tax", ["Pretax Income"], "money"),
#                 ("Net profit", ["Net Income", "Net Income Common Stockholders"], "money"),
#                 ("EPS", ["Diluted EPS", "Basic EPS"], "per_share"),
#             ],
#         )
#         add_margin(income, "Operating profit", "Sales", "Operating margin %")
#         add_margin(income, "Net profit", "Sales", "Net margin %")

#         quarterly = build_table(
#             t.quarterly_financials,
#             [
#                 ("Sales", ["Total Revenue", "Operating Revenue"], "money"),
#                 ("Operating profit", ["Operating Income", "EBIT"], "money"),
#                 ("Net profit", ["Net Income", "Net Income Common Stockholders"], "money"),
#                 ("EPS", ["Diluted EPS", "Basic EPS"], "per_share"),
#             ],
#             limit=6,
#         )
#         add_margin(quarterly, "Operating profit", "Sales", "Operating margin %")

#         balance = build_table(
#             t.balance_sheet,
#             [
#                 ("Equity capital", ["Common Stock", "Ordinary Shares Number"], "money"),
#                 ("Total equity", ["Stockholders Equity", "Common Stock Equity"], "money"),
#                 ("Borrowings", ["Total Debt"], "money"),
#                 ("Total liabilities", ["Total Liabilities Net Minority Interest"], "money"),
#                 ("Cash", ["Cash And Cash Equivalents"], "money"),
#                 ("Total assets", ["Total Assets"], "money"),
#             ],
#         )

#         cashflow = build_table(
#             t.cashflow,
#             [
#                 ("Operating activity", ["Operating Cash Flow"], "money"),
#                 ("Investing activity", ["Investing Cash Flow"], "money"),
#                 ("Financing activity", ["Financing Cash Flow"], "money"),
#                 ("Free cash flow", ["Free Cash Flow"], "money"),
#             ],
#         )

#         ebit = latest(t.financials, ["EBIT", "Operating Income"])
#         total_assets = latest(t.balance_sheet, ["Total Assets"])
#         current_liab = latest(t.balance_sheet, ["Current Liabilities"])
#         roce = None
#         if ebit is not None and total_assets and current_liab is not None:
#             cap_employed = total_assets - current_liab
#             if cap_employed > 0:
#                 roce = round(ebit / cap_employed * 100, 2)

#         roe = clean(info.get("returnOnEquity"))
#         roe = round(roe * 100, 2) if roe is not None else None
#         de_raw = clean(info.get("debtToEquity"))
#         debt_to_equity = round(de_raw / 100, 2) if de_raw is not None else None
#         rate = clean(info.get("dividendRate"))
#         div_yield = round(rate / price * 100, 2) if rate and price else 0.0
#         pe = clean(info.get("trailingPE"))
#         pb = clean(info.get("priceToBook"))

#         insiders = clean(info.get("heldPercentInsiders"))
#         institutions = clean(info.get("heldPercentInstitutions"))
#         insiders = round(insiders * 100, 2) if insiders is not None else None
#         institutions = round(institutions * 100, 2) if institutions is not None else None
#         public = None
#         if insiders is not None and institutions is not None:
#             public = round(max(0.0, 100 - insiders - institutions), 2)

#         sales_cagr = cagr(row_values(income, "Sales"))
#         profit_cagr = cagr(row_values(income, "Net profit"))

#         pros, cons = [], []
#         if debt_to_equity is not None:
#             if debt_to_equity < 0.1:
#                 pros.append("Company is almost debt free.")
#             elif debt_to_equity > 1.5:
#                 cons.append(f"Debt is high at {debt_to_equity}x equity.")
#         if pb is not None:
#             if pb < 1:
#                 pros.append(f"Stock is trading at {pb:.2f} times its book value.")
#             elif pb > 8:
#                 cons.append(f"Stock is trading at {pb:.1f} times its book value.")
#         if roe is not None:
#             if roe >= 15:
#                 pros.append(f"Good return on equity of {roe}%.")
#             elif roe < 8:
#                 cons.append(f"Low return on equity of {roe}%.")
#         if div_yield and div_yield >= 2:
#             pros.append(f"Pays a healthy dividend, yielding {div_yield}%.")
#         elif not div_yield:
#             cons.append("Company is not paying out dividend.")
#         if sales_cagr is not None:
#             if sales_cagr >= 10:
#                 pros.append(f"Sales grew {sales_cagr:.1f}% a year over the period shown.")
#             elif sales_cagr < 0:
#                 cons.append(f"Sales shrank {abs(sales_cagr):.1f}% a year over the period shown.")
#         if profit_cagr is not None:
#             if profit_cagr >= 15:
#                 pros.append(f"Profit grew {profit_cagr:.1f}% a year over the period shown.")
#             elif profit_cagr < 0:
#                 cons.append(f"Profit fell {abs(profit_cagr):.1f}% a year over the period shown.")
#         if pe is not None and pe > 50:
#             cons.append(f"Stock looks expensive with a P/E of {pe:.1f}.")
#         if insiders is not None:
#             if insiders >= 50:
#                 pros.append(f"Insider / promoter holding is high at {insiders}%.")
#             elif insiders < 10:
#                 cons.append(f"Insider / promoter holding is low at {insiders}%.")

#         result = {
#             "ticker": key,
#             "name": info.get("longName") or info.get("shortName"),
#             "currency": info.get("currency"),
#             "exchange": info.get("fullExchangeName") or info.get("exchange"),
#             "sector": info.get("sector"),
#             "industry": info.get("industry"),
#             "website": info.get("website"),
#             "about": info.get("longBusinessSummary"),
#             "ratios": {
#                 "market_cap": clean(info.get("marketCap")),
#                 "price": price,
#                 "high": clean(info.get("fiftyTwoWeekHigh")),
#                 "low": clean(info.get("fiftyTwoWeekLow")),
#                 "pe": pe,
#                 "book_value": clean(info.get("bookValue")),
#                 "price_to_book": pb,
#                 "dividend_yield": div_yield,
#                 "roce": roce,
#                 "roe": roe,
#                 "debt_to_equity": debt_to_equity,
#                 "eps": clean(info.get("trailingEps")),
#                 "beta": clean(info.get("beta")),
#             },
#             "growth": {
#                 "sales_cagr": round(sales_cagr, 1) if sales_cagr is not None else None,
#                 "profit_cagr": round(profit_cagr, 1) if profit_cagr is not None else None,
#             },
#             "pros": pros,
#             "cons": cons,
#             "shareholding": {
#                 "insiders": insiders,
#                 "institutions": institutions,
#                 "public": public,
#             },
#             "income": income,
#             "quarterly": quarterly,
#             "balance": balance,
#             "cashflow": cashflow,
#         }
#         _cache[key] = (time.time(), result)
#         return result
#     except Exception as e:
#         return {"error": str(e)}


# # ---------------------------------------------------------------
# # Markets page
# # ---------------------------------------------------------------
# _market_cache = {"t": 0, "data": None}
# MARKET_SECONDS = 120

# INDICES = [
#     ("^GSPC", "S&P 500"),
#     ("^IXIC", "Nasdaq"),
#     ("^NSEI", "Nifty 50"),
#     ("^BSESN", "Sensex"),
# ]
# US_STOCKS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]
# INDIA_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"]


# def _quote(symbol):
#     try:
#         closes = yf.Ticker(symbol).history(period="5d")["Close"].dropna()
#         if len(closes) < 2:
#             return {"symbol": symbol, "price": None, "change_pct": None}
#         price, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
#         return {
#             "symbol": symbol,
#             "price": round(price, 2),
#             "change_pct": round((price - prev) / prev * 100, 2),
#         }
#     except Exception:
#         return {"symbol": symbol, "price": None, "change_pct": None}


# @app.get("/market")
# def market():
#     if _market_cache["data"] and time.time() - _market_cache["t"] < MARKET_SECONDS:
#         return _market_cache["data"]
#     try:
#         symbols = [s for s, _ in INDICES] + US_STOCKS + INDIA_STOCKS
#         with ThreadPoolExecutor(max_workers=8) as pool:
#             quotes = {q["symbol"]: q for q in pool.map(_quote, symbols)}
#         data = {
#             "indices": [{**quotes[s], "name": n} for s, n in INDICES],
#             "us": [quotes[s] for s in US_STOCKS],
#             "india": [quotes[s] for s in INDIA_STOCKS],
#         }
#         _market_cache["t"] = time.time()
#         _market_cache["data"] = data
#         return data
#     except Exception as e:
#         return {"error": str(e)}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes import stock, chat, fundamentals, market

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Stock AI",
    description="AI-Powered Stock Analysis and Financial Advisor",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# Home route
@app.get("/")
def home():
    return {
        "message": "Backend is running"
    }


# Register API routers
app.include_router(stock.router)
app.include_router(chat.router)
app.include_router(fundamentals.router)
app.include_router(market.router)
