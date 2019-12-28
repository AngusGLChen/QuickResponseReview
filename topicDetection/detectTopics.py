'''
Created on 14 Jun 2019

@author: gche0022
'''

import os
import re
import json
import string
import demjson
import operator
import bibtexparser
from PyPDF2 import PdfFileReader
from xml.etree import ElementTree
from _collections import defaultdict
from collections import OrderedDict
from copy import deepcopy

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import csv

import numpy
import matplotlib.pyplot as plt


def analyze_page_types(data_path):
    
    conferences = ['LAK', 'EDM']
    
    for conference_name in conferences:
        conference_path = data_path + conference_name + '/'
        
        ########################################################################
        if conference_name == 'LAK':
            for year in range(2011,2020):
                # print('--------------- %s\t%d ---------------' % (conference_name, year))
                # Metadata repository
                article_metadata_map = json.loads(open(conference_path + str(year) + '/article_metadata_map', 'r').read())
                pageNum_map = defaultdict(int)
                num_articles = 0
                
                for article in article_metadata_map.keys():
                             
                    bibtexText = article_metadata_map[article]['bibtex']
                    bib_data = bibtexparser.loads(bibtexText)
                    # if 'pages' in bib_data.entries[0].keys():
                    numpages = int(bib_data.entries[0]['numpages'])
                    pageNum_map[numpages] += 1
                    
                    num_articles += 1
                    
                    # if numpages <= 3:
                    #     print(bib_data.entries[0]['title'])
                    
                print("In %s %d, # papers:\t%d" % (conference_name, year, num_articles))
                # sorted_pageNum_map = sorted(pageNum_map.items(), key=lambda x: x[0], reverse=True)
                # for sortedTuple in sorted_pageNum_map:
                #     print("%d pages => %d papers" % (sortedTuple[0], sortedTuple[1]))
                
                # print('')
        
        if conference_name == 'EDM':
            for year in range(2008,2019):
                # print('--------------- %s\t%d ---------------' % (conference_name, year))
                pageNum_map = defaultdict(int)
                num_articles = 0
                
                for article in os.listdir(conference_path + str(year)):
                    if article.endswith('.pdf'):
                        num_articles += 1
                        numpages = PdfFileReader(open(conference_path + str(year) + '/' + article, 'rb')).getNumPages()
                        pageNum_map[numpages] += 1
                    
                    # if numpages == 1:
                    #     print(article)
                    
                print("In %s %d, # papers:\t%d" % (conference_name, year, num_articles))
                # sorted_pageNum_map = sorted(pageNum_map.items(), key=lambda x: x[0], reverse=True)
                # for sortedTuple in sorted_pageNum_map:
                #     print("%d pages => %d papers" % (sortedTuple[0], sortedTuple[1]))
                 
                # print('')'
                
                
def preprocess_text_data(stop_words, text):
    # print(text)
    # Lower case
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuations
    text = text.translate(str.maketrans('','',string.punctuation))  
    # Remove whitespace & linebreaks  
    text = text.strip() 
    text = text.replace('\n', ' ').replace('\r', '')       
    # Remove stopwords
    tokens = word_tokenize(text)
    tokens = [i for i in tokens if not i in stop_words]
    # Stemming
    # stemmer= PorterStemmer()
    # tokens = [stemmer.stem(token) for token in tokens] 
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]                
    # print(tokens)
    # print('')        
    return tokens
                
                
