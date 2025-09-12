from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import ingest, ingest_universal, eeff, eecc, cierre, inflacion, reexpresar

from .routers.clientes import router as clientes_router

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(ingest.router)
app.include_router(ingest_universal.router)
app.include_router(eeff.router)
app.include_router(eecc.router)
app.include_router(cierre.router)
app.include_router(inflacion.router)
app.include_router(reexpresar.router)

@app.get("/health")
async def health():
    return {"status":"ok"}