
import math
import time

import yfinance as yf
from fastapi import APIRouter

router = APIRouter()

_cache = {}
CACHE_SECONDS = 600


def clean(v):
    try:
        if v is None:
            return None

        f = float(v)

        return None if math.isnan(f) or math.isinf(f) else f

    except (TypeError, ValueError):
        return None


def build_table(df, rows, limit=5):

    if df is None or df.empty:
        return {"periods": [], "rows": []}

    cols = list(df.columns[:limit])

    periods = [
        c.strftime("%b %Y")
        for c in cols
    ][::-1]

    out = []

    for label, names, kind in rows:

        for name in names:

            if name in df.index:

                vals = [
                    clean(df.loc[name, c])
                    for c in cols
                ][::-1]

                if any(v is not None for v in vals):

                    out.append({
                        "label": label,
                        "values": vals,
                        "kind": kind
                    })

                break

    return {
        "periods": periods,
        "rows": out
    }


def row_values(table, label):

    for r in table["rows"]:

        if r["label"] == label:
            return r["values"]

    return None


def add_margin(table, num_label, den_label, new_label):

    num = row_values(table, num_label)
    den = row_values(table, den_label)

    if not num or not den:
        return

    vals = [
        round(n / d * 100, 2)
        if n is not None and d not in (None, 0)
        else None
        for n, d in zip(num, den)
    ]

    if any(v is not None for v in vals):

        table["rows"].append({
            "label": new_label,
            "values": vals,
            "kind": "pct"
        })


def cagr(vals):

    v = [
        x for x in (vals or [])
        if x is not None
    ]

    if len(v) < 2 or v[0] <= 0 or v[-1] <= 0:
        return None

    return (
        (v[-1] / v[0]) ** (1 / (len(v) - 1)) - 1
    ) * 100


def latest(df, names):

    if df is None or df.empty:
        return None

    for n in names:

        if n in df.index:
            return clean(df.loc[n].iloc[0])

    return None


