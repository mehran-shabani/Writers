from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router

app = FastAPI(
    title="Writers API",
    description="A task management application API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Writers API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
