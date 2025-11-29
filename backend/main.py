import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.vehicles import router as vehicles_router
from endpoints.images import router as images_router
from utils.helpers import _keep_alive_loop

app = FastAPI()

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vehicles_router)
app.include_router(images_router)


@app.on_event("startup")
async def _startup_keep_alive():
    # attach task to app state so it can be cancelled on shutdown
    app.state._keep_alive_task = asyncio.create_task(_keep_alive_loop())


@app.on_event("shutdown")
async def _shutdown_keep_alive():
    task = getattr(app.state, "_keep_alive_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@app.get("/")
async def root():
    return {"message": "VehicIQ API is running!"}