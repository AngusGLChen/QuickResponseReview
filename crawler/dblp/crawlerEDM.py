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
from google_drive_downloader import GoogleDriveDownloader as gdd


def click_action(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)


def crawl_articles(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
        
    links = {2008:'https://dblp.org/db/conf/edm/edm2008.html',
             2009:'https://dblp.org/db/conf/edm/edm2009.html',
             2010:'https://dblp.org/db/conf/edm/edm2010.html',
             2011:'https://dblp.org/db/conf/edm/edm2011.html',
             2012:'https://dblp.org/db/conf/edm/edm2012.html',
             2013:'https://dblp.org/db/conf/edm/edm2013.html',
             2014:'https://dblp.org/db/conf/edm/edm2014.html',
             2015:'https://dblp.org/db/conf/edm/edm2015.html',
             2016:'https://dblp.org/db/conf/edm/edm2016.html',
             2017:'https://dblp.org/db/conf/edm/edm2017.html',
             2018:'https://dblp.org/db/conf/edm/edm2018.html'
            }  
        
    for year in links.keys():
        
        if year != 2008:
            continue
        
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
        
        if year not in [2009, 2010, 2014]:
            headers = driver.find_elements_by_xpath("//header/h2")
            article_blocks = driver.find_elements_by_xpath("//header[h2]/following-sibling::ul")
            
            for header,article_block in zip(headers,article_blocks):
                category = header.text
                    
                articles = article_block.find_elements_by_xpath(".//li[@class='entry inproceedings']")
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
                    
                    article_links.append({'title':title,                                              
                                          'authors':authors,
                                          'pages':pages,
                                          'pdf_link':pdf_link,
                                          'category':category
                                          })
                    
                    # Crawl pdf files
                    if not os.path.exists(data_path + str(year) + '/' + pdf_link.split('/')[-1]) and pdf_link != None:
                        response = requests.get(pdf_link)
                        outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                        outFile.write(response.content)
                        outFile.close()                    
                        time.sleep(random.randint(3,5))
                        
            outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
            outFile.write(json.dumps(article_links))
            outFile.close()
        
        elif year in [2014]:
            
            headers = driver.find_elements_by_xpath("//header/h3")
            article_blocks = driver.find_elements_by_xpath("//header[h3]/following-sibling::ul")
            
            for header,article_block in zip(headers,article_blocks):
                category = header.text
                    
                articles = article_block.find_elements_by_xpath(".//li[@class='entry inproceedings']")
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
                    
                    article_links.append({'title':title,                                              
                                          'authors':authors,
                                          'pages':pages,
                                          'pdf_link':pdf_link,
                                          'category':category
                                          })
                    
                    # Crawl pdf files
                    if not os.path.exists(data_path + str(year) + '/' + pdf_link.split('/')[-1]) and pdf_link != None:
                        if "shortpapers" in pdf_link:  
                            pdf_link = pdf_link.replace("shortpapers", "short%20papers")
                        if "longpapers" in pdf_link:  
                            pdf_link = pdf_link.replace("longpapers", "long%20papers") 
                        
                        response = requests.get(pdf_link)
                        outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                        outFile.write(response.content)
                        outFile.close()                    
                        time.sleep(random.randint(3,5))
                        
            outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
            outFile.write(json.dumps(article_links))
            outFile.close()
        
        else:
            
            category = None
                                
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
                pages = article.find_element_by_xpath(".//span[@itemprop='pagination']").text                                       
            
                article_links.append({'title':title,                                              
                                      'authors':authors,
                                      'pages':pages,
                                      'pdf_link':pdf_link,
                                      'category':category
                                      })
                
                print(title)
            
                # Crawl pdf files
                if not os.path.exists(data_path + str(year) + '/' + pdf_link.split('/')[-1]) and pdf_link != None:
                    response = requests.get(pdf_link)
                    outFile = open(data_path + str(year) + '/' + pdf_link.split('/')[-1], 'wb')
                    outFile.write(response.content)
                    outFile.close()                    
                    time.sleep(random.randint(3,5))
                        
            outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
            outFile.write(json.dumps(article_links))
            outFile.close()
                    
    driver.close()
    
    
def crawl_articles_2019(data_path):
    
    download_dir = '/Users/gche0022/Downloads/Projects/QuickResponseReview/data/EDM/2019/'
    chromeOptions = webdriver.ChromeOptions()
    profile = {"plugins.always_open_pdf_externally": True,
               "directory_upgrade": True, 
               "download.default_directory": download_dir,
               "download.prompt_for_download": False,
               "download.directory_upgrade": True}
    chromeOptions.add_experimental_option("prefs", profile)
            
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
        
    links = {2019:'http://educationaldatamining.org/edm2019/proceedings/'}  
        
    for year in links.keys():
                
        if not os.path.exists(data_path + str(year)):
            os.mkdir(data_path + str(year))     
                
        # Visit proceeding page
        link = links[year]
        driver.get(link)
        time.sleep(5)
        
        article_links = []
        
        print(link)        
        article_blocks = driver.find_elements_by_xpath("//table")
        
        for article_block in article_blocks:
            
            # Check whether a table contains articles
            try:
                category = article_block.find_element_by_xpath(".//h4").text
            except:
                continue
            
            if category not in ['FULL PAPERS', 'SHORT PAPERS']:
                continue
            
            print(category)
                
            articles = article_block.find_elements_by_xpath(".//tr/td[2]")
            for article in articles:                
                try:
                    # Link to pdf                
                    pdf_link = article.find_element_by_xpath("./a").get_attribute('href').replace('?usp=sharing', '')
                    
                    # Title
                    title = article.find_element_by_xpath("./a").text   
                                                  
                    # Authors
                    authors = (article.text).replace(title, "").strip()
                    
                    article_links.append({'title':title,                                              
                                          'authors':authors,
                                          'pdf_link':pdf_link,
                                          'category':category
                                          })
                    
                    print("%s\t%s\t%s\t%s" % (category, title, authors, pdf_link))
                    
                    # Crawl pdf files
                    googleFileID = pdf_link.split('/')[-2]  
                    if not os.path.exists(data_path + str(year) + '/' + googleFileID):                        
                        gdd.download_file_from_google_drive(file_id=googleFileID,
                                                            dest_path= data_path + str(year) + '/' + googleFileID + ".pdf",
                                                            unzip=True)
                        
                        
                except Exception as e:
                    print(e)
                
                
        outFile = open(data_path + str(year) + '/article_links', 'w', encoding='utf-8')
        outFile.write(json.dumps(article_links))
        outFile.close()
        
        
                    
    driver.close()



def main():
    
    conference_name = 'EDM'
    data_path = '../../data/' + conference_name + '/'
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        
    crawl_articles(data_path)
    
    # crawl_articles_2019(data_path)   
   
if __name__ == "__main__":
    main()
