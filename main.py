from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, engine
from routes import student, lecturer
from contextlib import asynccontextmanager


async def close_db_connections():
    """Closes all database connections gracefully."""
    await engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    print("Application startup: Database initialized")

    try:
        yield
    finally:
        # Shutdown logic
        await close_db_connections()
        print("Application shutdown: Database connections closed")


app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from specific origins (for development use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change to specific URLs for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the router
router = APIRouter()

@router.get("/")
async def home():
    return {"message": "Welcome to the Attendance Management System API"}

# Include the router in the FastAPI app
app.include_router(router)
app.include_router(lecturer.router, tags=["Lecturer"], prefix="/lecturer")
app.include_router(student.router, tags=["Student"], prefix="/student")
