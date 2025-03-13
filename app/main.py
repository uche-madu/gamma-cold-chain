from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.routers import email, call, outreach

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app lifecycle events."""
    logger.info("🚀 Starting application...")
    
    logger.info("🕒 Starting background tasks...")

    yield  # The application runs during this time

    # Cleanup on shutdown
    logger.info("🛑 Shutting down application...")

app = FastAPI(lifespan=lifespan, title="Gamma Cold Emails and Calls API", version="1.0")

# CORS Middleware (Allow frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
routers = [email.router, outreach.router]
for router in routers:
    app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Gamma Cold Emails and Calls API"}
