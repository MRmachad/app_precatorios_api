from typing import IO
from src.app.dominio.models.storage.blob import BlobInfo


class ServicoDeStorage:
        
    async def removeBlob(self, container:str, id:str):
        pass
    
    async def obtenhaBlob(self, container:str, id:str) -> BlobInfo:        
        pass

    async def obtenhaBlobs(self, container:str, prefix:str = None):
        pass

    async def verifiqueExistencia(self, container:str, blob_name:str):
        pass

    async def uploadBlob(self, container_name:str, blob_name:str, content:bytes | str | IO[bytes], content_type:str):
        pass
