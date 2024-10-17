import random
import re
import time
from typing import Any, List

import inject
import selenium
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.app.dominio.models.dadosTribunais.metaProcesso import MetaProcessoMixin, MetaProcessoSchemma
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin, ProcessoSchemma
from src.app.dominio.services.servicoDeMetaProcesso import ServicoDeMetaProcesso
from src.app.dominio.services.servicoDeProcesso import ServicoDeProcesso
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager
from src.app.dominio.basicos.Enumeradores.enumeradorTipoProcesso import TipoDeProcesso
from selenium.webdriver.remote.webdriver import WebDriver as WebDriverRemote
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriverChrome
from config import config

class metaScrappingTJGO(BaseScrapping):

    def __init__(self) -> None:

        super().__init__()    
        self.projudi_url = "https://projudi.tjgo.jus.br"    
        self.servicoDeMetaProcesso =  inject.instance(ServicoDeMetaProcesso)

    async def obtenha_inicio_paginacao(self, driver:WebDriverRemote | WebDriverChrome) -> datetime | None:
        try:
            data_ultima_pub = await self.servicoDeMetaProcesso.obtenha_ultima_data_publicacao()
            if(data_ultima_pub == None):
                return datetime(2020, 1, 1)
            
            driver.get(f"{self.projudi_url}/ConsultaPublicacao") 

            driver.find_element(By.ID, "Texto").send_keys("Expeça-se Precatório OU precatório")
            driver.find_element(By.ID, "DataFinal").send_keys(datetime.now().strftime("%d/%m/%Y"))
            driver.find_element(By.ID, "DataInicial").send_keys((data_ultima_pub + relativedelta(days=1)).strftime("%d/%m/%Y"))

            driver.find_element(By.NAME, "Localizar").click()

            campo_pagina = driver.find_elements(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')

            if(campo_pagina.count() > 0):
                return data_ultima_pub + relativedelta(days=1)
            else:
                return None
            
        except Exception as e:            
            print(f"Erro no worker metaScrappingTJGO busca data incial {e}")  

    async def work(self) -> Any:
        try:                
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]

            user_agent = random.choice(user_agents)
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("enable-automation")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={user_agent}")
            chrome_options.add_argument("--disable-blink-features=AutomationOrigin")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            if(config.ehProd):
                driver = webdriver.Remote(config.data["hub_selenium"], options=chrome_options)
            else:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 
                            
            driver.implicitly_wait(10)   
            driver.set_page_load_timeout(30)  

            end_date = datetime.now()
            start_date = await self.obtenha_inicio_paginacao(driver)

            if(start_date != None):
                current_date = start_date
                while current_date <= end_date:
                    try:
                        _metaProcessos : List[MetaProcessoSchemma]= []
                        stop_date = current_date + relativedelta(months=1)

                        driver.get(f"{self.projudi_url}/ConsultaPublicacao") 

                        driver.find_element(By.ID, "Texto").send_keys("Expeça-se Precatório OU precatório")

                        driver.find_element(By.ID, "DataFinal").send_keys(stop_date.strftime("%d/%m/%Y"))
                        driver.find_element(By.ID, "DataInicial").send_keys(current_date.strftime("%d/%m/%Y"))

                        driver.find_element(By.NAME, "Localizar").click()

                        campo_pagina = driver.find_elements(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')
                        
                        if(campo_pagina.count() > 0): 

                            valor_pagina = campo_pagina[0].get_attribute("value")   

                            for pagina in range(1, int(valor_pagina) + 1):
                                try:
                                    campo_pagina[0].clear()  
                                    campo_pagina[0].send_keys(str(pagina))  

                                    try:
                                        botao_ir = driver.find_element(By.XPATH, '//*[@value="Ir"]')
                                        botao_ir.click()      
                                        
                                        numeroProcesso = driver.find_elements(By.XPATH, "//*[@id='formLocalizar']//h4[contains(text(), '-') or contains(text(), '.')]")
                                        dataPublicacao = driver.find_elements(By.XPATH, "//*[@id='formLocalizar']//div[@class='search-result']/p/b/i[contains(text(), 'Publicado')]")                      
                                    except Exception as e:
                                        driver.refresh()  
                                        try:
                                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CaixaTextoPosicionar"]')))
                                            campo_pagina[0].clear()  
                                            campo_pagina[0].send_keys(str(pagina))  
                                            botao_ir = driver.find_element(By.XPATH, '//*[@value="Ir"]')
                                            botao_ir.click()
                                            
                                            numeroProcesso = driver.find_elements(By.XPATH, "//*[@id='formLocalizar']//h4[contains(text(), '-') or contains(text(), '.')]")
                                            dataPublicacao = driver.find_elements(By.XPATH, "//*[@id='formLocalizar']//div[@class='search-result']/p/b/i[contains(text(), 'Publicado')]")   
                                        except Exception as e:
                                            print(f"Erro após refresh na página {pagina}: {e}")                                   

                                    metaProcesso : MetaProcessoSchemma = MetaProcessoSchemma(
                                        NumeroProcesso=numeroProcesso[0].text,         
                                        NumeroProcessoConsulta=  re.search(r'\d{7}[-.]\d{2}', numeroProcesso[0].text).group().replace(".","-"),
                                        DataPublicacao=datetime.strptime(dataPublicacao[0].text.split('Publicado em ')[1], '%d/%m/%Y %H:%M:%S')
                                    )
                                    metaProcesso.add_tipo(TipoDeProcesso.PRECATORIO)

                                    _metaProcessos.append(metaProcesso)
                                except Exception as e:
                                    print(f"Erro na página {pagina}: {e}")
                                    pass

                            await self.servicoDeMetaProcesso.adicioneTodosCasoNaoExista(_metaProcessos)
                    except Exception as e:
                        print(f"Erro na paginação de metaProcesso {e}")  
                        pass
                    finally:
                        current_date += relativedelta(months=1)
        except Exception as e:
            print(f"Erro no worker metaScrappingTJGO {e}")  
            pass
        
        
         
        

        