'''
Created on 4 Jun 2019

@author: gche0022
'''

import os
import json
import time
import bibtexparser
from xml.etree import ElementTree
import http.client, urllib.request, urllib.parse, urllib.error, base64
from collections import defaultdict


def retrieve_fos(data_path):
    headers = {
        # Request headers
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': 'c10598fb715d4ee28a3025ba2cf52377',
    }
    
    mark = True    
    fosContainer = {'offset':0, 'fos':[]}
    if os.path.exists(data_path +'/mag_fos'):
        fosContainer = json.loads(open(data_path +'/mag_fos', 'r', encoding='utf-8').read())
    
    offset = fosContainer['offset']    
        
    while mark:        
        params = urllib.parse.urlencode({'expr':'Ty=\'6\'',
                                         'model':'latest',
                                         'count':1000,
                                         'offset':offset,
                                         'attributes':'Id,FN,DFN,CC,ECC,FL,FP.FN,FP.FId,FC.FN,FC.FId'})
        
        try:
            conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')      
            conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            
            if len(data['entities']) != 0:
                fosContainer['fos'] += data['entities']
            else:
                mark = False
                        
        except Exception as e:
            print('Offset is:\t%d' % offset)
            # print("[Errno {0}] {1}".format(e.errno, e.strerror))
            print(e)
            time.sleep(10)
            offset -= 1000
        
        offset += 1000
        
        fosContainer['offset'] = offset
        if offset > 10000 and offset % 10000 == 0:
            print(offset)
            outFile = open(data_path +'/mag_fos', 'w', encoding='utf-8')
            outFile.write(json.dumps(fosContainer))
            outFile.close()
            
    outFile = open(data_path +'/mag_fos', 'w', encoding='utf-8')
    outFile.write(json.dumps(fosContainer))
    outFile.close()


def check_fos_by_level(fos_list, level):
    fos_set = set()
    print("Level of concepts:\t%d" % level)
    for fos in fos_list:
        if fos['FL'] == level:
            fosName = fos['FN']
            if 'education' in fosName:
                # print(fosName)
                fos_set.add(fosName)
    print('# concepts:\t%d\n' % len(fos_set))
    return fos_set
        

def check_child_foss(fos_parent_children_map, target_fos):
    child_set = set()
    unchecked_fos_set = set()
    checked_fos_set = set()
    
    if target_fos in fos_parent_children_map.keys():
        checked_fos_set.add(target_fos)
        child_set.add(target_fos.lower())
        for child_fos in fos_parent_children_map[target_fos]:
            child_set.add(child_fos['FN'].lower())
            unchecked_fos_set.add(child_fos['FN'])
        
    while len(unchecked_fos_set) > 0:
        current_fos = unchecked_fos_set.pop()        
        if current_fos in fos_parent_children_map.keys():
            checked_fos_set.add(current_fos)
            child_set.add(current_fos.lower())
            if current_fos in fos_parent_children_map.keys():
                for child_fos in fos_parent_children_map[current_fos]:
                    child_set.add(child_fos['FN'].lower())
                    unchecked_fos_set.add(child_fos['FN'])
        
    # print("Target concept is:\t%s\t%d" % (target_fos, len(child_set)))
    # for fos in child_set:
    #     print(fos)
        
    return child_set
    
    

