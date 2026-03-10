from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

client = OpenAI()

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/test-openai")
def test_openai():
    try:
        r = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": "responda apenas OK"}
            ]
        )

        return {
            "success": True,
            "response": r.choices[0].message.content
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
