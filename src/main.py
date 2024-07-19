import threading
from fastapi import FastAPI

from src.app.interfaceWeb.routers import processoRoute

from src.app.infraestrutura.ioc import register_inversion_control
from config import config

app = FastAPI()

app.include_router(processoRoute.router)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=register_inversion_control, daemon=True).start() 
    print(f"Starting {config.app_name} version {config.version}")
