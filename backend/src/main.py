from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_rest import router as rest_router
from .api.routes_ws import router as ws_router
from .core.config import settings

app = FastAPI(title="Locomotive Digital Twin API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(rest_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.get("/")
def root() -> dict:
	return {"status": "ok", "service": "locomotive-dt"}