def generate_data_hlta(data_path):
    
    data_array = []    
    conferences = ['LAK','EDM']
    
    # The list of considered papers
    selected_publication_map = json.loads(open(data_path + '/selected_papers_' + "_".join(conferences) + '.txt', 'r', encoding='utf-8').read())
    
    # Supplemented abstracts
    supplemented_abstract = dict()
    infile = open(data_path + '/Data Crawling - Supplemented_Abstract.csv', 'r', encoding='utf-8')
    reader = csv.reader(infile)
    for row in reader:
        conference = row[0]
        year = row[1]
        paperID = row[2]
        abstract = row[3]
        supplemented_abstract[paperID] = abstract
    
    hlta_metadata_map = dict()
    index = None
    
    for conference_name in conferences:
        conference_path = data_path + conference_name + '/'
        
        ########################################################################
        if conference_name == 'LAK':
            for year in range(2011,2020):                
                # Metadata repository
                article_metadata_map = json.loads(open(conference_path + str(year) + '/article_metadata_map', 'r').read())
                article_metadata_mag_map = json.loads(open(conference_path + str(year) + '/article_metadata_mag_map', 'r').read())
                                
                for article in article_metadata_map.keys():
                    
                    if article in selected_publication_map[conference_name][str(year)]:                        
                                     
                        bibtexText = article_metadata_map[article]['bibtex']
                        bib_data = bibtexparser.loads(bibtexText)
                        
                        title = bib_data.entries[0]['title']
                        abstract = article_metadata_map[article]['abstract']
                        
                        data_array.append(title + ' ' + abstract)
                        
                        # For hlta_metadata_map
                        index = len(hlta_metadata_map.keys())
                        
                        citation_count = article_metadata_mag_map[article][0]['CC']
                                                                    
                        if 'keywords' in bib_data.entries[0].keys():
                            keywords = [keyword.lower().strip() for keyword in bib_data.entries[0]['keywords'].split(',')]
                        else:
                            keywords = []
                            
                        hlta_metadata_map[index] = {'title':title,
                                                    'article_link':article,
                                                    'citation_count':citation_count,
                                                    'keywords':keywords,
                                                    'conference':'LAK'}
                    
            print("After processing LAK, # papers:\t%d" % len(hlta_metadata_map.keys()))
                            
        ########################################################################
        if conference_name == 'EDM':
            
            for year in range(2008,2020):
                
                if year != 2019:
                
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    article_metadata_mag_map = json.loads(open(conference_path + str(year) + '/article_metadata_mag_map', 'r', encoding='utf-8').read())
                    
                    processed_articles = set()
                    
                    for articleDict in article_links:
                        
                        title = articleDict['title']
                        pdf_link = articleDict['pdf_link']
                        
                        # Remove duplicates
                        if pdf_link in processed_articles:
                            continue
                        else:
                            processed_articles.add(pdf_link)
                            
                        
                        if pdf_link in selected_publication_map[conference_name][str(year)]:
                                                    
                            xmlFile = pdf_link.split('/')[-1].replace('.pdf', '.tei.xml')
                            
                            # Searching for abstract
                            mark = False
                            
                            tree = ElementTree.parse(conference_path + str(year) + '/' + xmlFile)                        
                             
                            try:
                                abstract = tree.find('.//{http://www.tei-c.org/ns/1.0}abstract/{http://www.tei-c.org/ns/1.0}p').text
                                mark = True
                            except Exception as e:
                                pass
                            
                            if not mark:                            
                                try:
                                    abstract = " ".join(list(json.loads(article_metadata_mag_map[pdf_link][0]['E'])['IA']['InvertedIndex'].keys()))
                                    mark = True
                                except Exception as e:
                                    '''
                                    print(year)
                                    print(title)
                                    print(pdf_link)
                                    print(xmlFile)
                                    print(e)
                                    print('')
                                    abstract = ""
                                    '''
                                    pass
                            
                            if not mark:
                                try:
                                    abstract = supplemented_abstract[xmlFile]
                                    mark = True
                                except:
                                    pass
                            
                            if not mark:
                                print(title)
                                print(xmlFile)
                                abstract = ''
                                
                            data_array.append(title + ' ' + abstract)
                            
                            # For hlta_metadata_map
                            index = len(hlta_metadata_map.keys())
                            
                            if pdf_link in article_metadata_mag_map.keys():
                                citation_count = article_metadata_mag_map[pdf_link][0]['CC']
                            else:
                                citation_count = 0
                                                    
                            keywords = []
                            for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                keyword = element.text.replace('- ', '')
                                keywords.append(keyword.lower().strip())
                            
                            hlta_metadata_map[index] = {'title':title,
                                                        'article_link':pdf_link,
                                                        'citation_count':citation_count,
                                                        'keywords':keywords,
                                                        'conference':'EDM'}
                            
                else:
                    
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    
                    for articleDict in article_links:
                        
                        title = articleDict['title']
                        pdf_link = articleDict['pdf_link']
                        
                        if pdf_link in selected_publication_map[conference_name][str(year)]:
                                                    
                            xmlFile = pdf_link.split('/')[-2] + '.tei.xml'
                            
                            # Searching for abstract
                            mark = False
                            
                            tree = ElementTree.parse(conference_path + str(year) + '/' + xmlFile)                        
                             
                            try:
                                abstract = tree.find('.//{http://www.tei-c.org/ns/1.0}abstract/{http://www.tei-c.org/ns/1.0}p').text
                                mark = True
                            except Exception as e:
                                pass
                            
                            if not mark:
                                try:
                                    abstract = supplemented_abstract[xmlFile]
                                    mark = True
                                except:
                                    pass
                            
                            if not mark:
                                print(title)
                                print(xmlFile)
                                abstract = ''
                                
                            data_array.append(title + ' ' + abstract)
                            
                            # For hlta_metadata_map
                            index = len(hlta_metadata_map.keys())
        
                            citation_count = 0
                                                    
                            keywords = []
                            for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                keyword = element.text.replace('- ', '')
                                keywords.append(keyword.lower().strip())
                            
                            hlta_metadata_map[index] = {'title':title,
                                                        'article_link':pdf_link,
                                                        'citation_count':citation_count,
                                                        'keywords':keywords,
                                                        'conference':'EDM'}
                        
            print("After processing EDM, # papers:\t%d" % len(hlta_metadata_map.keys()))
        
    word_set = set()
    
    print("# articles:\t%d" % len(data_array))
    
    # Preprocess data
    processed_data_array = []
    stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)
    for record in data_array:
        tokens = preprocess_text_data(stop_words, record)
        processed_data_array.append(tokens)
        word_set = word_set.union(set(tokens))
    
    print("# words:\t%d" % len(word_set))
    
    # Output data file for HTLA
    outFile = open(data_path + '/hlta_files_' + "_".join(conferences) + '.txt', 'w', encoding='utf-8')
    writer = csv.writer(outFile)
    for record in processed_data_array:
        writer.writerow(record)
    outFile.close()
    
    folder = data_path + 'hlta_files_' + "_".join(conferences) + '/'
    if not os.path.exists(folder):
        os.mkdir(folder)
    for i in range(len(processed_data_array)):
        outFile = open(folder + str(i) + '.txt', 'w', encoding='utf-8')
        writer = csv.writer(outFile)
        writer.writerow(processed_data_array[i])
        outFile.close()
    
    outFile = open(data_path + '/hlta_metadata_map_' + "_".join(conferences) + '.txt', 'w', encoding='utf-8')
    outFile.write(json.dumps(hlta_metadata_map))
    outFile.close()
    

