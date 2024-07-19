
import datetime
from io import BufferedReader
from typing import IO, AnyStr, Iterable
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient,BlobSasPermissions,generate_blob_sas

from src.app.dominio.models.storage.blob import BlobInfo
from src.app.dominio.services.interfaces.servicoDeStorage import ServicoDeStorage

from config import config

class ServicoDeStorageAzure(ServicoDeStorage):

    def __init__(self):
<<<<<<< HEAD
       #connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        #self.blob_service_client = BlobServiceClient.from_connection_string(connect_str)
=======
        self.blob_service_client = BlobServiceClient.from_connection_string(config.connections["storage"])
>>>>>>> master
        pass

    async def removeBlob(self, container:str, id:str):
        try:
            container_client = self.blob_service_client.get_container_client(container)
            await container_client.delete_blob(id)
        except Exception as e:            
            raise Exception(f"Erro ao remover blob: {e}") from e
    
    async def obtenhaBlob(self, container:str, id:str) -> BlobInfo:        
        try:
            container_client = self.blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(id)
            property = await blob_client.get_blob_properties()

            sas_token = generate_blob_sas(
                blob_name=id,
                container_name=container,
                permission=BlobSasPermissions(read=True),
                account_name=self.blob_service_client.account_name,
                expiry=datetime.utcnow() + datetime.timedelta(days=365*5),
                account_key=self.blob_service_client.credential.account_key,
            )
            
            return BlobInfo(
                nome=blob_client.blob_name,
                saas=f"{blob_client.url}?{sas_token}",
                contentype=property['content_settings'].content_type,
                content= blob_client.download_blob().readall()
            )
        
        except Exception as e:            
            raise Exception(f"Erro ao remover blob: {e}") from e

    async def obtenhaBlobs(self, container:str, prefix:str = None):
        try:
            container_client = self.blob_service_client.get_container_client(container)
            await container_client.create_container()
            blob_list = []
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                blob_list.append(blob.name)
            return blob_list
        except Exception as ex:
            raise Exception("Falha ao obter arquivo!") from ex

    async def verifiqueExistencia(self, container:str, blob_name:str):
        try:
            blob_client = self.blob_service_client.get_blob_client(container, blob_name)
            return await blob_client.exists()
        except Exception as ex:
            raise Exception("Falha ao fazer verificação de existência") from ex

    async def uploadBlob(self, container_name:str, blob_name:str, content:bytes | str | IO[bytes], content_type:str):
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            await container_client.create_container()
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(content, overwrite=True, content_settings={'content_type': content_type})
            content.seek(0)

            sas_token = generate_blob_sas(
                blob_name=id,
                container_name=container_name,
                permission=BlobSasPermissions(read=True),
                account_name=self.blob_service_client.account_name,
                expiry=datetime.utcnow() + datetime.timedelta(days=365*5),
                account_key=self.blob_service_client.credential.account_key,
            )
            return f"{blob_client.url}?{sas_token}"
        except Exception as ex:
            self._logger.error(f"Error uploading {blob_name}", exc_info=True)
            raise Exception("Falha ao fazer upload de arquivo!") from ex
