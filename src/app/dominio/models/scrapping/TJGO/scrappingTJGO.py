from concurrent.futures import thread
import json
import random
import time
from typing import Any

import inject
import requests
from src.app.dominio.models.dadosTribunais.metaProcesso import MetaProcesso
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin, ProcessoSchemma
from src.app.dominio.services.servicoDeMetaProcesso import ServicoDeMetaProcesso
from src.app.dominio.services.servicoDeProcesso import ServicoDeProcesso
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver as WebDriverRemote
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriverChrome
from config import config
from src.core.util.gerenciadorDeLog import log_error

class scrappingTJGO(BaseScrapping):

    PROCESSO_EM_RASTREAMENTO_OU_FALHA : list[str] | None = None

    def __init__(self) -> None:

        super().__init__()
        
        self.servicoDeProcesso =  inject.instance(ServicoDeProcesso)
        self.servicoDeMetaProcesso =  inject.instance(ServicoDeMetaProcesso)

        self.size = 100
        self.projudi_url = "https://projudi.tjgo.jus.br"
        self.projudi_login = config.data["connections"]["projudi"]["login"]
        self.projudi_senha = config.data["connections"]["projudi"]["senha"]


    def adicione_processo_em_rastreamento(self, numero:str):        
        if scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA and len(scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA) < 100000 :            
            scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA.append(numero) 
        elif scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA:
            scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA.pop()
            scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA.append(numero) 
        else:
             scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA = [numero]

    async def work(self) -> Any:
        try:       
            time.sleep(60 * 1)

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
                driver = webdriver.Remote(config.data["hub_selenium"], options=chrome_options)
            else:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 
                    
            print(f"scrapping session => {driver.session_id }", flush=True)    

            driver.implicitly_wait(10)        
            driver.set_script_timeout(60 * 5)          
            driver.set_page_load_timeout(60 * 5)      

            driver.get(self.projudi_url)
            driver.find_element(By.NAME, "Usuario").send_keys(self.projudi_login)
            driver.find_element(By.NAME, "Senha").send_keys(self.projudi_senha)
            driver.find_element(By.XPATH, "//form[@id='formLogin']//input[@type='submit' and @value='Entrar']").click()

            primeiro_inexistente = await self.servicoDeProcesso.obtenha_data_primeiro_inexistente() if not scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA else await self.servicoDeProcesso.obtenha_data_primeiro_inexistente(scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA)

            if(primeiro_inexistente is not None):
                inexistente = primeiro_inexistente
                while True:                    
                    print(f"primeiro inexistente detalhes => {inexistente.NumeroProcesso}", flush=True)
                    self.adicione_processo_em_rastreamento(inexistente.NumeroProcesso)
                    time.sleep(1)
                    if await self.findAndInsert(metaProcesso=inexistente, driver=driver):
                        scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA.remove(inexistente.NumeroProcesso)
                    inexistente = await self.servicoDeProcesso.obtenha_data_primeiro_inexistente(scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA)
                    if(inexistente is None):
                        break
            elif scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA:
                while scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA:
                    try:
                        inexistente = await self.servicoDeMetaProcesso.obtenha_por_numeroProcesso(numero_processo=scrappingTJGO.PROCESSO_EM_RASTREAMENTO_OU_FALHA.pop())
                        print(f"primeiro inexistente detalhes RASTREAMENTO_OU_FALHA=> {inexistente.NumeroProcesso}", flush=True)
                        if(inexistente and not (await self.findAndInsert(metaProcesso=inexistente, driver=driver))):
                            print(f"Falha ao buscar detalhes de metaProcesso {inexistente.NumeroProcesso}, removido de cache")
                    except Exception as e:
                        log_error(e)
                        print(f"Erro no worker scrappingTJGO, falha ao tratar processo em falha ou rastreamento")  

        except Exception as e:
            log_error(e)
            print(f"Erro no worker scrappingTJGO")  
        
    async def findAndInsert(self, metaProcesso:MetaProcesso, driver:WebDriverChrome | WebDriverRemote):        
                 
        try:            
            driver.get(f"{self.projudi_url}/BuscaProcesso") 
            driver.find_element(By.XPATH, '//*[@id="fieldsetDadosProcesso"]/div[1]//button[@name = "imaLimparProcessoStatus"]').click()
            driver.execute_script("window.Serventia = {};")    
            driver.find_element(By.NAME, "ProcessoNumero").clear()
            driver.find_element(By.NAME, "ProcessoNumero").send_keys(metaProcesso.NumeroProcessoConsulta + Keys.RETURN)
            driver.find_element(By.NAME, "imgSubmeter").click()

            if(len(driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')) > 0):
                driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')[0].click()
                return False

            valorCausa = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[4]')
            assunto = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[3]/table/tbody/tr/td')
            serventia = driver.find_elements(By.XPATH, "(//fieldset[@id='VisualizaDados']//div[contains(text(),'Serventia')]/following::span[@class='span1'])[1]")

            nomeAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
            CpfCNPJ_NomePoloAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")
            nomePassivo= driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
            CpfCNPJ_PoloPassivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")    
                                    
            processo : ProcessoSchemma = ProcessoSchemma(
                Classe= " ",
                meta_processo_id = metaProcesso.uuid,
                NumeroProcesso = metaProcesso.NumeroProcesso,
                NumeroProcessoConsulta= metaProcesso.NumeroProcessoConsulta,
                CpfCNPJNomePoloAtivo= ",".join([x.text for x in CpfCNPJ_NomePoloAtivo]) if len(CpfCNPJ_NomePoloAtivo) > 0 else '',
                CpfCNPJPoloPassivo= ",".join([x.text for x in CpfCNPJ_PoloPassivo]) if len(CpfCNPJ_PoloPassivo) > 0 else '',
                NomePoloAtivo= ", ".join([x.text for x in nomeAtivo]) if len(nomeAtivo) > 0  else '',
                NomePoloPassivo= ", ".join([x.text for x in nomePassivo]) if len(nomePassivo) > 0  else '',
                Assunto= assunto[0].text if len(assunto) > 0  else '',
                Valor= valorCausa[0].text if len(valorCausa) > 0  else '',
                Serventia = serventia[0].text if len(serventia) > 0  else ''                
            )
            await self.servicoDeProcesso.adicione_ou_atualize_um_processo(processo)
            
            return True
        except Exception as e:
            log_error(e)
            print(f"Erro ao obter informações")
            return False
        finally:
            driver.back()
        
        
         
        

        