def generate_data_lda(data_path):
    
    conferences = ['LAK','EDM']
    
    # The list of considered papers
    selected_publication_map = json.loads(open(data_path + 'LAK_EDM_Comparison/selected_papers_' + "_".join(conferences) + '.txt', 'r', encoding='utf-8').read())
    
    # Supplemented abstracts
    supplemented_abstract = dict()
    infile = open(data_path + 'LAK_EDM_Comparison/Data Crawling - Supplemented_Abstract.csv', 'r', encoding='utf-8')
    reader = csv.reader(infile)
    for row in reader:
        conference = row[0]
        year = row[1]
        paperID = row[2]
        abstract = row[3]
        supplemented_abstract[paperID] = abstract
        
    # Supplemented affiliations
    supplemented_affiliations = dict()
    infile = open(data_path + 'LAK_EDM_Comparison/Data Crawling - EDM_2019_Author_Affiliations.csv', 'r', encoding='utf-8')
    reader = csv.reader(infile)
    headers = next(reader, None)
    for row in reader:
        conference = row[0]
        year = row[1]
        article_link = row[2]
        title = row[3]
        author = row[4]
        affiliations = row[5].split(',')
        
        if article_link not in supplemented_affiliations.keys():
            supplemented_affiliations[article_link] = []
        supplemented_affiliations[article_link].append((author, affiliations))
        
    # Read clustering results -------------------------------------------------------
    # Manually selected data ===================================================
    conferences = ['LAK','EDM']
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
    # Read & Process clustering results ========================================
    clusterID_clusterIndex_map = dict()
    for i in range(len(clusterIDs)):
        clusterID_clusterIndex_map[clusterIDs[i]] = i
        
    # Tree structure
    hlta_tree_structure = " ".join(open(data_path + 'LAK_EDM_Comparison/HLTA/12/myModel.nodes.js', 'r', encoding='utf-8').read().split()).replace('var nodes = ', "")[:-1]
    hlta_tree_structure = demjson.decode(hlta_tree_structure)
    
    parentSet = set(['root'])    
    child_parent_map = retrieve_parents({"children":hlta_tree_structure}, parentSet)
            
    # Detected topics
    hlta_clusters = " ".join(open(data_path + 'LAK_EDM_Comparison/HLTA/12/myModel.topics.js', 'r', encoding='utf-8').read().split()).replace('var topicMap = ', "")[:-1]
    hlta_clusters = demjson.decode(hlta_clusters)
    
    # Retrieve the relationship between articles and hlta_clusters
    article_hltaCluster_map = dict()
    for clusterID in hlta_clusters:
        for record in hlta_clusters[clusterID]:
            articleID = record[0]
            score = record[1]
            if articleID not in article_hltaCluster_map.keys():
                article_hltaCluster_map[articleID] = dict()
            article_hltaCluster_map[articleID][clusterID] = score
    
    # Copy articles from child-clusters to parent-clusters
    article_hltaCluster_map_copy = deepcopy(article_hltaCluster_map)    
    for articleID in article_hltaCluster_map_copy.keys():
        for clusterID in article_hltaCluster_map_copy[articleID]:
            parents = child_parent_map[clusterID]
            for parent in parents:
                if parent != 'root':
                    if parent not in article_hltaCluster_map[articleID].keys():
                        article_hltaCluster_map[articleID][parent] = article_hltaCluster_map[articleID][clusterID]
    
    # Retrieve the relationship between hlta_clusters and articles
    '''
    hltaCluster_article_map = dict()
    for articleID in article_hltaCluster_map.keys():
        for clusterID in article_hltaCluster_map[articleID]:
            if clusterID not in hltaCluster_article_map.keys():
                hltaCluster_article_map[clusterID] = set()
            hltaCluster_article_map[clusterID].add(int(articleID))
    '''
    
    # Read mapping between paperIDs and index of clustering result
    hlta_metadata_map_LAK_EDM = json.loads(open(data_path + 'LAK_EDM_Comparison/hlta_metadata_map_LAK_EDM.txt', 'r', encoding='utf-8').read())
    hlta_paper_paperIndex_map = dict()
    for paperIndex in hlta_metadata_map_LAK_EDM.keys():
        article_link = hlta_metadata_map_LAK_EDM[paperIndex]['article_link']
        hlta_paper_paperIndex_map[article_link] = paperIndex
    
    
    # Prepare data -------------------------------------------------------------    
    lda_data_array = []
        
    for conference_name in conferences:
        conference_path = data_path + conference_name + '/'
        
        ########################################################################
        if conference_name == 'LAK':
            for year in range(2011,2020):
                # Metadata repository
                article_metadata_map = json.loads(open(conference_path + str(year) + '/article_metadata_map', 'r').read())
                article_metadata_mag_map = json.loads(open(conference_path + str(year) + '/article_metadata_mag_map', 'r').read())
                                
                for article in article_metadata_map.keys():
                    
                    if article in selected_publication_map[conference_name][str(year)]:                        
                                     
                        bibtexText = article_metadata_map[article]['bibtex']
                        bib_data = bibtexparser.loads(bibtexText)
                        
                        title = bib_data.entries[0]['title']
                        abstract = article_metadata_map[article]['abstract']                                                
                        citation_count = article_metadata_mag_map[article][0]['CC']
                                                                    
                        if 'keywords' in bib_data.entries[0].keys():
                            keywords = [keyword.lower().strip() for keyword in bib_data.entries[0]['keywords'].split(',')]
                        else:
                            keywords = []
                                                
                        xmlFile = article.split('=')[-1] + '.tei.xml'                        
                        # print(xmlFile)
                                         
                        tree = ElementTree.parse(conference_path + str(year) + '/' + xmlFile)        
                        
                        bodyText = []
                        
                        divElements = tree.findall('.//{http://www.tei-c.org/ns/1.0}div')
                        for divElement in divElements:                                
                            try:                          
                                head = None                            
                                if 'type' not in divElement.attrib:
                                    headElement = divElement.find('.//{http://www.tei-c.org/ns/1.0}head')
                                    if 'n' in headElement.attrib:
                                        head = headElement.attrib['n'] + ' ' + headElement.text
                                                          
                                    if head != None:
                                        bodyText.append({'section_title':head, 'section_text': ' '.join(divElement.itertext())})
                                    else:
                                        if len(bodyText) == 0:                                                
                                            bodyText.append({'section_title':'', 'section_text': ' '.join(divElement.itertext())})                                            
                                        else:
                                            bodyText[-1] = {'section_title':bodyText[-1]['section_title'], 'section_text': bodyText[-1]['section_text'] + ' ' + ' '.join(divElement.itertext())}
                                    
                            except Exception as e:
                                print(e)            
                                                
                        # Authors & Affiliations
                        authors_affiliations = article_metadata_mag_map[article][0]['AA']
                        
                        RId = article_metadata_mag_map[article][0]['RId']
                        
                        # Clusters
                        paperIndex = hlta_paper_paperIndex_map[article]
                        
                        if paperIndex in article_hltaCluster_map.keys():
                            clusters = [(clusterID,article_hltaCluster_map[paperIndex][clusterID]) for clusterID in article_hltaCluster_map[paperIndex].keys() if clusterID in clusterIDs]
                        # else:
                        #     print(paperIndex)
                        
                        lda_data_array.append({'title':title,
                                               'abstract':abstract,
                                               'citation_count':citation_count,
                                               'keywords':keywords,
                                               'bodyText':bodyText,
                                               'authors_affiliations':authors_affiliations,
                                               'RId':RId,
                                               'conference':conference_name,
                                               'year':year,
                                               'clusters':clusters})
                    
            print("After processing LAK, # papers:\t%d" % len(lda_data_array))
                            
        ########################################################################
        if conference_name == 'EDM':
            
            for year in range(2008,2020):
                
                if year != 2019:
                
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    article_metadata_mag_map = json.loads(open(conference_path + str(year) + '/article_metadata_mag_map', 'r', encoding='utf-8').read())
                    
                    processed_articles = set()
                    
                    for articleDict in article_links:
                        
                        title = articleDict['title']
                        pdf_link = articleDict['pdf_link']
                        
                        # Remove duplicates
                        if pdf_link in processed_articles:
                            continue
                        else:
                            processed_articles.add(pdf_link)
                                                
                        if pdf_link in selected_publication_map[conference_name][str(year)]:
                                                    
                            xmlFile = pdf_link.split('/')[-1].replace('.pdf', '.tei.xml')
                            
                            # Searching for abstract
                            mark = False
                            
                            tree = ElementTree.parse(conference_path + str(year) + '/' + xmlFile)                        
                             
                            try:
                                abstract = tree.find('.//{http://www.tei-c.org/ns/1.0}abstract/{http://www.tei-c.org/ns/1.0}p').text
                                mark = True
                            except Exception as e:
                                pass
                            
                            if not mark:                            
                                try:
                                    abstract = " ".join(list(json.loads(article_metadata_mag_map[pdf_link][0]['E'])['IA']['InvertedIndex'].keys()))
                                    mark = True
                                except Exception as e:
                                    '''
                                    print(year)
                                    print(title)
                                    print(pdf_link)
                                    print(xmlFile)
                                    print(e)
                                    print('')
                                    abstract = ""
                                    '''
                                    pass
                            
                            if not mark:
                                try:
                                    abstract = supplemented_abstract[xmlFile]
                                    mark = True
                                except:
                                    pass
                            
                            if not mark:
                                print(title)
                                print(xmlFile)
                                abstract = ''
                            
                            # For lda_data_array                            
                            if pdf_link in article_metadata_mag_map.keys():
                                citation_count = article_metadata_mag_map[pdf_link][0]['CC']
                            else:
                                citation_count = 0
                                                    
                            keywords = []
                            for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                keyword = element.text.replace('- ', '')
                                keywords.append(keyword.lower().strip())
                                
                            bodyText = []
                                                   
                            divElements = tree.findall('.//{http://www.tei-c.org/ns/1.0}div')
                            for divElement in divElements:                                
                                try:                          
                                    head = None                            
                                    if 'type' not in divElement.attrib:
                                        headElement = divElement.find('.//{http://www.tei-c.org/ns/1.0}head')
                                        if 'n' in headElement.attrib:
                                            head = headElement.attrib['n'] + ' ' + headElement.text
                                                              
                                        if head != None:
                                            bodyText.append({'section_title':head, 'section_text': ' '.join(divElement.itertext())})
                                        else:
                                            if len(bodyText) == 0:                                                
                                                bodyText.append({'section_title':'', 'section_text': ' '.join(divElement.itertext())})                                            
                                            else:
                                                bodyText[-1] = {'section_title':bodyText[-1]['section_title'], 'section_text': bodyText[-1]['section_text'] + ' ' + ' '.join(divElement.itertext())}
                                        
                                except Exception as e:
                                    print(e)
                            
                            # Authors & Affiliations
                            if pdf_link in article_metadata_mag_map.keys():
                                authors_affiliations = article_metadata_mag_map[pdf_link][0]['AA']                                
                            else:
                                authors_affiliations = []
                                
                            if pdf_link in article_metadata_mag_map.keys():
                                if 'RId' in article_metadata_mag_map[pdf_link][0].keys():
                                    RId = article_metadata_mag_map[pdf_link][0]['RId']
                                else:
                                    RId = []
                            else:
                                authors_affiliations = []
                                RId = []
                                
                            # Clusters
                            paperIndex = hlta_paper_paperIndex_map[pdf_link]
                            
                            if paperIndex in article_hltaCluster_map.keys():
                                clusters = [(clusterID,article_hltaCluster_map[paperIndex][clusterID]) for clusterID in article_hltaCluster_map[paperIndex].keys() if clusterID in clusterIDs]
                            # else:
                            #     print(paperIndex)
                                                                                 
                            lda_data_array.append({'title':title,
                                                   'abstract':abstract,
                                                   'citation_count':citation_count,
                                                   'keywords':keywords,
                                                   'bodyText':bodyText,
                                                   'authors_affiliations':authors_affiliations,
                                                   'RId':RId,
                                                   'conference':conference_name,
                                                   'year':year,
                                                   'clusters':clusters})
                            
                else:
                    
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    
                    for articleDict in article_links:
                        
                        title = articleDict['title']
                        pdf_link = articleDict['pdf_link']
                        
                        if pdf_link in selected_publication_map[conference_name][str(year)]:
                                                    
                            xmlFile = pdf_link.split('/')[-2] + '.tei.xml'
                            
                            # Searching for abstract
                            mark = False
                            
                            tree = ElementTree.parse(conference_path + str(year) + '/' + xmlFile)                        
                             
                            try:
                                abstract = tree.find('.//{http://www.tei-c.org/ns/1.0}abstract/{http://www.tei-c.org/ns/1.0}p').text
                                mark = True
                            except Exception as e:
                                pass
                            
                            if not mark:
                                try:
                                    abstract = supplemented_abstract[xmlFile]
                                    mark = True
                                except:
                                    pass
                            
                            if not mark:
                                # print(title)
                                # print(xmlFile)
                                abstract = ''
                            
                            # For lda_data_array
                            citation_count = 0
                                
                            keywords = []
                            for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                keyword = element.text.replace('- ', '')
                                keywords.append(keyword.lower().strip())
                                
                            bodyText = []                        
                            divElements = tree.findall('.//{http://www.tei-c.org/ns/1.0}div')
                            for divElement in divElements:                                
                                try:                          
                                    head = None                            
                                    if 'type' not in divElement.attrib:
                                        headElement = divElement.find('.//{http://www.tei-c.org/ns/1.0}head')
                                        if 'n' in headElement.attrib:
                                            head = headElement.attrib['n'] + ' ' + headElement.text
                                                              
                                        if head != None:
                                            bodyText.append({'section_title':head, 'section_text': ' '.join(divElement.itertext())})
                                        else:
                                            if len(bodyText) == 0:                                                
                                                bodyText.append({'section_title':'', 'section_text': ' '.join(divElement.itertext())})                                            
                                            else:
                                                bodyText[-1] = {'section_title':bodyText[-1]['section_title'], 'section_text': bodyText[-1]['section_text'] + ' ' + ' '.join(divElement.itertext())}
                                        
                                except Exception as e:
                                    print(e)
                            
                            # Authors & Affiliations
                            if pdf_link in supplemented_affiliations.keys():
                                authors_affiliations = [{"AuN": author, "AuId": None, "AfN": [affiliation.lower() for affiliation in affiliations], "AfId": None, "S": None} for (author, affiliations) in supplemented_affiliations[pdf_link]]
                            RId = []
                            
                            # Clusters
                            paperIndex = hlta_paper_paperIndex_map[pdf_link]
                            
                            if paperIndex in article_hltaCluster_map.keys():
                                clusters = [(clusterID,article_hltaCluster_map[paperIndex][clusterID]) for clusterID in article_hltaCluster_map[paperIndex].keys() if clusterID in clusterIDs]
                            # else:
                            #     print(paperIndex)
                            
                            
                            lda_data_array.append({'title':title,
                                                   'abstract':abstract,
                                                   'citation_count':citation_count,
                                                   'keywords':keywords,
                                                   'bodyText':bodyText,
                                                   'authors_affiliations':authors_affiliations,
                                                   'RId':RId,
                                                   'conference':conference_name,
                                                   'year':year,
                                                   'clusters':clusters})
                        
            print("After processing EDM, # papers:\t%d" % len(lda_data_array))
    
    # Output data file for LDA
    outFile = open(data_path + 'LAK_EDM_Comparison/lda_data_array_' + "_".join(conferences) + '.txt', 'w', encoding='utf-8')
    outFile.write(json.dumps(lda_data_array))
    outFile.close()
    
   

    
