import json
import random
from typing import Any

import inject
import requests
from src.app.dominio.models.dadosTribunais.processo import ProcessoSchemma
from src.app.dominio.services.servicoDeProcesso import ServicoDeProcesso
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.edge.service import Service as ServiceEdge
from selenium.webdriver.edge.options import Options as OptionsEdge
from webdriver_manager.microsoft import EdgeChromiumDriverManager

class scrappingTJGO(BaseScrapping):

    def __init__(self) -> None:
        self.baseAdress = "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo"
        self.token = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw"
        self.tokenScheme = "APIKey" 
        super().__init__()
        
    async def work(self) -> Any:

        servicoDeProcesso =  inject.instance(ServicoDeProcesso)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        user_agent = random.choice(user_agents)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-blink-features=AutomationOrigin")
        chrome_options.add_argument(f"user-agent={user_agent}")
        driver_chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)                    
        driver_chrome.implicitly_wait(30)
        driver_chrome.set_page_load_timeout(30)
        
        size = 100
        search_after = None
        tokenScheme = "APIKey" 
        token = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw"
        baseAdress = "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo"

            

        headers = {
            "Authorization": f"{tokenScheme} {token}",
            "Content-Type": "application/json"
        }

        body = {
            "size": size,
            "query": {
                "match": {
                    "classe.codigo": 12078
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ]
        }

         
        while True:
            response = requests.post(f"{baseAdress}/_search", json=body, headers=headers)

            if(response.ok):
                for processo in json.loads(response.text)["hits"]["hits"]:
                    classe = processo["_source"]["classe"]["nome"]
                    numeroProcesso = processo["_source"]["numeroProcesso"]
                    processoCode = f"{numeroProcesso[0:7]}-{numeroProcesso[7:9]}"

                    search_after =  processo["sort"]                    
                    print(f"after atualizado {search_after}")

                    try:
                        print("buscando por chrome")
                        driver_chrome.get("https://projudi.tjgo.jus.br/BuscaProcesso") 
                        driver_chrome.execute_script("window.Serventia = {};")                   
                        driver = driver_chrome
                    except:
                        continue
                    try:
                        print(processoCode)
                        print(numeroProcesso)

                        driver.find_element(By.NAME, "ProcessoNumero").send_keys(processoCode + Keys.RETURN)
                        driver.find_element(By.NAME, "imgSubmeter").click()

                        serventia = driver.find_element(By.XPATH, '/html/body/div[4]/form/div[1]/fieldset/fieldset/fieldset[3]/span[1]')
                        nome = driver.find_element(By.XPATH, '//span[@class="span1 nomes"]')
                        valorCausa = driver.find_element(By.XPATH, '//*[@id="VisualizaDados"]/span[4]')
                        assunto = driver.find_element(By.XPATH, '//*[@id="VisualizaDados"]/span[3]/table/tbody/tr/td')

                        processo : ProcessoSchemma = ProcessoSchemma(
                            NumeroProcesso = numeroProcesso,
                            Classe= classe,
                            Nome= nome.text if nome != None else None,
                            Assunto= assunto.text if assunto != None else None,
                            Valor= valorCausa.text if valorCausa != None else None,
                            Serventia = serventia.text if serventia != None else None
                        )
                        print(processo)
                        await servicoDeProcesso.adicione(processo)
                    except Exception as e:
                        print(f"Erro ao obter informações: {e}")
                        pass
            else:
                break

            
            if search_after == None:
                driver.quit()
                break
            else:
                print(f"paginando pos {search_after}")
                body["search_after"] = search_after

        