from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Chào mừng bạn đến với ứng dụng FastAPI!"}

@app.get("/health")
def read_health():
    return {"status": "ok"}