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
from multiprocessing import Pool
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver import Firefox
import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

options = Options()
options.add_argument("--headless")


class Control:
    def __init__(self):
        self.counter = 0
        self.article_accumulator = 0
        self.with_citation_accumulator = 0
        self.h_index_accumulator = 0
        self.existent_h_index_counter = 0


def id_cleaning(a_link):
    if '\r\n' in a_link:  # testa finais de linha para verificar se usam \n ou \r\n
        return a_link.replace(' ', '').replace('\r\n', '\t')  # troca final por \t e tira blank spaces
    else:
        return a_link.replace(' ', '').replace('\n', '\t')


def get_metrics_info(a_soup):  # function que extrai dados alvo da pagina
    return (a_soup.find(id='metrics_totalArticleCount').getText(),
            a_soup.find(id='metrics_articleCountForMetrics').getText(),
            a_soup.find(id='metrics_timesCited').getText(),
            a_soup.find(id='metrics_averagePerItem').getText(),
            a_soup.find(id='metrics_hindex').getText())

chromedriver = "../scripts/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

def parallel_scraping(a_trio):
    # driver = Firefox(firefox_options=options)
    driver = webdriver.Chrome(chromedriver)
    for rid in a_trio[0]:  # for para percorrer a lista de links
        a_trio[2].counter += 1  # incrementa counter para acompanhar progresso
        print a_trio[2].counter, ': Extracting: %s' % rid

        while True:
            try:
                driver.get('http://www.researcherid.com/rid/' + rid)  # acessa link alvo
                break
            except selenium.common.exceptions.WebDriverException:
                continue

        try:
            driver.find_elements_by_xpath('/html/body/div[3]/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/'
                                          'div[1]/ul[1]/''li[2]/a')[0].click()
            # clica para mostrar citation metrics
        except IndexError:
            print '%s apparently got no citation metrics' % rid  # exception tratada
            continue
        a_file = codecs.open(a_trio[1], 'a', 'utf-8-sig')
        try:
            WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, '#metrics_hindex')))
        except selenium.common.exceptions.TimeoutException:
            a_file.write(rid + '\t' + 'TO\tTO\tTO\tTO\tTO\n')
        else:
            root = BeautifulSoup(driver.page_source, 'lxml')  # parsing inicial
            data = get_metrics_info(root)
            if data != '':
                a_trio[2].article_accumulator += int(data[0])
                a_file.write(rid + '\t' + '%s\t%s\t%s\t%s\t%s\n' % data)
                if data[-1] > 0:
                    a_trio[2].with_citation_accumulator += int(data[1])
                    a_trio[2].h_index_accumulator += float(data[-1])
                    a_trio[2].existent_h_index_counter += 1
            else:
                a_file.write(rid + '\t' + 'NA\tNA\tNA\tNA\tNA\n')
                # aguarda carregamento da pagina para escrever no arquivo de output
        finally:
            a_file.close()
    driver.quit()  # fecha browser


