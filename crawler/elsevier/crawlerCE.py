from bs4 import BeautifulSoup
import requests

import os
import json
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from functions import click_action
import xml.etree.ElementTree


    
def crawl_article_links(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    starting_link = 'https://www.sciencedirect.com/journal/computers-and-education/vol/34/issue/1'
    starting_link = 'https://www.sciencedirect.com/journal/computers-and-education/vol/81/suppl/C'
    driver.get(starting_link)
    time.sleep(5)
    
    while True:
        abstract_buttons = driver.find_elements_by_xpath("//button[@class='button-link button-link-primary u-font-sans text-s']")
        for button in abstract_buttons:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
                
        volume_issue = driver.find_element_by_xpath("//*[contains(@class, 'js-vol-issue')]").text
        timestamp = driver.find_element_by_xpath("//h3[@class='js-issue-status text-s']").text
        timestamp = timestamp[timestamp.find("(")+1:timestamp.find(")")].replace('1 ', '')
        
        if os.path.exists(data_path + '/article_links/' + timestamp):
            click_action(driver, "(//a[@class='anchor text-m u-padding-s-ver u-display-block'])[position()=2]")
            continue
        
        if 'January 2019' in timestamp:
            break
        
        data_map = {'url':driver.current_url,
                    'volume_issue':volume_issue,
                    'timestamp':timestamp,
                    'articles':[]}
        
        article_blocks = driver.find_elements_by_xpath(".//dl[@class='js-article article-content']")
        for block in article_blocks:
            article_title = block.find_element_by_xpath(".//span[@class='js-article-title']").text
            
            try:
                article_type = block.find_element_by_xpath(".//span[@class='js-article-subtype']").text
            except:
                article_type = ''
                print("Article type error.\t%s\t%s" % (timestamp, article_title))
                
            try:
                abstract = block.find_element_by_xpath(".//div[@class='js-abstract-body-text branded']/div/p").text
            except:
                abstract = ''
                print("Abstract error.    \t%s\t%s" % (timestamp, article_title))
            
            try:
                authors = block.find_element_by_xpath(".//div[@class='text-s u-clr-grey8 js-article__item__authors']").text
            except:
                authors = ''
                print("Authors error.      \t%s\t%s" % (timestamp, article_title))
            
            link = block.find_element_by_xpath(".//a[@class='anchor article-content-title u-margin-xs-top u-margin-s-bottom']").get_attribute('href')
            
            data_map['articles'].append({'article_type':article_type,
                                         'article_title':article_title,
                                         'authors':authors,
                                         'abstract':abstract,
                                         'link':link
                                         })
            time.sleep(1)
            
        outFile = open(data_path + '/article_links/' + timestamp, 'w', encoding='utf-8')
        outFile.write(json.dumps(data_map))
        outFile.close()
        
        # Click next page   
        click_action(driver, "(//a[@class='anchor text-m u-padding-s-ver u-display-block'])[position()=2]")

    driver.close()


def crawl_article_pdfUrls(data_path):
    # Create folder
    if not os.path.exists(data_path + '/xml_files/'):
        os.mkdir(data_path + '/xml_files/')
    
    article_type_set = set()
    article_links = []
    
    for file in os.listdir(data_path + '/article_links/'):
        if file != '.DS_Store':
            voloum_issue_object = json.loads(open(data_path + '/article_links/' + file, 'r', encoding='utf-8').read())
            for article in voloum_issue_object['articles']:
                article_type = article['article_type']
                link = article['link']
                
                article_type_set.add(article_type)
                
                if article_type == 'Research article':
                    article_links.append(link)
    
    # print(article_type_set)
    print('# articles:\t%d' % len(article_links))
    
    # Crawled articles
    crawled_articles = set(os.listdir(data_path + '/xml_files/'))
    print('# crawled articles:\t%d' % len(crawled_articles))
    
    apikey = "f0707eb3232f3a31367fbf547384dd24"
    
    for link in article_links:
        pii = link.replace('https://www.sciencedirect.com/science/article/pii/', '') 
        if pii in crawled_articles:
            continue
        
        pii_link = "https://api.elsevier.com/content/article/pii/" + pii + "?apiKey=" + apikey
        xmlPage = requests.get(pii_link)
        
        outFile = open(data_path + '/xml_files/' + pii, 'wb')
        outFile.write(xmlPage.content)
        outFile.close()
        

def check_xml_files(data_path):
    xml_files = os.listdir(data_path + '/xml_files/')
    for xml_file in xml_files:
        if xml_file != '.DS_Store':
            try:
                xml.etree.ElementTree.parse(data_path + '/xml_files/' + xml_file)
            except Exception as e:
                print(e)
                os.remove(data_path + '/xml_files/' + xml_file)
        
        
        
    
def main():
    
    journal_name = 'Computers & Education'
    data_path = '../../data/' + journal_name
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        
    # 1. Crawl links pointing to each article
    # crawl_article_links(data_path)
    
    # 2. Crawl article pdfUrls
    crawl_article_pdfUrls(data_path)
    # check_xml_files(data_path)
     
   
if __name__ == "__main__":
    main()

