'''
Created on 29 Sep 2019

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

from topicDetection.detectTopics import retrieve_parents,\
    retrieve_nodes_by_level



def analyze_topic_detection_results(data_path, num_display_level, version):
    
    word2vecFile = open(data_path + 'LAK_EDM_Comparison/future/w2v_second.csv', 'r', encoding='utf-8')
    reader = csv.reader(word2vecFile)
    next(reader)
    word_similarWords_map = dict()
    for row in reader:
        term = row[0]
        
        abstractWords = row[3][2:-2].split('\', \'')
        futureWords = row[4][2:-2].split('\', \'')
        
                        
        word_similarWords_map[term] = {'abstractWords':abstractWords,
                                       'futureWords':futureWords}
    
    
    ############################################################################
    # Tree structure
    tree_structure = " ".join(open(data_path + 'LAK_EDM_Comparison/HLTA/' + version + '/myModel.nodes.js', 'r', encoding='utf-8').read().split()).replace('var nodes = ', "")[:-1]
    tree_structure = demjson.decode(tree_structure)
    
    parentSet = set(['root'])    
    child_parent_map = retrieve_parents({"children":tree_structure}, parentSet)
      
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
    
    # Copy articles from child-clusters to parent-clusters
    article_cluster_map_copy = deepcopy(article_cluster_map)    
    for articleID in article_cluster_map_copy.keys():
        for clusterID in article_cluster_map_copy[articleID]:
            parents = child_parent_map[clusterID]
            for parent in parents:
                if parent != 'root':
                    article_cluster_map[articleID].add(parent)
    
    # Retrieve the relationship between clusters and articles
    cluster_article_map = dict()
    for articleID in article_cluster_map.keys():
        for clusterID in article_cluster_map[articleID]:
            if clusterID not in cluster_article_map.keys():
                cluster_article_map[clusterID] = set()
            cluster_article_map[clusterID].add(int(articleID))
    
    
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
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
        
        covered_articles = set()
        
        for nodeID in clusterIDs:
            # print("ClusterID:%s\tDominant terms:%s" % (nodeID, ", ".join(nodes_map[nodeID]['nodeText'].split()[1:])))
            
            abstractWords_count_map = defaultdict(int)
            futureWords_count_map = defaultdict(int)
            
            for term in nodes_map[nodeID]['nodeText'].split()[1:]:
                term = term.replace('-', '_')
                try:
                    
                    abstractWords = word_similarWords_map[term]['abstractWords']
                    futureWords = word_similarWords_map[term]['futureWords']
                    
                    for word in abstractWords:
                        
                        abstractWords_count_map[word] += 1
                    for word in futureWords:
                        futureWords_count_map[word] += 1                    
                except:
                    pass
                    #print(term)
                    
            sorted_abstractWords_count_map = sorted(abstractWords_count_map.items(), key=lambda x: x[1], reverse=True)
            sorted_futureWords_count_map = sorted(futureWords_count_map.items(), key=lambda x: x[1], reverse=True)
            
            
            def print_topK_words(sorted_map, topK=10):
                
                selectedWords = []
                for i in range(topK):
                    selectedWords.append(sorted_map[i][0])
                    # print(sorted_map[i][1])
                # print(", ".join(selectedWords))
                return set(selectedWords)
                
            abstractSimilarWords = print_topK_words(sorted_abstractWords_count_map)
            futureSimilarWords = print_topK_words(sorted_futureWords_count_map)
            
            futureSimilarWords = futureSimilarWords - abstractSimilarWords
            
            # print('\n\n')
               
            # Retrieve articles belonging to this cluster       
            articles = set(cluster_article_map[nodeID])        
            
            # for subcluster in nodes_map[nodeID]['children']:
            #     if subcluster in cluster_article_map.keys():
            #         articles = articles.union(set(cluster_article_map[subcluster]))
            
            # print("# papers:\t%d" % len(articles))
            
            # Retrieve top-k cited papers
            # retrieve_topK_cited_papers(nodeID, articles, article_cluster_map, hlta_metadata_map, nodes_map[nodeID]['nodeText'], 20)
            
            # Retrieve top-k keywords
            # retrieve_topK_keywords(articles, hlta_metadata_map, 5)
            # print('\n')
        
        current_level -= 1
  



def main():  
    
    data_path = '../../data/'    
    analyze_topic_detection_results(data_path, 1, "12")
   
if __name__ == "__main__":
    main()
    