import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.firebase.firestore_service import FirestoreService

# ✅ MERGED: Import all necessary controllers from both features
from src.controllers import query_controller, auth_controller, conversation_controller
from src.controllers import allin1_controller  # <-- The new controller

# ✅ MERGED: Load environment variables from .env file (e.g., for FIREBASE_CREDENTIALS_PATH)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    # ✅ MERGED: Updated title and description for the combined application
    title="Allin1 AI Platform",
    description="An integrated platform featuring an LLM-Routed Query Engine and an Autonomous Task Orchestrator.",
    version="2.0.0"
)

# Add CORS middleware (no changes from your original code)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """✅ MERGED: Application startup event to initialize services and OpenAPI."""
    
    # 1. Initialize Firestore (critical new step for robust startup)
    creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not creds_path:
        logger.critical("FATAL: 'FIREBASE_CREDENTIALS_PATH' environment variable not set or .env file not found.")
    elif not FirestoreService.initialize(credentials_path=creds_path):
        logger.critical(f"FATAL: Firestore could not be initialized. Check the path: {creds_path}")
    else:
        logger.info("Application startup: Firestore is connected.")

    # 2. Configure Custom OpenAPI for JWT Bearer Auth (preserved from your original code)
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi

# ✅ MERGED: Include all API routers for both features
app.include_router(query_controller.router)
app.include_router(auth_controller.router)
app.include_router(conversation_controller.router)
app.include_router(allin1_controller.router)  # <-- The new router is added here

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Allin1 AI Platform is running!"}

# Main execution block (no changes)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)