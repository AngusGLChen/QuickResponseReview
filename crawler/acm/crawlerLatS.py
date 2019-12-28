'''
Created on 22 May 2019

@author: gche0022
'''


import os
import glob
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# from functions import click_action


def click_action(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)


def crawl_article_links(data_path):
    driver = webdriver.Chrome(executable_path='../../chromedriver')
    driver.maximize_window()
    
    links = {2014:'https://dl.acm.org/citation.cfm?id=2556325&picked=prox',
             2015:'https://dl.acm.org/citation.cfm?id=2724660&picked=prox',
             2016:'https://dl.acm.org/citation.cfm?id=2876034&picked=prox',
             2017:'https://dl.acm.org/citation.cfm?id=3051457&picked=prox',
             2018:'https://dl.acm.org/citation.cfm?id=3231644&picked=prox'
             }
    
    for year in links.keys():
        
        if not os.path.exists(data_path + str(year)):
            os.mkdir(data_path + str(year))
            
        if os.path.exists(data_path + str(year) + '/article_links'):
            continue
        
        # Visit proceeding page
        link = links[year]        
        driver.get(link)
        time.sleep(5)
        
        # Click 'Table of Contents' tab
        click_action(driver, "//button[@id='tab-1022-btnEl']")
        time.sleep(20)
        
        # expand_buttons = driver.find_elements_by_xpath("//a[contains(text(), 'expand')]")
        # for button in expand_buttons:
        #     driver.execute_script("arguments[0].click();", button)
        #     time.sleep(3)
        
        article_links = []
               
        articles = driver.find_elements_by_xpath("//*[contains(@href, 'citation.cfm?id=') and not(contains(@href, '&picked=prox'))]")
        for article in articles:
            title = article.text
            link = article.get_attribute('href')
            article_links.append([title,link])
                   
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
            
            for [title,link] in article_links:
                if link not in article_metadata_map.keys():
                    driver.get(link)
                    time.sleep(5)
                    
                    try:
                        # Authors & Institutions
                        authors = driver.find_elements_by_xpath("//a[@title='Author Profile Page']")
                        instituions = driver.find_elements_by_xpath("//a[@title='Institutional Profile Page']")
                        
                        author_instituion_array = []
                        for author,instituion in zip(authors, instituions):
                            author_name = author.text
                            # author_acm_link = author.get_attribute('href')
                            instituion_name = instituion.text
                            # instituion_acm_link = instituion.get_attribute('href')
                            
                            author_instituion_array.append({'author_name':author_name,                                                            
                                                            'instituion_name':instituion_name})
                    
                        # Abstract
                        abstract = driver.find_element_by_xpath("//div[@id='abstract-body']").text
                        
                        # Bib
                        click_action(driver, "//a[contains(text(), 'BibTeX')]")
                        time.sleep(random.randint(3,5))
                        bibtex = driver.find_element_by_xpath("//pre").text
                        
                        article_metadata_map[link] = {'author_instituion_array':author_instituion_array,
                                                      'abstract':abstract,
                                                      'bibtex':bibtex}
                    
                    except Exception as e:
                        
                        print(e)
                        print(link)
                        print('')
                    
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
            download_dir = '/Users/gche0022/Downloads/Projects/QuickResponseReview/data/LatS/' + year + '/'
            chromeOptions = webdriver.ChromeOptions()
            profile = {"plugins.always_open_pdf_externally": True,
                       "directory_upgrade": True, 
                       "download.default_directory": download_dir,
                       "download.prompt_for_download": False,
                       "download.directory_upgrade": True}
            chromeOptions.add_experimental_option("prefs", profile)
                        
            driver = webdriver.Chrome(executable_path='../../chromedriver', options=chromeOptions)
            driver.maximize_window()
            
            article_links = json.loads(open(data_path + year + '/article_links', 'r').read())
            print("In %s, there are %d articles." % (year, len(article_links)))
                           
            for [title,link] in article_links:
                uid = link.replace('https://dl.acm.org/citation.cfm?id=', '')
                if not os.path.exists(download_dir + uid + '.pdf'):
                    driver.get(link)
                    time.sleep(5)
                        
                    try:
                        click_action(driver, "//a[@name='FullTextPDF']")
                        time.sleep(random.randint(20, 30))
                        
                        # Rename the downloaded file
                        files = glob.glob(download_dir + '*')
                        downloaded_file = max(files, key=os.path.getctime)                    
                        os.rename(downloaded_file, download_dir + uid + '.pdf')
                                            
                    except Exception as e:                         
                        print(e)
                        print(link)
                        print('')
                    
            driver.close()
                










def main():
    
    conference_name = 'LatS'
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
