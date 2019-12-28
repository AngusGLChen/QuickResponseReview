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


def click_action(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)


def crawl_article_links(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
        
    links = {2011:['https://link.springer.com/book/10.1007/978-3-642-21869-9?page=1',
                   'https://link.springer.com/book/10.1007/978-3-642-21869-9?page=2',
                   'https://link.springer.com/book/10.1007/978-3-642-21869-9?page=3',
                   ],
             2013:['https://link.springer.com/book/10.1007/978-3-642-39112-5?page=1',
                   'https://link.springer.com/book/10.1007/978-3-642-39112-5?page=2',
                   'https://link.springer.com/book/10.1007/978-3-642-39112-5?page=3',
                   'https://link.springer.com/book/10.1007/978-3-642-39112-5?page=4'],
             2015:['https://link.springer.com/book/10.1007/978-3-319-19773-9?page=1',
                   'https://link.springer.com/book/10.1007/978-3-319-19773-9?page=2',
                   'https://link.springer.com/book/10.1007/978-3-319-19773-9?page=3'],
             2017:['https://link.springer.com/book/10.1007/978-3-319-61425-0?page=1',
                   'https://link.springer.com/book/10.1007/978-3-319-61425-0?page=2'],
             2018:['https://link.springer.com/book/10.1007/978-3-319-93843-1?page=1',
                   'https://link.springer.com/book/10.1007/978-3-319-93846-2?page=1',
                   'https://link.springer.com/book/10.1007/978-3-319-93846-2?page=2',
                   'https://link.springer.com/book/10.1007/978-3-319-93846-2?page=3']    
            }
    
    for year in links.keys():
        
        if not os.path.exists(data_path + str(year)):
            os.mkdir(data_path + str(year))
            
        if os.path.exists(data_path + str(year) + '/article_links'):
            continue
        
        article_links = []
                
        # Visit proceeding page
        for link in links[year]:
            driver.get(link)
            time.sleep(5)
            
            article_blocks = driver.find_elements_by_xpath("//li[@class='part-item']")
            for article_block in article_blocks:
                category = article_block.find_element_by_xpath(".//h3").text
                 
                articles = article_block.find_elements_by_xpath(".//li[@class='chapter-item content-type-list__item']")
                for article in articles:
                    title = article.find_element_by_xpath(".//a[@class='content-type-list__link u-interface-link']")
                    article_springer_link = title.get_attribute('href')
                    title = title.text                                                
                    authors = article.find_element_by_xpath(".//div[@data-test='author-text']").text                        
                    pages = article.find_element_by_xpath(".//span[@data-test='page-range']").text                        
                    pdf_link = article.find_element_by_xpath(".//a[@data-track-action='Pdf download']").get_attribute('href')
                    
                    if title not in ['Front Matter', 'Back Matter']:
                        article_links.append({'title':title,
                                              'article_springer_link':article_springer_link,
                                              'authors':authors,
                                              'pages':pages,
                                              'pdf_link':pdf_link,
                                              'category':category
                                              })                        
                        
            outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
            outFile.write(json.dumps(article_links))
            outFile.close()
        
    driver.close()



def crawl_article_metadata(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    # Iterate over years
    for year in os.listdir(data_path):
        if year != '.DS_Store':
            
            # Metadata repository
            if not os.path.exists(data_path + year + '/article_metadata_map'):
                article_metadata_map = dict()
            else:
                article_metadata_map = json.loads(open(data_path + year + '/article_metadata_map', 'r').read())
            
            article_links = json.loads(open(data_path + year + '/article_links', 'r').read())
            
            print("In %s, there are %d articles." % (year, len(article_links)))
            
            if len(article_links) == len(article_metadata_map.keys()):
                continue
            
            for article in article_links:
                link = article['article_springer_link']               
                
                if link not in article_metadata_map.keys():
                    driver.get(link)
                    time.sleep(5)
                                        
                    # Authors & Institutions
                    click_action(driver, "//a[@data-track-action='Authors and affiliations tab']")
                    time.sleep(2)
                    
                    authors = driver.find_elements_by_xpath("//span[@class='authors-affiliations__name']")
                    authorsArray = []
                    for author in authors:
                        authorsArray.append(author.text)
                                        
                    authorsIndexes = driver.find_elements_by_xpath("//ul[@data-role='AuthorsIndexes']")
                    authorsIndexesArray = []
                    for i in range(len(authorsArray)):
                        authorsIndexesArray.append([])
                    for i in range(len(authorsIndexes)):
                        indexes = authorsIndexes[i].find_elements_by_xpath(".//li")
                        for index in indexes:
                            authorsIndexesArray[i].append(index.text)                        
                    
                    instituions_map = {}
                    instituions = driver.find_elements_by_xpath("//li[@class='affiliation']")
                    for instituion in instituions:
                        affiliation__count = instituion.find_element_by_xpath(".//span[@class='affiliation__count']").text
                        
                        # affiliation__name = instituion.find_element_by_xpath(".//span[@class='affiliation__name']").text
                        try:
                            affiliation__name = instituion.find_element_by_xpath(".//span[@class='affiliation__name']").text
                        except Exception as e:
                            affiliation__name = None
                        
                        try:
                            affiliation__city = instituion.find_element_by_xpath(".//span[@class='affiliation__city']").text
                        except Exception as e:
                            affiliation__city = None
                            # print(e)
                        
                        try:
                            affiliation__country = instituion.find_element_by_xpath(".//span[@class='affiliation__country']").text
                        except Exception as e:
                            affiliation__country = None
                            # print(e)
                            
                        instituions_map[affiliation__count] = {'affiliation__name':affiliation__name,
                                                               'affiliation__city':affiliation__city,
                                                               'affiliation__country':affiliation__country}
                        
                    # Abstract
                    abstract = driver.find_element_by_xpath("//section[@class='Abstract']/p").text
                                   
                    # Keywords
                    keywords_spans = driver.find_elements_by_xpath("//span[@class='Keyword']")
                    keywords = []
                    for keywords_span in keywords_spans:
                        keywords.append(keywords_span.text)
                                            
                    article_metadata_map[link] = {'authorsArray':authorsArray,
                                                  'authorsIndexesArray':authorsIndexesArray,
                                                  'instituions_map':instituions_map,
                                                  'abstract':abstract,
                                                  'keywords':keywords}
                    
                    
                     
                if len(article_metadata_map.keys()) % 10 == 0:
                    print('%d articles have been crawled.' % len(article_metadata_map.keys()))
                    outFile = open(data_path + year + '/article_metadata_map', 'w', encoding='utf-8')
                    outFile.write(json.dumps(article_metadata_map))
                    outFile.close()
                
                # Testing
                # if len(article_metadata_map.keys()) > 5:
                #     break
                
                
            outFile = open(data_path + year + '/article_metadata_map', 'w', encoding='utf-8')
            outFile.write(json.dumps(article_metadata_map))
            outFile.close()

    driver.close()
                

                           
def crawl_article_pdfUrls(data_path):
    # Iterate over years
    for year in os.listdir(data_path):
        if year != '.DS_Store':
            # Initialize selenium
            download_dir = data_path + year + '/'            
            article_links = json.loads(open(data_path + year + '/article_links', 'r').read())
            print("In %s, there are %d articles." % (year, len(article_links)))
                           
            for article in article_links:
                link = article['article_springer_link']
                uid = link.split("/")[-1]
                
                if not os.path.exists(download_dir + uid + '.pdf'):  
                    try:                        
                        response = requests.get(article['pdf_link'])
                        outFile = open(download_dir + uid + '.pdf', 'wb')
                        outFile.write(response.content)
                        outFile.close()  
                    except Exception as e:                         
                        print(e)
                        print(link)
                        print('')
                        
                    time.sleep(random.randint(10,20))
               


def main():
    
    conference_name = 'AIED'
    data_path = '../../data/' + conference_name + '/'
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        
    # 1. Crawl links pointing to each article
    # crawl_article_links(data_path)
    
    # 2. Crawl metadata of each article
    # crawl_article_metadata(data_path)
    
    # 3. Crawl article pdfUrls
    crawl_article_pdfUrls(data_path)
         
   
if __name__ == "__main__":
    main()
