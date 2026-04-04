from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_rest import router as rest_router
from .api.routes_ws import router as ws_router
from .core.config import settings
from .services.ingest_buffer import ingest_buffer

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


@app.on_event("startup")
async def start_ingest_buffer() -> None:
	await ingest_buffer.start()


@app.on_event("shutdown")
async def stop_ingest_buffer() -> None:
	await ingest_buffer.stop()


@app.get("/")
def root() -> dict:
	return {"status": "ok", "service": "locomotive-dt"}