@router.get("/fundamentals/{ticker}")
def fundamentals(ticker: str):

    key = ticker.upper()

    hit = _cache.get(key)

    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]

    try:

        t = yf.Ticker(key)

        info = t.info or {}

        if not (info.get("longName") or info.get("shortName")):

            return {
                "error": f"No fundamentals found for {key}. "
                "For Indian stocks add .NS or .BO, "
                "e.g. RELIANCE.NS"
            }

        price = clean(
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        # Annual income statement

        income = build_table(
            t.financials,
            [
                ("Sales", ["Total Revenue", "Operating Revenue"], "money"),
                ("Expenses", ["Total Expenses"], "money"),
                ("Operating profit", ["Operating Income", "EBIT"], "money"),
                ("Profit before tax", ["Pretax Income"], "money"),
                ("Net profit", ["Net Income", "Net Income Common Stockholders"], "money"),
                ("EPS", ["Diluted EPS", "Basic EPS"], "per_share"),
            ]
        )

        add_margin(
            income, "Operating profit", "Sales",
            "Operating margin %"
        )

        add_margin(
            income, "Net profit", "Sales",
            "Net margin %"
        )

        # Quarterly financial statement

        quarterly = build_table(
            t.quarterly_financials,
            [
                ("Sales", ["Total Revenue", "Operating Revenue"], "money"),
                ("Operating profit", ["Operating Income", "EBIT"], "money"),
                ("Net profit", ["Net Income", "Net Income Common Stockholders"], "money"),
                ("EPS", ["Diluted EPS", "Basic EPS"], "per_share"),
            ],
            limit=6
        )

        add_margin(
            quarterly, "Operating profit", "Sales",
            "Operating margin %"
        )

        # Balance sheet

        balance = build_table(
            t.balance_sheet,
            [
                ("Equity capital", ["Common Stock", "Ordinary Shares Number"], "money"),
                ("Total equity", ["Stockholders Equity", "Common Stock Equity"], "money"),
                ("Borrowings", ["Total Debt"], "money"),
                ("Total liabilities", ["Total Liabilities Net Minority Interest"], "money"),
                ("Cash", ["Cash And Cash Equivalents"], "money"),
                ("Total assets", ["Total Assets"], "money"),
            ]
        )

        # Cash flow statement

        cashflow = build_table(
            t.cashflow,
            [
                ("Operating activity", ["Operating Cash Flow"], "money"),
                ("Investing activity", ["Investing Cash Flow"], "money"),
                ("Financing activity", ["Financing Cash Flow"], "money"),
                ("Free cash flow", ["Free Cash Flow"], "money"),
            ]
        )

        # ROCE calculation

        ebit = latest(
            t.financials,
            ["EBIT", "Operating Income"]
        )

        total_assets = latest(
            t.balance_sheet,
            ["Total Assets"]
        )

        current_liab = latest(
            t.balance_sheet,
            ["Current Liabilities"]
        )

        roce = None

        if (
            ebit is not None
            and total_assets is not None
            and current_liab is not None
        ):

            cap_employed = total_assets - current_liab

            if cap_employed > 0:
                roce = round(
                    ebit / cap_employed * 100, 2
                )

        # Financial ratios

        roe = clean(info.get("returnOnEquity"))

        roe = (
            round(roe * 100, 2)
            if roe is not None else None
        )

        de_raw = clean(info.get("debtToEquity"))

        debt_to_equity = (
            round(de_raw / 100, 2)
            if de_raw is not None else None
        )

        rate = clean(info.get("dividendRate"))

        div_yield = (
            round(rate / price * 100, 2)
            if rate and price else 0.0
        )

        pe = clean(info.get("trailingPE"))

        pb = clean(info.get("priceToBook"))

        # Shareholding

        insiders = clean(
            info.get("heldPercentInsiders")
        )

        institutions = clean(
            info.get("heldPercentInstitutions")
        )

        insiders = (
            round(insiders * 100, 2)
            if insiders is not None else None
        )

        institutions = (
            round(institutions * 100, 2)
            if institutions is not None else None
        )

        public = None

        if insiders is not None and institutions is not None:

            public = round(
                max(0.0, 100 - insiders - institutions), 2
            )

        # Growth calculations

        sales_cagr = cagr(
            row_values(income, "Sales")
        )

        profit_cagr = cagr(
            row_values(income, "Net profit")
        )

        # Pros and cons

        pros = []
        cons = []

        if debt_to_equity is not None:

            if debt_to_equity < 0.1:
                pros.append("Company is almost debt free.")

            elif debt_to_equity > 1.5:
                cons.append(
                    f"Debt is high at {debt_to_equity}x equity."
                )

        if pb is not None:

            if pb < 1:
                pros.append(
                    f"Stock is trading at {pb:.2f} times its book value."
                )

            elif pb > 8:
                cons.append(
                    f"Stock is trading at {pb:.1f} times its book value."
                )

        if roe is not None:

            if roe >= 15:
                pros.append(
                    f"Good return on equity of {roe}%."
                )

            elif roe < 8:
                cons.append(
                    f"Low return on equity of {roe}%."
                )

        if div_yield and div_yield >= 2:

            pros.append(
                f"Pays a healthy dividend, yielding {div_yield}%."
            )

        elif not div_yield:

            cons.append("Company is not paying out dividend.")

        if sales_cagr is not None:

            if sales_cagr >= 10:
                pros.append(
                    f"Sales grew {sales_cagr:.1f}% a year over the period shown."
                )

            elif sales_cagr < 0:
                cons.append(
                    f"Sales shrank {abs(sales_cagr):.1f}% a year over the period shown."
                )

        if profit_cagr is not None:

            if profit_cagr >= 15:
                pros.append(
                    f"Profit grew {profit_cagr:.1f}% a year over the period shown."
                )

            elif profit_cagr < 0:
                cons.append(
                    f"Profit fell {abs(profit_cagr):.1f}% a year over the period shown."
                )

        if pe is not None and pe > 50:

            cons.append(
                f"Stock looks expensive with a P/E of {pe:.1f}."
            )

        if insiders is not None:

            if insiders >= 50:
                pros.append(
                    f"Insider / promoter holding is high at {insiders}%."
                )

            elif insiders < 10:
                cons.append(
                    f"Insider / promoter holding is low at {insiders}%."
                )

        # Final response

        result = {

            "ticker": key,

            "name": info.get("longName") or info.get("shortName"),

            "currency": info.get("currency"),

            "exchange": info.get("fullExchangeName") or info.get("exchange"),

            "sector": info.get("sector"),

            "industry": info.get("industry"),

            "website": info.get("website"),

            "about": info.get("longBusinessSummary"),

            "ratios": {
                "market_cap": clean(info.get("marketCap")),
                "price": price,
                "high": clean(info.get("fiftyTwoWeekHigh")),
                "low": clean(info.get("fiftyTwoWeekLow")),
                "pe": pe,
                "book_value": clean(info.get("bookValue")),
                "price_to_book": pb,
                "dividend_yield": div_yield,
                "roce": roce,
                "roe": roe,
                "debt_to_equity": debt_to_equity,
                "eps": clean(info.get("trailingEps")),
                "beta": clean(info.get("beta")),
            },

            "growth": {
                "sales_cagr": (
                    round(sales_cagr, 1)
                    if sales_cagr is not None else None
                ),
                "profit_cagr": (
                    round(profit_cagr, 1)
                    if profit_cagr is not None else None
                ),
            },

            "pros": pros,

            "cons": cons,

            "shareholding": {
                "insiders": insiders,
                "institutions": institutions,
                "public": public,
            },

            "income": income,

            "quarterly": quarterly,

            "balance": balance,

            "cashflow": cashflow,
        }

        _cache[key] = (time.time(), result)

        return result

    except Exception as e:
        return {"error": str(e)}
