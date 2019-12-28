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
    
    links = {2015:'https://dblp.org/db/conf/cscl/cscl2015.html',
             2017:'https://dblp.org/db/conf/cscl/cscl2017.html'
             }
    
    for year in links.keys():
        
        if not os.path.exists(data_path + str(year)):
            os.mkdir(data_path + str(year))     
                
        # Visit proceeding page
        link = links[year]
        driver.get(link)
        time.sleep(5)
        
        article_links = []
        print(link)
        
        if os.path.exists(data_path + str(year) + '/article_links'):
            continue
                            
        articles = driver.find_elements_by_xpath("//li[@class='entry inproceedings']")
        for article in articles:            
            # Link to pdf
            try:
                isls_link = article.find_element_by_xpath(".//nav[@class='publ']/ul/li/div/a").get_attribute('href')
            except Exception as e:
                print(e)
                isls_link = None
                            
            # Authors
            authors = []
            author_spans = article.find_elements_by_xpath(".//span[@itemprop='author']/a/span")
            for author_span in author_spans:
                authors.append(author_span.text)                    
        
            # Title
            title = article.find_element_by_xpath(".//span[@class='title']").text               
            
            article_links.append({'title':title,                                              
                                  'authors':authors,
                                  'isls_link':isls_link
                                  })
            
        outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
        outFile.write(json.dumps(article_links))
        outFile.close()
        
    driver.close()


                         
def crawl_article_pdfUrls(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    # Iterate over years
    for year in ['2015', '2017']:        
        article_links = json.loads(open(data_path + year + '/article_links', 'r').read())
        print("In %s, there are %d articles." % (year, len(article_links)))
                       
        for article_link in article_links:
            driver.get(article_link['isls_link'])
            time.sleep(random.randint(3,5))
            
            pdf_link = driver.find_element_by_xpath("//a[contains(text(), 'View/Open')]").get_attribute('href')  
            file_name = pdf_link.split('/')[-1]
            
            if not os.path.exists(data_path + year + '/' + file_name):                
                response = requests.get(pdf_link)
                outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                outFile.write(response.content)
                outFile.close()                    
                time.sleep(random.randint(5,10))
                    
    driver.close()
        

def main():
    
    conference_name = 'CSCL'
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
