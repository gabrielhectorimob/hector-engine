from fastapi import FastAPI
from openai import OpenAI
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def root():
    return {"status": "Hector Engine running"}

@app.get("/test-openai")
def test_openai():

    if not OPENAI_API_KEY:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found"
        }

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Responda apenas OK"
        )

        return {
            "success": True,
            "response": response.output_text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