def check_fos(data_path):
    # Real the whole FoS structure
    fosContainer = json.loads(open(data_path +'/mag_fos', 'r', encoding='utf-8').read())
    fos_list = fosContainer['fos']
        
    # Extract the parent-children mapping relationship
    fos_parent_children_map = dict()
    fos_set = set()
    for fos in fos_list:
        fosName = fos['FN']
        
        # Test
        '''
        test_fos = 'educational data mining'
        test_fos = 'learning analytics'
        if fosName == test_fos:
            print(fos)
        '''
           
        fos_set.add(fosName)
        if 'FC' in fos.keys():
            fos_parent_children_map[fosName] = fos['FC']
    
    # Check how many concepts of a specific level contains "education"
    education_fos = check_fos_by_level(fos_list, 1)
    education_fos = education_fos.union(check_fos_by_level(fos_list, 2))
    
    # Check the child concepts of a specific concept
    # check_child_foss(fos_parent_children_map, 'educational research')
    
    # Retrieve all of the child fos of any L1/L2 fos that contains "education"
    selected_fos_set = set()
    for fos in education_fos:
        selected_fos_set = selected_fos_set.union(check_child_foss(fos_parent_children_map, fos))
    
    print("# ALL fos:\t%d\n" % len(fos_set))
    print("# SELECTED fos:\t%d\n" % len(selected_fos_set))
    # for fos in selected_fos_set:
    #     print(fos)   
    
    ############################################################################
    
    publication_keywords_map = defaultdict(int)
    
    # LAK
    conferences = ['LAK', 'LatS', 'AIED', 'ECTEL', 'EDM']
    conferences = ['LAK', 'EDM']
    for conference_name in conferences:
        conference_path = os.path.dirname(os.path.dirname(data_path)) + '/' + conference_name + '/'
        for year in os.listdir(conference_path):
            if year != '.DS_Store':
                
                # if int(year) < 2009:
                #     continue
                
                if conference_name in ['LAK', 'LatS']:
                    article_metadata_map = json.loads(open(conference_path + year + '/article_metadata_map', 'r', encoding='utf-8').read())                    
                    for article in article_metadata_map.keys():
                        bibtexText = article_metadata_map[article]['bibtex']
                        bib_data = bibtexparser.loads(bibtexText)
                        if 'keywords' in bib_data.entries[0].keys():
                            keywords = bib_data.entries[0]['keywords'].split(',')
                            for keyword in keywords:
                                publication_keywords_map[keyword.strip().lower()] += 1                            
                
                if conference_name in ['AIED', 'ECTEL']:
                    article_metadata_map = json.loads(open(conference_path + year + '/article_metadata_map', 'r', encoding='utf-8').read())
                    for article in article_metadata_map.keys():
                        if 'keywords' in article_metadata_map[article].keys():
                            keywords = article_metadata_map[article]['keywords']
                            for keyword in keywords:
                                publication_keywords_map[keyword.strip().lower()] += 1
                                
                if conference_name in ['EDM']:
                    articles = os.listdir(conference_path + year)
                    for article in articles:
                        if article.endswith('.tei.xml'):
                            tree = ElementTree.parse(conference_path + year + '/' + article)
                            
                            for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}term'):                                
                                keyword = element.text.replace('- ', '')
                                publication_keywords_map[keyword.strip().lower()] += 1                                   
                                
        # print("After including %s, # keywords:\t%d" % (conference_name, len(publication_keywords_set)))
    
    # Filter out keywords appearing for only once/twice
    # publication_keywords_map = {k:publication_keywords_map[k] for k in publication_keywords_map.keys() if publication_keywords_map[k] > 2}
        
    publication_keywords_set = publication_keywords_map.keys()
    
    print('')         
    print("# keywords in publication data is:\t%d" % len(publication_keywords_set))
           
    print('# overlapped keywords between SELECTED fos and publication keywords:\t%d' % len(selected_fos_set.intersection(publication_keywords_set)))
    print('# overlapped keywords between All fos and publication keywords:\t%d\n\n' % len(fos_set.intersection(publication_keywords_set))) 
    
    frequent_publication_keywords = set()
    k = 100
    sorted_publication_keywords_map = sorted(publication_keywords_map.items(), key=lambda x: x[1], reverse=True)
    for i in range(k):
        frequent_publication_keywords.add(sorted_publication_keywords_map[i][0])
        print("%s\t%d" % (sorted_publication_keywords_map[i][0], sorted_publication_keywords_map[i][1]))
        
    diff_keywords = frequent_publication_keywords - fos_set
    print("# diff keywords:\t%d" % len(diff_keywords))
    for keyword in diff_keywords:
        print(keyword)
    
    
def main():
    
    mag_name = 'mag'
    data_path = '../data/' + mag_name + '/'
    
    # Create data folder
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    
    # Step 1: retrieve field of study entities
    # retrieve_fos(data_path)
    
    # Step 2: Manually check L1/L2 concepts
    check_fos(data_path)
    
         
   
if __name__ == "__main__":
    main()