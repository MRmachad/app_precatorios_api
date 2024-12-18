import random
import re
import time
import traceback
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
from src.core.util.gerenciadorDeLog import log_error

class metaScrappingTJGO(BaseScrapping):
    WORK_INST : bool = False

    def __init__(self) -> None:

        super().__init__()    
        self.projudi_url = "https://projudi.tjgo.jus.br"    
        self.servicoDeMetaProcesso =  inject.instance(ServicoDeMetaProcesso)

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]

        user_agent = random.choice(user_agents)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
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
            self.driver = webdriver.Remote(config.data["hub_selenium"], options=chrome_options)
        else:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)             
        
        print(f"meta scrapping session => {self.driver.session_id }", flush=True)           

        self.driver.implicitly_wait(10)   
        self.driver.set_page_load_timeout(60)  


    async def obtenha_inicio_paginacao(self) -> datetime | None:
        try:
            data_ultima_pub = await self.servicoDeMetaProcesso.obtenha_ultima_data_publicacao()
            if(data_ultima_pub == None):
                return datetime(2020, 1, 1)
            
            self.driver.get(f"{self.projudi_url}/ConsultaPublicacao") 

            self.driver.find_element(By.ID, "Texto").send_keys("Expeça-se Precatório OU precatório")
            self.driver.find_element(By.ID, "DataFinal").send_keys(datetime.now().strftime("%d/%m/%Y"))
            self.driver.find_element(By.ID, "DataInicial").send_keys((data_ultima_pub + relativedelta(days=1)).strftime("%d/%m/%Y"))

            self.driver.find_element(By.NAME, "Localizar").click()

            campo_pagina = self.driver.find_elements(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')

            if(len(campo_pagina) > 0):
                return data_ultima_pub + relativedelta(days=1)
            else:
                print(f"\nAtualizando meta processos \n", flush=True)
                return datetime(2020, 1, 1)
            
        except Exception as e:            
            print(f"Erro no worker metaScrappingTJGO busca data incial {e}")  

    async def work(self) -> Any:
        
        if(not metaScrappingTJGO.WORK_INST):   
            
            metaScrappingTJGO.WORK_INST = True

            try:             
                end_date = datetime.now()
                start_date = await self.obtenha_inicio_paginacao()
                
                current_date = start_date 

                while current_date <= end_date:
                    try:                        
                        _metaProcessos : List[MetaProcessoSchemma]= []
                        stop_date = current_date + relativedelta(days=1)

                        print(f"data corrente meta consulta => {current_date.strftime("%d/%m/%Y")}  => {stop_date.strftime("%d/%m/%Y")}", flush=True)

                        self.driver.get(f"{self.projudi_url}/ConsultaPublicacao") 

                        self.driver.find_element(By.ID, "Texto").send_keys("Expeça-se Precatório OU precatório")
                        self.driver.find_element(By.ID, "DataFinal").send_keys(stop_date.strftime("%d/%m/%Y"))
                        self.driver.find_element(By.ID, "DataInicial").send_keys(current_date.strftime("%d/%m/%Y"))

                        self.driver.find_element(By.NAME, "Localizar").click()

                        try:
                            campo_pagina = self.driver.find_element(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')                     
                            valor_pagina = campo_pagina.get_attribute("value")   
                        except: 
                            continue
                        
                        for pagina in range(1, int(valor_pagina) + 1):

                            try:                              

                                try:
                                    campo_pagina = self.driver.find_element(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')                              
                                    campo_pagina.clear()  
                                    campo_pagina.send_keys(str(pagina))  
                                    botao_ir = self.driver.find_element(By.XPATH, '//*[@value="Ir"]')
                                    botao_ir.click()      
                                    
                                    numeroProcesso = self.driver.find_element(By.XPATH, "//*[@id='formLocalizar']//h4[contains(text(), '-') or contains(text(), '.')]")
                                    dataPublicacao = self.driver.find_element(By.XPATH, "//*[@id='formLocalizar']//div[@class='search-result']/p/b/i[contains(text(), 'Publicado')]")                      
                                except Exception as e:                                    
                                    log_error(e)
                                    print(f"Erro ao clicar em botão ir {pagina}")   

                                    self.driver.refresh() 
                                    time.sleep(3) 
                                    try:
                                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CaixaTextoPosicionar"]')))
                                        
                                        campo_pagina = self.driver.find_element(By.XPATH, '//*[@id="CaixaTextoPosicionar"]')
                                        campo_pagina.clear()  
                                        campo_pagina.send_keys(str(pagina))  
                                        botao_ir = self.driver.find_element(By.XPATH, '//*[@value="Ir"]')
                                        botao_ir.click()
                                        
                                        numeroProcesso = self.driver.find_element(By.XPATH, "//*[@id='formLocalizar']//h4[contains(text(), '-') or contains(text(), '.')]")
                                        dataPublicacao = self.driver.find_element(By.XPATH, "//*[@id='formLocalizar']//div[@class='search-result']/p/b/i[contains(text(), 'Publicado')]")   
                                    except Exception as e:                                   
                                        log_error(e)
                                        print(f"Erro após refresh na página {pagina}")     
                                        continue                              

                                metaProcesso : MetaProcessoSchemma = MetaProcessoSchemma(
                                    NumeroProcesso=numeroProcesso.text.replace("-","."),         
                                    NumeroProcessoConsulta=  re.search(r'\d{7}[-.]\d{2}', numeroProcesso.text).group().replace(".","-"),
                                    DataPublicacao=datetime.strptime(dataPublicacao.text.split('Publicado em ')[1], '%d/%m/%Y %H:%M:%S')
                                )
                                metaProcesso.add_tipo(TipoDeProcesso.PRECATORIO)

                                _metaProcessos.append(metaProcesso)
                            except Exception as e:
                                log_error(e)
                                print(f"Erro após refresh na página {pagina}")   

                        if _metaProcessos:
                            await self.servicoDeMetaProcesso.adicioneTodosCasoNaoExista(_metaProcessos)
                            
                    except Exception as e:   
                        log_error(e)
                        print(f"Erro no ciclo de paginação do worker metaScrappingTJGO")   
                    finally:
                            current_date += relativedelta(days=1)                    
            except Exception as e:                                     
                log_error(e)                
                print(f"Erro geral no worker metaScrappingTJGO")  
            finally:
                metaScrappingTJGO.WORK_INST = False
            
        
        





















         
        

        