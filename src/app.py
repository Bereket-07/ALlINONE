from fastapi import FastAPI
from src.controllers import query_controller

# Create the FastAPI app
app = FastAPI(
    title="LLM-Routed Query Engine",
    description="Automatically routes a user's query to the most suitable LLM.",
    version="1.0.0"
)

# Include the API router
app.include_router(query_controller.router)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LLM Router is running!"}

# Note: The Uvicorn server will run this app. The following is for direct execution (e.g. `python src/app.py`)
# but the recommended way is `uvicorn src.app:app --reload`.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)