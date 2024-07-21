import json
import random
from typing import Any
import unicodedata

import inject
import requests
import selenium
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin, ProcessoSchemma
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

class scrappingTJGO(BaseScrapping):

    def __init__(self) -> None:

        super().__init__()
        
        self.servicoDeProcesso =  inject.instance(ServicoDeProcesso)

        self.size = 100
        self.projudi_url = "https://projudi.tjgo.jus.br"
        self.projudi_login = config.data["connections"]["projudi"]["login"]
        self.projudi_senha = config.data["connections"]["projudi"]["senha"]
        self.token = config.data["connections"]["datajud"]["token"]
        self.tokenScheme = config.data["connections"]["datajud"]["schema"]
        self.baseAdress = config.data["connections"]["datajud"]["tribunais"]["tjgo"]

    def remover_acentos(self, texto):
        texto_decomposto = unicodedata.normalize('NFD', texto)
        texto_sem_acentos = ''.join(char for char in texto_decomposto if unicodedata.category(char) != 'Mn')
        return texto_sem_acentos
    
    def verifica_filtros_poloPassivo(self, polo:str):
        filtros = ["Goias","Goiás","Goiasprev", "Goiásprev", "Goiânia", "Goiania", "INSS", "Instituto Nacional do Seguro Social", "União Federal", "Uniao Federal"]
        polo_sem_acentos = self.remover_acentos(polo).lower()        
        for filtro in filtros:
            filtro_sem_acentos = self.remover_acentos(filtro).lower()
            if filtro_sem_acentos in polo_sem_acentos:
                return True
        return False
    
    def verifica_filtros_movimento(self, movimento:str):
        filtros = ["precatorio"]
        movimento_sem_acentos = self.remover_acentos(movimento).lower()        
        for filtro in filtros:
            filtro_sem_acentos = self.remover_acentos(filtro).lower()
            if filtro_sem_acentos in movimento_sem_acentos:
                return True
        return False

    async def findAndInsert(self, body:dict[str, Any], headers:dict[str, str], driver:WebDriverChrome | WebDriverRemote):        
        
        search_after = None

        while True:
            response = requests.post(f"{self.baseAdress}/_search", json=body, headers=headers)

            if(response.ok and len(json.loads(response.text)["hits"]["hits"]) > 0):
                for processo in json.loads(response.text)["hits"]["hits"]:
                    ePrecatorio = False
                    classe = processo["_source"]["classe"]["nome"]
                    numeroProcesso = processo["_source"]["numeroProcesso"]
                    processoCode = f"{numeroProcesso[0:7]}-{numeroProcesso[7:9]}"

                    search_after =  processo["sort"]            

                    driver.get(f"{self.projudi_url}/BuscaProcesso") 
                    driver.find_element(By.XPATH, '//*[@id="fieldsetDadosProcesso"]/div[1]//button[@name = "imaLimparProcessoStatus"]').click()
                    driver.execute_script("window.Serventia = {};")    
                
                    try:
                        driver.find_element(By.NAME, "ProcessoNumero").clear()
                        driver.find_element(By.NAME, "ProcessoNumero").send_keys(processoCode + Keys.RETURN)
                        driver.find_element(By.NAME, "imgSubmeter").click()

                        if(len(driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')) > 0):
                            driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')[0].click()
                            continue

                        nome = driver.find_elements(By.XPATH, '//span[@class="span1 nomes"]')
                        valorCausa = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[4]')
                        movimentacao = driver.find_elements(By.CLASS_NAME, "filtro_coluna_movimentacao")
                        assunto = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[3]/table/tbody/tr/td')
                        serventia = driver.find_elements(By.XPATH, "(//fieldset[@id='VisualizaDados']//div[contains(text(),'Serventia')]/following::span[@class='span1'])[1]")

                        nomeAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
                        CpfCNPJ_NomePoloAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")
                        nomePassivo= driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
                        CpfCNPJ_PoloPassivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")    
                        
                        for item in movimentacao:
                            if (self.verifica_filtros_movimento(item.text)):
                                ePrecatorio = True
                                break 

                        if ePrecatorio and len(nomePassivo) > 0 and self.verifica_filtros_poloPassivo(", ".join([x.text for x in nomePassivo])):                            
                            processo : ProcessoSchemma = ProcessoSchemma(
                                Classe= classe,
                                NumeroProcesso = numeroProcesso,
                                NumeroProcessoConsulta= processoCode,
                                CpfCNPJNomePoloAtivo= ",".join([x.text for x in CpfCNPJ_NomePoloAtivo]) if len(CpfCNPJ_NomePoloAtivo) > 0 else '',
                                CpfCNPJPoloPassivo= ",".join([x.text for x in CpfCNPJ_PoloPassivo]) if len(CpfCNPJ_PoloPassivo) > 0 else '',
                                NomePoloAtivo= ", ".join([x.text for x in nomeAtivo]) if len(nomeAtivo) > 0  else '',
                                NomePoloPassivo= ", ".join([x.text for x in nomePassivo]) if len(nomePassivo) > 0  else '',
                                Assunto= assunto[0].text if len(assunto) > 0  else '',
                                Valor= valorCausa[0].text if len(valorCausa) > 0  else '',
                                Serventia = serventia[0].text if len(serventia) > 0  else ''                
                            )
                            processo_existente : ProcessoMixin = await self.servicoDeProcesso.obtenha_por_numeroProcesso(numeroProcesso)
                            if(processo_existente is not None):
                                processo_criado: ProcessoMixin = await self.servicoDeProcesso.atualize_por_id(processo,processo_existente.uuid)
                            else:
                                processo_criado : ProcessoMixin = await self.servicoDeProcesso.adicione(processo)

                    except Exception as e:
                        print(f"Erro ao obter informações: {e}")
                        pass
                    finally:
                        driver.back()
            else:
                break
            
            if search_after == None:
                driver.quit()
                break
            else:
                print(f"paginando pos {search_after}")
                body["search_after"] = search_after
        

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
            chrome_options.add_argument(f"user-agent={user_agent}")
            chrome_options.add_argument("--disable-blink-features=AutomationOrigin")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            if(config.ehProd):
                driver_chrome = webdriver.Remote(config.data["hub_selenium"], options=chrome_options)
            else:
                driver_chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 
                            
            driver_chrome.set_page_load_timeout(30)        

            driver_chrome.get(self.projudi_url)
            driver_chrome.find_element(By.NAME, "Usuario").send_keys(self.projudi_login)
            driver_chrome.find_element(By.NAME, "Senha").send_keys(self.projudi_senha)
            driver_chrome.find_element(By.XPATH, "//form[@id='formLogin']//input[@type='submit' and @value='Entrar']").click()
            link_Busca_Process = driver_chrome.find_element(By.XPATH, '//*[@id="1m1"]').get_attribute('href')

            headers = {
                "Authorization": f"{self.tokenScheme} {self.token}",
                "Content-Type": "application/json"
            }

            body = {
                "size": self.size,                
                "sort": [
                    {
                        "@timestamp": {
                            "order": "asc"
                        }
                    }
                ]
            }
            
            await self.findAndInsert(body=body,headers=headers,driver=driver_chrome)

        except Exception as e:
            print(f"Erro no worker{e}")  
            pass
        
        
         
        

        