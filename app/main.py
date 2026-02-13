from app.core.database import engine
from app.models import models
from app.api import routes
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Create the Database Tables (Safety check)
# This ensures tables exist if they weren't created manually
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the App
app = FastAPI(title="Voice AI Agent Backend")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.error(f"Validation Error: {exc}")
    logger.error(f"Body: {body.decode()}")
    logger.error(f"Query Params: {request.query_params}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body.decode(), "query": str(request.query_params)},
    )

# 3. Connect the Routes (The API Logic)
app.include_router(routes.router, prefix="/api")

# 4. Root Endpoint (To check if server is alive)
@app.get("/")
def read_root():
    return {"message": "Voice AI Agent Backend is Running!"}