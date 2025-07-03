from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from src.controllers import query_controller, auth_controller
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="LLM-Routed Query Engine",
    description="Automatically routes a user's query to the most suitable LLM.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("JWT Authentication with Firestore storage initialized successfully")

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
        # Apply globally (all endpoints unless overridden)
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    app.openapi = custom_openapi

# Include the API routers
app.include_router(query_controller.router)
app.include_router(auth_controller.router)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LLM Router is running!"}

# Note: The Uvicorn server will run this app. The following is for direct execution (e.g. `python src/app.py`)
# but the recommended way is `uvicorn src.app:app --reload`.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)