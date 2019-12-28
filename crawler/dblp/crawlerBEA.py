'''
Created on 22 May 2019

@author: gche0022
'''

import os
import json
import time
import random
import requests
from selenium import webdriver


def crawl_articles(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
        
    links = {2009:'https://dblp.org/db/conf/bea/bea2009.html',
             2011:'https://dblp.org/db/conf/bea/bea2011.html',
             2012:'https://dblp.org/db/conf/bea/bea2012.html',
             2013:'https://dblp.org/db/conf/bea/bea2013.html',
             2014:'https://dblp.org/db/conf/bea/bea2014.html',
             2015:'https://dblp.org/db/conf/bea/bea2015.html',
             2016:'https://dblp.org/db/conf/bea/bea2016.html',
             2017:'https://dblp.org/db/conf/bea/bea2017.html',
             2018:'https://dblp.org/db/conf/bea/bea2018.html',
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
                pdf_link = article.find_element_by_xpath(".//nav[@class='publ']/ul/li/div/a").get_attribute('href')
            except Exception as e:
                print(e)
                pdf_link = None
                            
            # Authors
            authors = []
            author_spans = article.find_elements_by_xpath(".//span[@itemprop='author']/a/span")
            for author_span in author_spans:
                authors.append(author_span.text)                    
        
            # Title
            title = article.find_element_by_xpath(".//span[@class='title']").text   
                                
            # Pages
            try:
                pages = article.find_element_by_xpath(".//span[@itemprop='pagination']").text                                       
            except:
                pages = None
                
            if title != 'Front Matter.':
                article_links.append({'title':title,                                              
                                      'authors':authors,
                                      'pages':pages,
                                      'pdf_link':pdf_link
                                      })
            
                # Crawl pdf files
                if not os.path.exists(data_path + str(year) + '/' + pdf_link.split('/')[-1]) and pdf_link != None:
                    # print(pdf_link)
                    
                    if year in [2009, 2011, 2017, 2018]:
                        pdf_link = "https://www.aclweb.org/anthology/" + pdf_link.split('/')[-2] + '.pdf'
                    
                    response = requests.get(pdf_link)
                    outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                    outFile.write(response.content)
                    outFile.close()                    
                    time.sleep(random.randint(3,5))
                    
        outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
        outFile.write(json.dumps(article_links))
        outFile.close()
        
    driver.close()




def main():
    
    conference_name = 'BEA'
    data_path = '../../data/' + conference_name + '/'
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        
    crawl_articles(data_path)
         
   
if __name__ == "__main__":
    main()