def retrieve_children(node):
    children_set = set()
    if len(node['children']) == 0:
        children_set.add(node['id'])
    else:
        for child_node in node['children']:
            children_set = children_set.union(retrieve_children(child_node))
    return list(children_set)
    

def retrieve_nodes_by_level(tree_structure, target_level):
    nodes_map = dict()
    if isinstance(tree_structure, list):
        for node in tree_structure:        
            nodeID = node['id']
            nodeText = node['text']
            current_level = node['data']['level']
            if current_level == target_level:
                children_set = retrieve_children(node)         
                nodes_map[nodeID] = {'nodeText':nodeText,
                                     'children':children_set}
            else:
                for child_node in node['children']:
                    nodes_map = {**nodes_map, **retrieve_nodes_by_level(child_node, target_level)}
    else:
        nodeID = tree_structure['id']
        nodeText = tree_structure['text']
        children_set = retrieve_children(tree_structure)
        
        nodes_map[nodeID] = {'nodeText':nodeText,
                             'children':children_set}       
        
    return nodes_map


def retrieve_topK_cited_papers(clusterID, articles, article_cluster_map, hlta_metadata_map, nodeText, k):
    stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)
    
    article_citation_map = dict()
    for article in articles:
        article = str(article)
        title = hlta_metadata_map[article]['title']
        conference = hlta_metadata_map[article]['conference']
        citation_count = hlta_metadata_map[article]['citation_count']
        article_citation_map[article] = {'title':title, 
                                         'citation_count':citation_count,
                                         'conference':conference}
        
    sorted_article_citation_map = sorted(article_citation_map.items(), key = lambda x: (x[1]["citation_count"]), reverse=True)
    
    dominant_words = nodeText.split()[1:]
    
    print('*** Most cited papers:')
    display_num = k
    for i in range(len(sorted_article_citation_map)):
        if display_num > 0:
            article = sorted_article_citation_map[i][0]
            title = sorted_article_citation_map[i][1]['title']
            conference = sorted_article_citation_map[i][1]['conference']
            citation_count = sorted_article_citation_map[i][1]['citation_count']
            
            print("PaperID:%s\t%s\t%d\t%s" % (article, title, citation_count, conference))
            display_num -= 1
        else:
            break
        
    print('*** Most cited papers (contains dominant keywords):')
    display_num = k
    for i in range(len(sorted_article_citation_map)):
        if display_num > 0:
            article = sorted_article_citation_map[i][0]
            title = sorted_article_citation_map[i][1]['title']
            conference = sorted_article_citation_map[i][1]['conference']
            citation_count = sorted_article_citation_map[i][1]['citation_count']
            
            mark = False
            for word in dominant_words:
                if word in preprocess_text_data(stop_words, title):
                    mark = True
                    break            
            
            if mark: 
                print("PaperID:%s\t%s\t%d\t%s" % (article, title, citation_count, conference))
                display_num -= 1
            
        else:
            break
    '''
    print('*** Most cited papers (only being classified to this group):')
    display_num = k
    for i in range(len(sorted_article_citation_map)):
        if display_num > 0:
            article = sorted_article_citation_map[i][0]
            title = sorted_article_citation_map[i][1]['title']
            citation_count = sorted_article_citation_map[i][1]['citation_count']
            
            if len(article_cluster_map[article]) == 1:
                print("PaperID:%s\t%s\t%d" % (article, title, citation_count))
                display_num -= 1
            
        else:
            break
    '''
        
    print('')
    

