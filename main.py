import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from routers.explain import router as explain_router

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("labexplain")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for graceful startup and shutdown."""
    logger.info("=" * 60)
    logger.info("🎓 LabExplain Backend Starting Up...")
    logger.info(f"🤖 Inference Engine: Groq / {settings.MODEL_NAME}")
    logger.info(f"🔒 Session PIN Protection: Active (Default: {settings.SESSION_PIN})")
    logger.info(f"🚀 Listening Port: {settings.PORT}")

    if not settings.GROQ_API_KEY:
        logger.warning(
            "⚠️  WARNING: GROQ_API_KEY is not set. API calls will fail until an API key is provided."
        )
    else:
        logger.info("✅ Groq API key detected.")
    logger.info("=" * 60)

    yield

    logger.info("👋 LabExplain Backend gracefully shutting down.")


# Initialize FastAPI application
app = FastAPI(
    title="LabExplain API",
    description=(
        "Zero-login, peer-accessible university code tutor powered by "
        "Google's Gemma 2 (gemma2-9b-it) via Groq Cloud."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Configure CORS middleware (allow all origins for lab network compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register API routers
app.include_router(explain_router)


# 3. Health-check endpoint
@app.get(
    "/health",
    tags=["system"],
    summary="Health check endpoint",
    description="Returns the operational status of the service and active model name.",
)
async def health_check():
    return {
        "status": "ok",
        "model": settings.MODEL_NAME,
        "service": "LabExplain",
        "session_pin_configured": bool(settings.SESSION_PIN),
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


# 4. Mount static assets directory and serve frontend single-page app
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_root():
    """Serves the frontend single-page application at the root route."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={
            "service": "LabExplain API",
            "message": "Backend is active. Frontend index.html not yet installed in static/ directory.",
            "docs": "/docs",
            "health": "/health",
        }
    )


if __name__ == "__main__":
    # Render and cloud platforms supply PORT as an environment variable
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
