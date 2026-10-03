from fastapi import FastAPI
from app.db import Base,engine
from app.api import router
app=FastAPI(title="Journey Simulation Engine",version="1.0.0")
app.include_router(router)
@app.on_event("startup")
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
@app.get("/health")
async def health():return {"status":"ok"}
