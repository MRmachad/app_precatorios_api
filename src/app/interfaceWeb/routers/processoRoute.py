from uuid import UUID
from fastapi import APIRouter, Path, Body
import inject

from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin
from src.app.dominio.services.servicoDeProcesso import  ServicoDeProcesso
from src.app.interfaceWeb.dtos.processoDTO import ProcessoDTO

router = APIRouter(
    prefix="/processo",
    tags=["processo"],
    responses={404: {"description": "Not found"}},
)
    
@router.get("/obter-processos")
async def root():
    service = inject.instance(ServicoDeProcesso)
    return await service.obtenha_muitos()

@router.get("/obter-processo/{processo_id}")
async def obter_processo(processo_id:str|UUID = Path(..., title="The ID of the process")):
    service =  inject.instance(ServicoDeProcesso)
    return await service.obtenha_um_por_id(processo_id)

@router.delete("/delete-processo/{processo_id}")
async def delete_processo(processo_id:str|UUID = Path(..., title="The ID of the process to delete")):
    service =  inject.instance(ServicoDeProcesso)
    return await service.remova_por_id(processo_id)

@router.put("/atualize-processo")
async def atualize_processo(processo: ProcessoDTO = Body(..., example={
                            "NumeroProcesso": "12345/2024",
                            "Classe": "Ação de Indenização por Danos Morais",
                            "Nome": "João da Silva",
                            "Assunto": "Danos Morais",
                            "Valor": "10000,00",
                            "Serventia": "Cartório da 1ª Vara Cível"
                            })):
    service = inject.instance(ServicoDeProcesso)
    return await service.atualize_por_id(processo)