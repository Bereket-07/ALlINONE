from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/callback")
async def callback(request: Request):
    data = await request.json()
    # You can process the callback data here
    return JSONResponse(content={"message": "Callback received", "data": data})

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