def retrieve_topK_keywords(articles, hlta_metadata_map, k):
    keywords_map = defaultdict(int)
    for article in articles:
        article = str(article)        
        keywords = hlta_metadata_map[article]['keywords']
        for keyword in keywords:
            keywords_map[keyword] += 1
    sorted_keywords_map = sorted(keywords_map.items(), key=operator.itemgetter(1), reverse=True)
    
    print('*** Frequent keywords:')
    for i in range(k):
        print("%s\t%d" % (sorted_keywords_map[i][0], sorted_keywords_map[i][1]))
    print('')


def retrieve_parents(tree_structure, parentSet):
    child_parent_map = dict()    
    
    if len(tree_structure['children']) != 0:
        for node in tree_structure['children']:
            nodeID = node['id']
            child_parent_map[nodeID] = parentSet                
            
            parentSetCopy = deepcopy(parentSet)
            parentSetCopy.add(nodeID)
            for subNode in node['children']:
                child_parent_map = {**child_parent_map, **retrieve_parents(subNode, parentSetCopy)}
                # print(child_parent_map)
    else:
        nodeID = tree_structure['id']
        child_parent_map[nodeID] = parentSet
        
    return child_parent_map
                    

def analyze_topic_detection_results(data_path, num_display_level, version):    
    # Tree structure
    tree_structure = " ".join(open(data_path + 'LAK_EDM_Comparison/HLTA/' + version + '/myModel.nodes.js', 'r', encoding='utf-8').read().split()).replace('var nodes = ', "")[:-1]
    # print(tree_structure)
    # print('')
    tree_structure = demjson.decode(tree_structure)
    
    parentSet = set(['root'])    
    child_parent_map = retrieve_parents({"children":tree_structure}, parentSet)
    # print(child_parent_map)
        
    # Detected topics
    clusters = " ".join(open(data_path + 'LAK_EDM_Comparison/HLTA/' + version + '/myModel.topics.js', 'r', encoding='utf-8').read().split()).replace('var topicMap = ', "")[:-1]
    clusters = demjson.decode(clusters)
    
    # Retrieve the relationship between articles and clusters
    article_cluster_map = dict()
    for clusterID in clusters:
        for record in clusters[clusterID]:
            articleID = record[0]
            if articleID not in article_cluster_map.keys():
                article_cluster_map[articleID] = set()
            article_cluster_map[articleID].add(clusterID)
    
    # Copy scores from children to parents
    '''
    article_cluster_map_copy = deepcopy(article_cluster_map)    
    for articleID in article_cluster_map_copy.keys():
        for clusterID in article_cluster_map_copy[articleID].keys():
            score = article_cluster_map_copy[articleID][clusterID]
            parents = child_parent_map[clusterID]
            for parent in parents:
                if parent != 'root':
                    article_cluster_map[articleID][parent] = score
    '''
    # Copy articles from child-clusters to parent-clusters
    article_cluster_map_copy = deepcopy(article_cluster_map)    
    for articleID in article_cluster_map_copy.keys():
        for clusterID in article_cluster_map_copy[articleID]:
            parents = child_parent_map[clusterID]
            for parent in parents:
                if parent != 'root':
                    article_cluster_map[articleID].add(parent)
        
    ''' 
    # Keep clusters that receive maximum score
    for articleID in article_cluster_map.keys():
        maxScore = 0
        for parent in article_cluster_map[articleID].keys():
            if maxScore < article_cluster_map[articleID][parent]:
                maxScore = article_cluster_map[articleID][parent]        
        article_cluster_map[articleID] = {parent:article_cluster_map[articleID][parent] for parent in article_cluster_map[articleID].keys() if article_cluster_map[articleID][parent] == maxScore}
    '''
                              
    print("# articles that have been successfully identified with topics:\t%d" % len(article_cluster_map.keys()))
    print('')
    
    # Retrieve the relationship between clusters and articles
    '''
    cluster_article_map = dict()
    for clusterID in clusters:
        cluster_article_map[clusterID] = []
        for record in clusters[clusterID]:
            articleID = record[0]
            cluster_article_map[clusterID].append(int(articleID))
    '''
    cluster_article_map = dict()
    for articleID in article_cluster_map.keys():
        for clusterID in article_cluster_map[articleID]:
            if clusterID not in cluster_article_map.keys():
                cluster_article_map[clusterID] = set()
            cluster_article_map[clusterID].add(int(articleID))
        
    # print(topic_map)
    # print('')
        
    # Cluster overlaps
    clusters_array = []
    for cluster in tree_structure:
        clusterID = cluster['id']
        clusters_array.append(clusterID)
    # print(clusters_array)
    # print('')
    
    avg_cluster_num = sum([len(cluster_article_map[cluster]) for cluster in clusters_array]) / float(len(article_cluster_map.keys()))
    print('On average, each article belongs to # clusters:\t%.2f\n' % avg_cluster_num)
    
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
    print("\t".join(clusterIDs))
    print("\t".join([str(len(cluster_article_map[cluster])) for cluster in clusterIDs]))
    
    print('')
    for i in range(len(clusterIDs)):
        jaccard_array = []
        for j in range(i+1):
            jaccard_array.append("-")
        for k in range(i+1, len(clusterIDs)):
            jaccard = len(cluster_article_map[clusterIDs[i]].intersection(cluster_article_map[clusterIDs[k]])) / float(len(cluster_article_map[clusterIDs[i]].union(cluster_article_map[clusterIDs[k]])))
            jaccard_array.append(str(int(jaccard*1000)/float(1000)))
        print("\t".join(jaccard_array))
    print('')
    
    # Bar chart ----------------------------------------------------------------
    value_array = []
    for article in article_cluster_map.keys():
        value_array.append(len(article_cluster_map[article].intersection(set(clusterIDs))))
    
    start = 0
    end = 8
    step = 1
    x_labels = list(range(start, end, step))
    bar_nums = [0] * (len(x_labels))
        
    for record_value in value_array:
        index = int(record_value / step) - 1
        bar_nums[index] += 1
        
    # Normalization
    bar_nums = [record_value/float(len(article_cluster_map.keys()))*100 for record_value in bar_nums]
    x_pos = numpy.arange(len(x_labels)) + 1
    
    plt.figure(figsize=(12, 7.5))
    plt.bar(x_pos, bar_nums, width=0.8, linewidth=0.4, edgecolor='black', align='center', color='#5974A4')
    
    for i in range(len(bar_nums)):
        plt.text(x_pos[i]-0.15, bar_nums[i]+0.25, ('%.1f' % bar_nums[i]) + '%')
    
    # x-axis labels
    updated_x_lables = []
    for i in range(len(x_labels)):
        updated_x_lables.append(str(x_labels[i] + 1))
    plt.xticks(x_pos, updated_x_lables)

    # y-axix percentage
    points = 0   
    plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
    
    plt.xlabel('# Clusters')    
    plt.ylabel('% Papers')
    
    title = 'Number of clusters of papers_LAK_EDM.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + title, bbox_inches='tight', pad_inches = 0.05)
    
    plt.show()        
    
    ############################################################################   
    
    highest_level = tree_structure[0]['data']['level']
    print('Total # of levels:\t%d' % highest_level)
    
    # Read hlta_metadata_map
    hlta_metadata_map = json.loads(open(data_path + 'LAK_EDM_Comparison/hlta_metadata_map_LAK_EDM.txt', 'r').read())
            
    # Analyze
    current_level = highest_level
    while current_level > highest_level - num_display_level:
        print("Current leve is:\t%d --------------------------" % current_level)
        nodes_map = retrieve_nodes_by_level(tree_structure, current_level)
        print("# clusters:\t%d\n" % len(nodes_map.keys()))
        # print(nodes_map)
        
        covered_articles = set()
        
        for nodeID in clusterIDs:
            # print("----- Node:\t%s\t%s" % (nodeID, nodes_map[nodeID]['nodeText']))
            # print("%s" % ", ".join(nodes_map[nodeID]['nodeText'].split()[1:]))
            print("ClusterID:%s\tDominant terms:%s" % (nodeID, ", ".join(nodes_map[nodeID]['nodeText'].split()[1:])))
                        
            # Retrieve articles belonging to this cluster       
            articles = set(cluster_article_map[nodeID])
            
            # for subcluster in nodes_map[nodeID]['children']:
            #     if subcluster in cluster_article_map.keys():
            #         articles = articles.union(set(cluster_article_map[subcluster]))
            
            # print("# papers:\t%d" % len(articles))
            
            # Retrieve top-k cited papers
            retrieve_topK_cited_papers(nodeID, articles, article_cluster_map, hlta_metadata_map, nodes_map[nodeID]['nodeText'], 20)
            
            # Retrieve top-k keywords
            # retrieve_topK_keywords(articles, hlta_metadata_map, 5)
            # print('\n')
        
        current_level -= 1
        

