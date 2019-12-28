'''
Created on 11 Jun 2019

@author: gche0022
'''

import os
import csv
import json
import bibtexparser
from xml.etree import ElementTree
from _collections import defaultdict


def find_rec(node, element):
    for item in node.findall(element):
        yield item
        for child in find_rec(item, element):
            yield child


def generate_gephi_csvFiles(data_path):
    
    outFile = open(data_path + 'lak_edm_keywords_gephi.csv', 'w', encoding='utf-8')
    writer = csv.writer(outFile)
    writer.writerow(['Source', 'Target'])
    
    keyword_map = defaultdict(int)
    # edge_count = 0
    edge_array = []
        
    conferences = ['LAK', 'EDM']
    for conference_name in conferences:
        conference_path = os.path.dirname(data_path) + '/' + conference_name + '/'
        for year in os.listdir(conference_path):
            if year != '.DS_Store':                
                if conference_name in ['LAK']:
                    article_metadata_map = json.loads(open(conference_path + year + '/article_metadata_map', 'r', encoding='utf-8').read())               
                    for article in article_metadata_map.keys():
                        bibtexText = article_metadata_map[article]['bibtex']
                        bib_data = bibtexparser.loads(bibtexText)
                        if 'keywords' in bib_data.entries[0].keys():
                            keywords = bib_data.entries[0]['keywords'].split(',')
                            for i in range(len(keywords)):
                                keyword_map[keywords[i].strip().lower()] += 1
                                for j in range(i+1, len(keywords)):
                                    # writer.writerow([keywords[i].strip().lower(), keywords[j].strip().lower()])
                                    # edge_count += 1
                                    edge_array.append([keywords[i].strip().lower(), keywords[j].strip().lower()])
                                    
                if conference_name in ['EDM']:
                    
                    if os.path.isdir(conference_path + year):                    
                        articles = os.listdir(conference_path + year)
                        for article in articles:
                            if article.endswith('.tei.xml'):
                                tree = ElementTree.parse(conference_path + year + '/' + article)
                                
                                keywords = []
                                for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                    keyword = element.text.replace('- ', '')
                                    keywords.append(keyword)
                                
                                for i in range(len(keywords)):
                                    keyword_map[keywords[i].strip().lower()] += 1
                                    for j in range(i+1, len(keywords)):
                                        # writer.writerow([keywords[i].strip().lower(), keywords[j].strip().lower()])
                                        # edge_count += 1
                                        edge_array.append([keywords[i].strip().lower(), keywords[j].strip().lower()])
        
    def merge_keywords(edge, origianl_keyword, replaced_keyword):
        if edge[0] == origianl_keyword:
            edge[0] = replaced_keyword
        if edge[1] == origianl_keyword:
            edge[1] = replaced_keyword
        return edge
                                 
    for edge in edge_array:
        if keyword_map[edge[0]] > 1 and keyword_map[edge[1]] > 1:
            edge = merge_keywords(edge, 'mooc', 'moocs')
            edge = merge_keywords(edge, 'intelligent tutoring system', 'intelligent tutoring systems')
            writer.writerow(edge)
    
    outFile.close()
                                    
    # print("# keywords:\t%d" % (len(keyword_set)))
    # print("# edges:\t%d" % edge_count)
    
    for keyword in keyword_map.keys():
        if "social" in keyword:
            print(keyword)
    
    
                
def main():
    
    data_path = '../data/'
    
    # Generate .csv files for Gephi
    generate_gephi_csvFiles(data_path)
    
    
    
         
   
if __name__ == "__main__":
    main()