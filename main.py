from fastapi import FastAPI

app = FastAPI(title="Hector Engine")

@app.get("/")
def root():
    return {"status": "hector-engine-running"}

@app.get("/health")
def health():
    return {"status": "ok"}
