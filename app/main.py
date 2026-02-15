from fastapi import FastAPI
from core.config import settings
from routers.todos import router as todos_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Chào mừng bạn đến với ứng dụng FastAPI!"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

# Include API routes
app.include_router(
    todos_router,
    prefix=settings.api_v1_str
)