import json
import random
from typing import Any

import inject
import requests
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin, ProcessoSchemma
from src.app.dominio.services.servicoDeProcesso import ServicoDeProcesso
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager

from config import config

class scrappingTJGO(BaseScrapping):

    def __init__(self) -> None:
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
        if(config.ehProd):
            driver_chrome = webdriver.Remote(config.data["hub_selenium"], options=chrome_options)
        else:
            driver_chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 
                         
        driver_chrome.set_page_load_timeout(30)
        #############
        driver_chrome.get("https://projudi.tjgo.jus.br")
        driver_chrome.find_element(By.NAME, "Usuario").send_keys("01093980176")
        driver_chrome.find_element(By.NAME, "Senha").send_keys("Capfi@123")
        driver_chrome.find_element(By.XPATH, "//form[@id='formLogin']//input[@type='submit' and @value='Entrar']").click()
        link_Busca_Process = driver_chrome.find_element(By.XPATH, '//*[@id="1m1"]').get_attribute('href')
        ##############
        size = 100
        search_after = None

        token = config.data["connections"]["datajud"]["token"]
        tokenScheme = config.data["connections"]["datajud"]["schema"]
        baseAdress = config.data["connections"]["datajud"]["tribunais"]["tjgo"]

            

        headers = {
            "Authorization": f"{tokenScheme} {token}",
            "Content-Type": "application/json"
        }

        body = {
            "size": size,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"classe.codigo": 12168}},
                        {"match": {"classe.codigo": 156}},
                        {"match": {"classe.codigo": 12079}},
                        {"match": {"classe.codigo": 12078}}
                    ]
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
                    ePrecatorio = False
                    classe = processo["_source"]["classe"]["nome"]
                    numeroProcesso = processo["_source"]["numeroProcesso"]
                    processoCode = f"{numeroProcesso[0:7]}-{numeroProcesso[7:9]}"

                    search_after =  processo["sort"]            

                    try:
                        ######################################
                        driver_chrome.get(link_Busca_Process) 
                        driver_chrome.find_element(By.XPATH, '//*[@id="fieldsetDadosProcesso"]/div[1]//button[@name = "imaLimparProcessoStatus"]').click()
                        #####################################
                        driver_chrome.execute_script("window.Serventia = {};")                   
                        driver = driver_chrome
                    except:
                        continue
                    try:
                        driver.find_element(By.NAME, "ProcessoNumero").clear()
                        driver.find_element(By.NAME, "ProcessoNumero").send_keys(processoCode + Keys.RETURN)
                        driver.find_element(By.NAME, "imgSubmeter").click()

                        if(len(driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')) > 0):
                            driver.find_elements(By.XPATH, '/html/body/div[4]/div[3]/div/button')[0].click()
                            continue

                        nome = driver.find_elements(By.XPATH, '//span[@class="span1 nomes"]')
                        #############################################################################
                        nomeAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
                        CpfCNPJ_NomePoloAtivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Ativo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")
                        nomePassivo= driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[text()='Nome']/following-sibling::span[contains(@class, 'span1 nomes')]")
                        CpfCNPJ_PoloPassivo = driver.find_elements(By.XPATH, "//fieldset[@id='VisualizaDados'][contains(legend, 'Polo Passivo')]//div[contains(text(), 'CPF/CNPJ')]/following-sibling::span[@class='span2']")               
                        ###############################################################################
                        valorCausa = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[4]')
                        movimentacao = driver.find_elements(By.CLASS_NAME, "filtro_coluna_movimentacao")
                        assunto = driver.find_elements(By.XPATH, '//*[@id="VisualizaDados"]/span[3]/table/tbody/tr/td')
                        serventia = driver.find_elements(By.XPATH, '/html/body/div[4]/form/div[1]/fieldset/fieldset/fieldset[3]/span[1]')

                        for item in movimentacao:
                            if ("precatório" in item.text.lower()):
                                ePrecatorio = True
                                break 

                        if not ePrecatorio:
                            break

                        processo : ProcessoSchemma = ProcessoSchemma(
                            Classe= classe,
                            NumeroProcesso = numeroProcesso,
                            NumeroProcessoConsulta= processoCode,
                            CpfCNPJNomePoloAtivo= ",".join([x.text for x in CpfCNPJ_NomePoloAtivo]) if len(CpfCNPJ_NomePoloAtivo) > 0  else '',############################################
                            CpfCNPJPoloPassivo= ",".join([x.text for x in CpfCNPJ_PoloPassivo]) if len(CpfCNPJ_PoloPassivo) > 0  else '',################################################
                            NomePoloAtivo= ", ".join([x.text for x in nomeAtivo]) if len(nomeAtivo) > 0  else '',
                            NomePoloPassivo= ", ".join([x.text for x in nomePassivo]) if len(nomePassivo) > 0  else '',
                            Assunto= assunto[0].text if len(assunto) > 0  else '',
                            Valor= valorCausa[0].text if len(valorCausa) > 0  else '',
                            Serventia = serventia[0].text if len(serventia) > 0  else '' 

                        )

                                        

                        processo_criado : ProcessoMixin = await servicoDeProcesso.adicione(processo)

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

        