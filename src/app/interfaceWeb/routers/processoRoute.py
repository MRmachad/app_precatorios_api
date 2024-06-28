from fastapi import APIRouter
import inject

from src.app.dominio.services.servicoDeProcesso import  ServicoDeProcesso

router = APIRouter(
    prefix="/processo",
    tags=["processo"],
    responses={404: {"description": "Not found"}},
)
    
@router.get("/obter-processos")
async def root():
    service = inject.instance(ServicoDeProcesso)
    return await service.obtenha_muitos()

@router.get("/obter-processo")
async def root():
    service =  inject.instance(ServicoDeProcesso)
    return await service.obtenha_muitos()

@router.delete("/delete-processo")
async def root():
    service =  inject.instance(ServicoDeProcesso)
    return await service.obtenha_muitos()

@router.post("/atualize-processo")
async def root():
    service = inject.instance(ServicoDeProcesso)
    return await service.obtenha_muitos()