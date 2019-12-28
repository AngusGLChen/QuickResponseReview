'''
Created on 15 Aug 2019

@author: gche0022
'''

import os
import re
import json
import time
import bibtexparser
from xml.etree import ElementTree
from collections import defaultdict
import http.client, urllib.request, urllib.parse, urllib.error, base64
from LAK_EDM.functions import read_selected_data



def crawl_author_mag_metadata(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_mag_metadata_' + '_'.join(conferences)):
        author_mag_metadata_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_mag_metadata_' + '_'.join(conferences), 'r', encoding='utf-8').read())
    else:
        author_mag_metadata_map = dict()
        
    headers = {
        # Request headers
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': 'ba67acf5f05f4825ba36973bf981ae6e',
    }
        
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:
                    if author not in author_mag_metadata_map.keys():                        
                        params = urllib.parse.urlencode({'expr':'AuN==\'' + author + '\'',
                                                         'model':'latest',
                                                         'attributes':'Id,AuN,DAuN,CC,ECC,E'})
                    
                        try:
                            conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')      
                            conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
                            response = conn.getresponse()
                            data = json.loads(response.read())
                            conn.close()
                            
                            if len(data['entities']) != 0:
                                author_mag_metadata_map[author] = data['entities']
                            else:
                                print(author)
                                                                 
                        except Exception as e:                         
                            # print("[Errno {0}] {1}".format(e.errno, e.strerror))
                            print(e)
                            print(author + '\n')
                            time.sleep(5)
                        
                        time.sleep(1)                     
                
                    if len(author_mag_metadata_map.keys()) % 10 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_mag_metadata_' + '_'.join(conferences), 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_mag_metadata_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_mag_metadata_' + '_'.join(conferences), 'w', encoding='utf-8')
    outfile.write(json.dumps(author_mag_metadata_map))
    outfile.close()
    
       

def main():  
    
    data_path = '../data/'
    crawl_author_mag_metadata(data_path)
         
   
if __name__ == "__main__":
    main()