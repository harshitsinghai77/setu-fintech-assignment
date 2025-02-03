"""Main app which serves the application."""
import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse

from app.api.routers.pancard import pancard_router
from app.api.routers.back_account import bank_account_router
from app.redis_client import check_redis_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan_context(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup logic
    print("Starting app...")

    # Check Redis connection
    if not await check_redis_connection():
        print("Failed to connect to Redis. Shutting down...")
        raise RuntimeError("Failed to connect to Redis")

    yield

    # Perform shutdown tasks (e.g., closing DB connections)
    # Shutdown logic
    print("Shutting down...")

app = FastAPI(lifespan=lifespan_context)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)
    duration = time.perf_counter() - start_time

    logger.info(f"{request.method} {request.url} - {response.status_code} - {duration:.6f}s")    
    return response

# app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS for security
# app.add_middleware(TrustedHostMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return HTMLResponse(content="<h1> Hi there. 🥳</h1> ", status_code=200)

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(
    pancard_router,
    prefix="/pancard",
    tags=["KYC"],
)

app.include_router(
    bank_account_router,
    prefix="/bankaccount",
    tags=["BANK_ACCOUNT_VERIFICATION"],
)