def select_papers(data_path):
    
    conferences = ['LAK','EDM']
    selected_publication_map = dict()
    
    # Manually-collected paper list
    paperListMap = dict()
    paperListCountMap = dict()
    for conference_name in conferences:
        paperListMap[conference_name] = dict()
        paperListCountMap[conference_name] = dict()
    
    paperListFile = open(data_path + 'Data Crawling - LAK_EDM_PaperList.csv', 'r', encoding='utf-8')
    paperListReader = csv.reader(paperListFile)
    for row in paperListReader:
        conference_name = row[0]
        year = int(row[1])
        paperType = row[2]
        title = row[3].lower() 
        if year not in paperListMap[conference_name].keys():
            paperListMap[conference_name][year] = []
            paperListCountMap[conference_name][year] = dict()
     
        paperListMap[conference_name][year].append(title)
        
        if paperType not in paperListCountMap[conference_name][year].keys():
            paperListCountMap[conference_name][year][paperType] = []
        paperListCountMap[conference_name][year][paperType].append(title)
        
    for year in range(2011,2020):
        for paperType in ['Short', 'Long']:
            if paperType in paperListCountMap[conference_name][year].keys():
                print("Year\t%d\t%s\t%d" % (year, paperType, len(paperListCountMap[conference_name][year][paperType])))
    print('\n')
    
    # Gather paper lists
    for conference_name in conferences:
        conference_path = data_path + conference_name + '/'
        
        selected_publication_map[conference_name] = dict()
                
        ########################################################################
        
        if conference_name == 'LAK':
            for year in range(2011,2020):
                
                selected_publication_map[conference_name][year] = []                
                article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())
                
                for article_link in article_links:                    
                    title = article_link[0].lower()
                    link = article_link[1]
                    
                    if title in paperListMap[conference_name][year]:
                        selected_publication_map[conference_name][year].append(link)
                        # selected_publication_map[conference_name][year].append(title)
                
                # Manually checking
                # print(len(set(paperListMap[conference_name][year])))
                # print(len(set(selected_publication_map[conference_name][year])))
                # for title in paperListMap[conference_name][year]:
                #     if title not in selected_publication_map[conference_name][year]:
                #         print(title)
                
        print('\n\n')
                         
        ########################################################################
        if conference_name == 'EDM':
            for year in range(2008,2020):
                
                selected_publication_map[conference_name][year] = []
                                    
                if year in [2008]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                            
                if year in [2009, 2010]:
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:                                        
                        title = articleDict['title'].lower()
                        pdf_link = articleDict['pdf_link']                              
                        if title in paperListMap[conference_name][year]:
                            selected_publication_map[conference_name][year].append(pdf_link)
                                            
                if year in [2011]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Short Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                
                if year in [2012]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full Papers Accepted']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Short papers accepted']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                
                if year in [2013]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Oral Presentations (Full Papers)']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Oral Presentations (Short Papers)']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                            
                if year in [2014]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Short papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                
                if year in [2015, 2016]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Short Papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                
                if year in [2017, 2018]:                                   
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['Full papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['Short papers']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                
                if year in [2019]:
                    article_links = json.loads(open(conference_path + str(year) + '/article_links', 'r', encoding='utf-8').read())                    
                    for articleDict in article_links:
                        pdf_link = articleDict['pdf_link']
                        category = articleDict['category']                        
                        if category in ['FULL PAPERS']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                        if category in ['SHORT PAPERS']:
                            selected_publication_map[conference_name][year].append(pdf_link)
                                   
                print("%s\t%s\t%d" % (conference_name, year, len(set(selected_publication_map[conference_name][year]))))
                    
    outFile = open(data_path + '/selected_papers_' + "_".join(conferences) + '.txt', 'w', encoding='utf-8')
    outFile.write(json.dumps(selected_publication_map))
    outFile.close()
    


def main():  
    
    data_path = '../data/'
    
    # Step 0: Select papers
    # select_papers(data_path)    
    
    # Step 1: Analyze paper types 
    # analyze_page_types(data_path)
    
    # Step 2: Generate data files for Hierarchical Latent Tree Analysis (HLTA)
    # generate_data_hlta(data_path)
    # generate_data_lda(data_path)
        
    # Step 3: Analyze topic detection results
    analyze_topic_detection_results(data_path, 1, "12")
    
   
if __name__ == "__main__":
    main()