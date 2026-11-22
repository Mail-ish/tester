"""Opt-in local adapter. Original Session 5 domain API is unchanged."""
import os
import secrets
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from erp_logistics_api import app
TOKEN = os.environ.get("LOGISTICS_API_TOKEN")
if not TOKEN:
    raise RuntimeError("Set LOGISTICS_API_TOKEN before running the local adapter")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
@app.middleware("http")
async def require_demo_token(request, call_next):
    if request.url.path.startswith("/shipments") and request.method != "OPTIONS":
        if not secrets.compare_digest(request.headers.get("authorization", ""), "Bearer " + TOKEN):
            return JSONResponse(status_code=401, content={"error": {"code": "UNAUTHENTICATED", "message": "A valid adapter token is required"}})
    return await call_next(request)
