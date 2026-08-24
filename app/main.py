from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api import questions, statistics, topics


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Quiz Learning Platform",
    description="Платформа для обучения с тестами",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")

# HTML страницы
@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path("app/templates/index.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Quiz Platform</h1><p>Index page not found</p>"

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    html_path = Path("app/templates/admin.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Admin Panel</h1><p>Admin page not found</p>"

@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page():
    html_path = Path("app/templates/statistics.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Statistics</h1><p>Statistics page not found</p>"