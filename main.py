from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
from groq import Groq
import os
from dotenv import load_dotenv
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        if hist.empty:
            return {"error": "No data found for " + ticker}

        hist["SMA20"] = hist["Close"].rolling(20).mean()
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        hist["RSI"] = 100 - (100 / (1 + gain / loss))

        current = hist.iloc[-1]
        prev = hist.iloc[-2]

        return {
            "ticker": ticker.upper(),
            "price": round(float(current["Close"]), 2),
            "change_pct": round(
                (float(current["Close"]) - float(prev["Close"])) / float(prev["Close"]) * 100, 2
            ),
            "rsi": round(float(current["RSI"]), 1) if not hist["RSI"].isna().iloc[-1] else None,
            "volume": int(current["Volume"]),
            "sma20": round(float(current["SMA20"]), 2) if not hist["SMA20"].isna().iloc[-1] else None,
            "history": [
                {"date": str(d.date()), "price": round(float(r["Close"]), 2)}
                for d, r in hist.tail(30).iterrows()
            ],
        }
    except Exception as e:
        return {"error": str(e)}

class ChatRequest(BaseModel):
    question: str
    stock_context: dict

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        prompt = f"""You are a helpful stock market analyst AI.
Here is the current data for {req.stock_context.get('ticker')}:
Price: ${req.stock_context.get('price')}
Change: {req.stock_context.get('change_pct')}%
RSI: {req.stock_context.get('rsi')}
SMA20: {req.stock_context.get('sma20')}
Volume: {req.stock_context.get('volume')}

User question: {req.question}

Give a short helpful answer in 3-4 sentences. Always remind the user this is not financial advice."""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}