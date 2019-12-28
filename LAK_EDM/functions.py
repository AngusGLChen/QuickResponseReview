'''
Created on 13 Aug 2019

@author: gche0022
'''

import json, demjson, csv

from copy import deepcopy
from topicDetection.detectTopics import retrieve_parents



def read_selected_data(data_path):
    
    # Manually selected data ===================================================
    conferences = ['LAK','EDM']
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
          
    # Read selected articles ===================================================
    selected_publication_map = json.loads(open(data_path + 'LAK_EDM_Comparison/selected_papers_' + "_".join(conferences) + '.txt', 'r', encoding='utf-8').read())
    
    
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
            if articleID not in article_hltaCluster_map.keys():
                article_hltaCluster_map[articleID] = set()
            article_hltaCluster_map[articleID].add(clusterID)
    
    # Copy articles from child-clusters to parent-clusters
    article_hltaCluster_map_copy = deepcopy(article_hltaCluster_map)    
    for articleID in article_hltaCluster_map_copy.keys():
        for clusterID in article_hltaCluster_map_copy[articleID]:
            parents = child_parent_map[clusterID]
            for parent in parents:
                if parent != 'root':
                    article_hltaCluster_map[articleID].add(parent)
    
    # Retrieve the relationship between hlta_clusters and articles
    hltaCluster_article_map = dict()
    for articleID in article_hltaCluster_map.keys():
        for clusterID in article_hltaCluster_map[articleID]:
            if clusterID not in hltaCluster_article_map.keys():
                hltaCluster_article_map[clusterID] = set()
            hltaCluster_article_map[clusterID].add(int(articleID))
    
    
    # Read mapping between paperIDs and index of clustering result =============
    hlta_metadata_map_LAK_EDM = json.loads(open(data_path + 'LAK_EDM_Comparison/hlta_metadata_map_LAK_EDM.txt', 'r', encoding='utf-8').read())
    hlta_paper_paperIndex_map = dict()
    for paperIndex in hlta_metadata_map_LAK_EDM.keys():
        article_link = hlta_metadata_map_LAK_EDM[paperIndex]['article_link']
        hlta_paper_paperIndex_map[article_link] = paperIndex
    
    
    # Prepare data =============================================================    
    data_repository = dict()
    years = range(2008,2020)
    
    for conference in conferences:
        data_repository[conference] = dict()
        for year in years:
            data_repository[conference][year] = []
            
    for conference in conferences:
        for year in years:
            
            if conference == 'EDM' and year == 2019:
                article_links = json.loads(open(data_path + conference + '/' + str(year) + '/article_links', 'r', encoding='utf-8').read())              
                
                # Supplemented affiliations
                supplemented_affiliations = dict()
                infile = open(data_path + 'LAK_EDM_Comparison/Data Crawling - EDM_2019_Author_Affiliations.csv', 'r', encoding='utf-8')
                reader = csv.reader(infile)
                next(reader, None)
                for row in reader:
                    article_link = row[2]                   
                    author = row[4]
                    affiliations = row[5].split(',')
                    
                    if article_link not in supplemented_affiliations.keys():
                        supplemented_affiliations[article_link] = []
                    supplemented_affiliations[article_link].append((author, affiliations))                
                
                for article_link in selected_publication_map[conference][str(year)]:
                    paperIndex = hlta_paper_paperIndex_map[article_link]
                    if paperIndex in article_hltaCluster_map.keys():
                        clusters = set(article_hltaCluster_map[paperIndex]).intersection(set(clusterIDs))
                        clusterIndexes = [clusterID_clusterIndex_map[cluster] for cluster in clusters]
                        
                        
                        for eleTuple in article_links:
                                                            
                            if article_link == eleTuple['pdf_link']:
                                authors = eleTuple['authors']
                                
                                if authors.endswith('.'):
                                    authors = authors[:-1]
                                authors = authors.replace(' and ', ', ').lower()
                                authors = authors.split(', ')                                
                                affiliations = [eleTuple[1] for eleTuple in supplemented_affiliations[article_link]]
                                
                                data_repository[conference][year].append({'paperIndex':paperIndex,
                                                                          'clusterIndexes':clusterIndexes,
                                                                          'authors':authors,
                                                                          'num_citations':0,
                                                                          'affiliations':affiliations})
                                
                                if False:
                                    for author in authors:
                                        print('%s\t%s\t%s\t%s' % ('EDM-2019', article_link, eleTuple['title'], author))
                                      
                                
            elif str(year) in selected_publication_map[conference].keys():                
                article_metadata_mag_map = json.loads(open(data_path + conference + '/' + str(year) + '/article_metadata_mag_map', 'r').read()) 
                for article_link in selected_publication_map[conference][str(year)]:
                    paperIndex = hlta_paper_paperIndex_map[article_link]
                    if paperIndex in article_hltaCluster_map.keys():
                        clusters = set(article_hltaCluster_map[paperIndex]).intersection(set(clusterIDs))
                        clusterIndexes = [clusterID_clusterIndex_map[cluster] for cluster in clusters]
                        
                        if article_link in article_metadata_mag_map.keys():
                            metadata = article_metadata_mag_map[article_link][0]                            
                            authors = [eleTuple['AuN'] for eleTuple in metadata['AA']]
                            num_citations = metadata['CC']
                            
                            affiliations = []
                            for eleTuple in metadata['AA']:
                                if 'AfN' in eleTuple.keys():
                                    affiliations.append(eleTuple['AfN'])
                                else:
                                    affiliations.append(None)
                        else:
                            authors = []
                            affiliations = []
                            num_citations = 0
                        data_repository[conference][year].append({'paperIndex':paperIndex,
                                                                  'clusterIndexes':clusterIndexes,
                                                                  'authors':authors,
                                                                  'num_citations':num_citations,
                                                                  'affiliations':affiliations})
    
    return data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map
   

# def main():  
#     
#     data_path = '../data/'    
#     data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
#     
#     
# if __name__ == "__main__":
#     main()