# coding: utf-8
"""
Created on Aug 27 2018

@author: Alexandre Ribas Semeler
@author: Adilson Luiz Pinto
@author: Arthur L. Oliveira
Agradecimentos
O presente trabalho foi realizado com apoio da Coordenação de Aperfeiçoamento de Pessoal de Nível Superior - Brasil (CAPES) - Código de Financiamento 001
"""
import codecs
from bs4 import BeautifulSoup
import selenium.common.exceptions
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import Firefox
# import os

url = 'http://www.researcherid.com/ViewProfileSearch.action'    # define url alvo
# Caso a execução seja feita com Chrome
# chromedriver = "../scripts/chromedriver"            # path do chromedriver
# os.environ["webdriver.chrome.driver"] = chromedriver
# driver = webdriver.Chrome(chromedriver)                         # abre browser

# abre arquivo para escrita dos resultados
with codecs.open('../dados/csv/RESEARCHID_Extraction2.tsv', 'w', 'utf-8-sig') as results:
    results.write('Name\tInstitution\tResearcher ID\tKeywords\n')   # escreve headers
results.close()
id_list = []
counter = 0     # inicializa contador de resultados e erros
errors = 0

driver = Firefox()
while True:
    try:
        driver.get(url)                                               # navega para a url
        # espera carregamento da combobox para escolher o Pais alvo
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                                        '#country > option:nth-child(33)'))).click()
        break
    except selenium.common.exceptions.TimeoutException:
        continue

# clica para submeter pesquisa
driver.find_element_by_css_selector('#submitImage > img').click()
# define limite de paginas para serem acessadas nos resultados
page_limit = int(WebDriverWait(driver, 10).until(ec.presence_of_element_located(
    (By.CSS_SELECTOR, '#criteria_requestedPage_total'))).text) // 50 + 1
# espera combobox carregar para mostrar 50 resultados por pagina
WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                                '#resultsPerPage > option:nth-child(3)'))).click()

for page in range(page_limit):      # percorre paginas de resultados da busca
    # espera tabela de resultados ser carregada
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(
        (By.CSS_SELECTOR, '#resultContainer > table:nth-child(23) > tbody > tr:nth-child(2) > td > table > tbody')))
    # define raiz da arvore de resultados para parsing
    root = BeautifulSoup(driver.page_source, 'lxml').find('td', {'class': 'resultsTableBox'}).findNext('tbody')
    with codecs.open('../dados/csv/RESEARCHID_Extraction2.tsv', 'a', 'utf-8-sig') as results:
        for item in root.findAll('tr')[1:]:     # percorre itens na tabela
            data = item.findAll('td')           # lista todos os resultados
            rid = data[4].getText().replace('\n', '').replace(' ', '')
            if rid in id_list:
                continue
            else:
                id_list.append(rid)
                # escreve resultados no arquivo de output
                results.write('%s\t%s\t%s\t%s\n' % (data[1].a.getText().replace('\n', ''),
                                                    data[2].getText().replace('\n', ''),
                                                    rid,
                                                    data[5].getText().replace('\n', '')))
                counter += 1        # incrementa contador de resultados
        results.close()
    if page < page_limit:       # testa se as paginas de resultados ja acabaram
        # clica em next page caso contrario
        WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '#resultContainer > table:nth-child(22) > tbody > tr > td:nth-child(2) > table > '
                              'tbody > tr > td:nth-child(7) > span > img'))).click()
    print counter
    try:        # tenta esperar pelo carregamento de um item da pagina como teste
        WebDriverWait(driver, 20).until(ec.presence_of_element_located(
            (By.ID, 'pageNumnull')))
    except selenium.common.exceptions.TimeoutException:     # em caso de timeout, trata o erro
        driver.get(url)     # navega para a url alvo novamente
        errors += 1         # incrementa counter de erros
        # reinicia a pesquisa
        WebDriverWait(driver, 30).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '#country > option:nth-child(33)'))).click()
        driver.find_element_by_css_selector('#submitImage > img').click()
        WebDriverWait(driver, 40).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '#resultsPerPage > option:nth-child(3)'))).click()
        page -= 1       # reduz contador de paginas navegadas em 1
        element = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[@id="pageNumnull"]')))
        element.clear()     # limpa caixa de texto com numero de paginas
        element.send_keys('%s' % page)      # escreve numero de paginas na caixa de texto
        driver.find_element_by_xpath('/html/body/div[3]/form[2]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/div/div/'
                                     'table[1]/tbody/tr/td[2]/table/tbody/tr/td[5]/a/img').click()  # clica em "go"
driver.quit()
print errors, 'errors happened. Extraction finished.'

