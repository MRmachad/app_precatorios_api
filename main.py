from fastapi import FastAPI

from src.app.interfaceWeb.routers import processoRoute

from src.app.infraestrutura.ioc import register_inversion_control

register_inversion_control()

app = FastAPI()

app.include_router(processoRoute.router)

