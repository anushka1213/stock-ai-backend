
import os

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq

load_dotenv()

router = APIRouter()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


class ChatRequest(BaseModel):
    question: str
    stock_context: dict


@router.post("/chat")
def chat(req: ChatRequest):

    try:

        prompt = f"""
        You are a helpful stock market analyst AI.

        Here is the current data for
        {req.stock_context.get('ticker')}:

        Price: {req.stock_context.get('price')}
        Change: {req.stock_context.get('change_pct')}%
        RSI: {req.stock_context.get('rsi')}
        SMA20: {req.stock_context.get('sma20')}
        Volume: {req.stock_context.get('volume')}

        User question: {req.question}

        Give a short helpful answer in 3-4 sentences.
        Always remind the user this is not financial advice.
        """

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=600
        )

        return {
            "answer": response.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)}
