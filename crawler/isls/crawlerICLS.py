'''
Created on 22 May 2019

@author: gche0022
'''


import os
import glob
import json
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


def crawl_article_links(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    links = {2014:{'link':'https://repository.isls.org/handle/1/920', 'num':308},
             2016:{'link':'https://repository.isls.org/handle/1/98', 'num':171},
             2018:{'link':'https://repository.isls.org/handle/1/473', 'num':446}
             }
    
    for year in links.keys():
        
        if not os.path.exists(data_path + str(year)):
            os.mkdir(data_path + str(year))
            
        if os.path.exists(data_path + str(year) + '/article_links'):
            continue
                
        # Visit proceeding page
        num = links[year]['num']
        article_links = set()
        for i in range(0, num, 20):
            link = links[year]['link'] + '?offset=' + str(i)
            driver.get(link)
            time.sleep(5)
            
            print(link)

            articles = driver.find_elements_by_xpath("//a[contains(@href, '/handle/')]")
            for article in articles:            
                # Link to pdf
                isls_link = article.get_attribute('href')
                article_links.add(isls_link)
        
        outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
        outFile.write(json.dumps(list(article_links)))
        outFile.close()
        
    driver.close()


                         
def crawl_article_pdfUrls(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    # Iterate over years
    for year in ['2014', '2016', '2018']:
        
        # Metadata repository
        if not os.path.exists(data_path + year + '/article_metadata_map'):
            article_metadata_map = dict()
        else:
            article_metadata_map = json.loads(open(data_path + year + '/article_metadata_map', 'r').read())
             
        article_links = json.loads(open(data_path + year + '/article_links', 'r').read())
        print("In %s, there are %d articles." % (year, len(article_links)))
                       
        for isls_link in article_links:
            if isls_link in article_metadata_map.keys():
                continue
            
            driver.get(isls_link)
            time.sleep(2)          
            
            mark = False
            try:
                driver.find_element_by_xpath("//td[@class='metadataFieldLabel dc_title']")
                driver.find_element_by_xpath("//td[@class='metadataFieldLabel dc_contributor']")
                driver.find_element_by_xpath("//td[@class='metadataFieldLabel dc_identifier_citation']")
                mark = True
            except:
                continue
            
            if mark:
                
                title = driver.find_element_by_xpath("//td[@class='metadataFieldValue dc_title']").text
                
                author_array = []
                authors = driver.find_elements_by_xpath("//td[@class='metadataFieldValue dc_contributor']/a")
                for author in authors:
                    author_array.append(author.text)
                
                try: 
                    abstract = driver.find_element_by_xpath("//td[@class='metadataFieldValue dc_description_abstract']").text
                except:
                    abstract = None
                
                article_metadata_map[isls_link] = {'author_iarray':author_array,
                                                   'abstract':abstract,
                                                   'title':title}
            
                pdf_link = driver.find_element_by_xpath("//a[contains(text(), 'View/Open')]").get_attribute('href')  
                file_name = pdf_link.split('/')[-1]
                
                if not os.path.exists(data_path + year + '/' + file_name):                
                    response = requests.get(pdf_link)
                    outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                    outFile.write(response.content)
                    outFile.close()                    
                    time.sleep(random.randint(3,5))
                    
            if len(article_metadata_map.keys()) % 10 == 0:
                print('%d articles have been crawled.' % len(article_metadata_map.keys()))
                outFile = open(data_path + year + '/article_metadata_map', 'w', encoding='utf-8')
                outFile.write(json.dumps(article_metadata_map))
                outFile.close()
                
        outFile = open(data_path + year + '/article_metadata_map', 'w', encoding='utf-8')
        outFile.write(json.dumps(article_metadata_map))
        outFile.close()
                    
    driver.close()
        


def main():
    
    conference_name = 'ICLS'
    data_path = '../../data/' + conference_name + '/'
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        
    # 1. Crawl links pointing to each article
    # crawl_article_links(data_path)
        
    # 2. Crawl article pdfUrls
    crawl_article_pdfUrls(data_path)
    
     
   
if __name__ == "__main__":
    main()
