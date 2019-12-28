'''
Created on 13 Jun 2019

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



def crawl_article_mag_metadata(data_path):
    headers = {
        # Request headers
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': 'ba67acf5f05f4825ba36973bf981ae6e',
    }
    
    title_map = {'Learning analytics in outer space: a Hidden Naïve Bayes model for automatic student off-task behavior detection':'learning analytics in outer space a hidden naive bayes model for automatic student off task behavior detection',
                 'What to do with actionable intelligence: E2Coach as an intervention engine':'what to do with actionable intelligence e 2 coach as an intervention engine',
                 'DCLA13: 1st International Workshop on Discourse-Centric Learning Analytics':'dcla13 1 st international workshop on discourse centric learning analytics',
                 'The 3rd LAK data competition':'the 3 rd lak data competition',
                 '1st International Workshop on Learning Analytics and Linked Data':'1 st international workshop on learning analytics and linked data',
                 'Beyond failure: the 2nd LAK Failathon':'beyond failure the 2 nd lak failathon',
                 '2nd cross-LAK: learning analytics across physical and digital spaces':'2 nd cross lak learning analytics across physical and digital spaces',
                 'Beyond failure: the 2nd LAK Failathon poster':'beyond failure the 2 nd lak failathon poster'}
                
    conferences = ['LAK', 'EDM']
    for conference_name in conferences:
        conference_path = data_path + conference_name + '/'
        for year in os.listdir(conference_path):
            if year != '.DS_Store':
                print('---- %s\t%s ----' % (conference_name, year))
                # Metadata repository
                article_links = json.loads(open(conference_path + year + '/article_links', 'r').read())
                
                # MAG Metadata repository
                if not os.path.exists(conference_path + year + '/article_metadata_mag_map'):
                    article_metadata_mag_map = dict()
                else:
                    article_metadata_mag_map = json.loads(open(conference_path + year + '/article_metadata_mag_map', 'r', encoding='utf-8').read())               
                
                if conference_name == 'LAK':
                    for [title,link] in article_links:
                        if link not in article_metadata_mag_map.keys():
                            if title in title_map.keys():
                                query_title = title_map[title]
                            else:
                                query_title = re.sub('[^A-Za-z0-9]+', ' ', title.lower())
                                while "  " in query_title:
                                    query_title = query_title.replace("  ", " ")
                                query_title = query_title.strip()
                            
                            params = urllib.parse.urlencode({'expr':'Ti==\'' + query_title + '\'',
                                                             'model':'latest',
                                                             'attributes':'Id,Ti,L,Y,D,CC,ECC,AA.AuN,AA.AuId,AA.AfN,AA.AfId,AA.S,F.FN,F.FId,J.JN,J.JId,C.CN,C.CId,RId,W,E'})
                    
                            try:
                                conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')      
                                conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
                                response = conn.getresponse()
                                data = json.loads(response.read())
                                conn.close()
                                
                                if len(data['entities']) != 0:
                                    article_metadata_mag_map[link] = data['entities']
                                else:
                                    print(query_title)
                                    print(title + '\n')
                                            
                            except Exception as e:                         
                                # print("[Errno {0}] {1}".format(e.errno, e.strerror))
                                print(e)
                                print(query_title)
                                print(title + '\n')
                                time.sleep(5)
                                
                        if len(article_metadata_mag_map.keys()) % 10 == 0:
                            outFile = open(conference_path + year + '/article_metadata_mag_map', 'w', encoding='utf-8')
                            outFile.write(json.dumps(article_metadata_mag_map))
                            outFile.close()
                                
                if conference_name == 'EDM':
                    for articleTuple in article_links:
                        link = articleTuple['pdf_link']
                        title = articleTuple['title']
                        
                        if link not in article_metadata_mag_map.keys():
                            if title in title_map.keys():
                                query_title = title_map[title]
                            else:
                                query_title = re.sub('[^A-Za-z0-9]+', ' ', title.lower())
                                while "  " in query_title:
                                    query_title = query_title.replace("  ", " ")
                                query_title = query_title.strip()
                            
                            params = urllib.parse.urlencode({'expr':'Ti==\'' + query_title + '\'',
                                                             'model':'latest',
                                                             'attributes':'Id,Ti,L,Y,D,CC,ECC,AA.AuN,AA.AuId,AA.AfN,AA.AfId,AA.S,F.FN,F.FId,J.JN,J.JId,C.CN,C.CId,RId,W,E'})
                            
                            try:
                                conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')      
                                conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
                                response = conn.getresponse()
                                data = json.loads(response.read())
                                conn.close()
                                
                                if len(data['entities']) != 0:
                                    article_metadata_mag_map[link] = data['entities']
                                else:
                                    print(query_title)
                                    print(link)
                                    print(title + '\n')
                                            
                            except Exception as e:                         
                                # print("[Errno {0}] {1}".format(e.errno, e.strerror))
                                print(e)
                                print(data)
                                print(link)
                                print(query_title)
                                print(title + '\n')
                                time.sleep(5)                 
                
                        if len(article_metadata_mag_map.keys()) % 10 == 0:
                            outFile = open(conference_path + year + '/article_metadata_mag_map', 'w', encoding='utf-8')
                            outFile.write(json.dumps(article_metadata_mag_map))
                            outFile.close()
        
                outFile = open(conference_path + year + '/article_metadata_mag_map', 'w', encoding='utf-8')
                outFile.write(json.dumps(article_metadata_mag_map))
                outFile.close()
                    

def main():  
    
    data_path = '../data/'
    crawl_article_mag_metadata(data_path)
         
   
if __name__ == "__main__":
    main()