if __name__ == '__main__':
    pool = Pool(processes=8)
    geckodriver = "../scripts/geckodriver"  # path do geckodriver para firefox

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chromedriver = "../scripts/chromedriver"  # path do chromedriver
    os.environ["webdriver.chrome.driver"] = chromedriver

    research = codecs.open('../dados/csv/RESEARCHID_Extraction2.tsv', 'r', 'utf-8-sig')  # abre arquivo
    link_list = research.readlines()[1:]  # extrai linhas do arquivo em uma lista
    research.close()  # fecha arquivo

    master = codecs.open('../dados/csv/RESEARCHERID-ALL-METRICS.tsv', 'r', 'utf-8')
    id_list = master.readlines()[1:]
    id_list.sort()
    master.close()

    for x in range(len(id_list)):
        if id_list[x].split('\t')[0][0].isalpha():
            id_list[x] = '%s' % id_list[x].split('\t')[0]
        else:
            id_list[x] = '%s' % id_list[x].split('\t')[0][1:]
    for x in range(len(link_list)):
        link_list[x] = id_cleaning(link_list[x].split('\t')[2])
    print id_list[-5:]
    for item in range(len(link_list)):
        try:
            if link_list[item] in id_list:
                del link_list[item]
                print len(link_list)
        except IndexError:
            break

    with open('../dados/error_logs/ResearcherIDanonScraping.txt', 'w') as log:
        out_file1 = codecs.open('../dados/csv/RESEARCHIDresultsPart1-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file2 = codecs.open('../dados/csv/RESEARCHIDresultsPart2-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file3 = codecs.open('../dados/csv/RESEARCHIDresultsPart3-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file4 = codecs.open('../dados/csv/RESEARCHIDresultsPart4-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file5 = codecs.open('../dados/csv/RESEARCHIDresultsPart5-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file6 = codecs.open('../dados/csv/RESEARCHIDresultsPart6-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file7 = codecs.open('../dados/csv/RESEARCHIDresultsPart7-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        out_file8 = codecs.open('../dados/csv/RESEARCHIDresultsPart8-8.tsv', 'w', 'utf-8-sig')  # abre arquivo de output
        file_list = [out_file1, out_file2, out_file3, out_file4, out_file5, out_file6, out_file7, out_file8]
        for out_file in file_list:
            out_file.write('ResearcherID\tTotal in Pub. List\tWith Citation Data\tSum of Times Cited\t'
                           'Average Citations/Article\tH-index\n')  # escreve headers
            out_file.close()
        control1, control2, control3, control4, control5, control6, control7, control8 = Control(), Control(), \
                                                                                         Control(), Control(), \
                                                                                         Control(), Control(), \
                                                                                         Control(), Control()
        control_list = [control1, control2, control3, control4, control5, control6, control7, control8]
        print 'Begin of extraction,', len(link_list) - 1, 'items to go'

        octan = len(link_list) // 8
        pool.map(parallel_scraping, [(link_list[:octan - 1], '../dados/csv/RESEARCHIDresultsPart1-8.tsv', control1),
                                     (link_list[octan:2 * octan - 1], '../dados/csv/RESEARCHIDresultsPart2-8.tsv',
                                      control2),
                                     (link_list[2 * octan:3 * octan - 1], '../dados/csv/RESEARCHIDresultsPart3-8.tsv',
                                      control3),
                                     (link_list[3 * octan:4 * octan - 1], '../dados/csv/RESEARCHIDresultsPart4-8.tsv',
                                      control4),
                                     (link_list[4 * octan:5 * octan - 1], '../dados/csv/RESEARCHIDresultsPart5-8.tsv',
                                      control5),
                                     (link_list[5 * octan:6 * octan - 1], '../dados/csv/RESEARCHIDresultsPart6-8.tsv',
                                      control6),
                                     (link_list[6 * octan:7 * octan - 1], '../dados/csv/RESEARCHIDresultsPart7-8.tsv',
                                      control7),
                                     (link_list[7 * octan:], '../dados/csv/RESEARCHIDresultsPart8-8.tsv', control8)])
    total_H_index = 0
    total_existent_H_index = 0
    total_cited = 0
    total_articles = 0
    elements_counter = 0
    for x in control_list:
        total_H_index += x.h_index_accumulator
        total_existent_H_index += x.existent_h_index_counter
        total_cited += x.with_citation_accumulator
        total_articles += x.article_accumulator
        elements_counter += x.counter

    log.write('Total count: %s\n' % str(elements_counter))
    log.write('Average H-Index: %s\n' % str(total_H_index / total_existent_H_index))
    log.write('Total articles with citation data: %s\n' % str(total_cited))
    log.write('Total articles: %s\n' % str(total_articles))
    log.close()
    print 'Extraction finished:', elements_counter, 'elements listed'
