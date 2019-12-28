'''
Created on 12 Aug 2019

@author: gche0022
'''


import json
import numpy
import random


import pandas as pd
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d

import time
import requests
from genderize import Genderize
import os
from _collections import defaultdict

import skbio
from LAK_EDM.functions import read_selected_data
import csv



# font = {'family' : 'normal',
#         'size'   : 12}
# plt.rc('font', **font)

   
def predict_author_gender_v1(data_path):
    
    # Predict authors' gender by using genderize.io
    # https://genderize.io/
    # Results: Male      1158    58.84
    #          Female     618    31.40
    #          Others     192     9.76
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v1', 'r', encoding='utf-8').read())
    
    genderize = Genderize(user_agent='GenderizeDocs/0.0',
                          api_key='5073167594a6a377efe12e4b35fef87e',
                          timeout=5.0)
    
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                        
                    name = author.split()[0]                        
                    
                    if author not in author_gender_map.keys():                        
                        try:
                            predictedGender = genderize.get([name])                            
                            predictedGender = predictedGender[0]['gender']                                           
                            if predictedGender == 'male':
                                predictedGender = 'Male'
                            elif predictedGender == 'female':
                                predictedGender = 'Female'
                            else:
                                predictedGender = 'Others'                            
                            author_gender_map[author] = predictedGender
                        except Exception as e:
                            print(e)
                            print(predictedGender)                        
                
                    if len(author_gender_map.keys()) % 20 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v1', 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_gender_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v1', 'w', encoding='utf-8')
    outfile.write(json.dumps(author_gender_map))
    outfile.close()
    
    gender_author_map = {'Male':0, 'Female':0, 'Others':0}
    for author in author_gender_map.keys():
        predictedGender = author_gender_map[author]
        gender_author_map[predictedGender] += 1
    print('Gender prediction:')
    for predictedGender in gender_author_map.keys():
        print('%s\t%d\t%.2f' % (predictedGender, gender_author_map[predictedGender], gender_author_map[predictedGender] / float(len(author_gender_map.keys())) * 100))                     


def predict_author_gender_v2(data_path):
    
    # Predict authors' gender by using NamSor
    # /api2/json/genderFull/{fullName}
    # Results: Male    1428    72.56
    #          Female   540    27.44
    #          Others     0     0.00   
        
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
        
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2'):
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + ' '.join(conferences) + '_v2', 'r', encoding='utf-8').read())
    else:
        author_gender_map = dict()
        
    headers = {'accept': 'application/json',
               'X-API-KEY': '71d1a89bdf5182d6d00cdbe60253f779'
               } 
    
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:
                    
                    if author not in author_gender_map.keys():               
                        try:
                            link = 'https://v2.namsor.com/NamSorAPIv2/api2/json/genderFull/' + author                                                       
                            r = requests.get(link, headers=headers)                                                        
                            predictedGender = r.json()['likelyGender']                     
                                                                       
                            if predictedGender == 'male':
                                predictedGender = 'Male'
                            elif predictedGender == 'female':
                                predictedGender = 'Female'
                            else:
                                predictedGender = 'Others'                            
                            author_gender_map[author] = predictedGender
                        except Exception as e:
                            print(e)
                            print(predictedGender)                        
                
                    if len(author_gender_map.keys()) % 20 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2', 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_gender_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2', 'w', encoding='utf-8')
    outfile.write(json.dumps(author_gender_map))
    outfile.close()
    
    gender_author_map = {'Male':0, 'Female':0, 'Others':0}
    for author in author_gender_map.keys():
        predictedGender = author_gender_map[author]
        gender_author_map[predictedGender] += 1
    print('Gender prediction:')
    for predictedGender in gender_author_map.keys():
        print('%s\t%d\t%.2f' % (predictedGender, gender_author_map[predictedGender], gender_author_map[predictedGender] / float(len(author_gender_map.keys())) * 100))                     


def analyze_author_gender(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    def analyze_author_gender_number(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = {'Male':set(), 'Female':set(), 'Others':set()}
        
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v1', 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        try:                       
                            predictedGender = author_gender_map[author]
                            plotValue_map[conference][year][predictedGender].add(author)
                        except:
                            plotValue_map[conference][year]['Others'].add(author)
        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
        
        genderTypes = ['Male', 'Female', 'Others']
        colors = ['#ff5858', '#ffdd67', '#a4d7e1']
        
        # genderTypes = ['Male', 'Female']
        # colors = ['#ff5858', '#ffdd67']
        
        for conference in conferences:
            for i in range(len(genderTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                for j in range(i):
                    for year in years:
                        bottom_array[year-2008] += len(plotValue_map[conference][year][genderTypes[j]])
                
                for year in years:
                    valueArray.append(len(plotValue_map[conference][year][genderTypes[i]]))
                
                if conference == 'LAK':
                    plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.4, linewidth=0.5, label=genderTypes[i], edgecolor='#444444', bottom=bottom_array)
                if conference == 'EDM':
                    plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.4, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                
        # x-axis labels
        updated_labels = []
        for year in years:
            if year < 2011:
                updated_labels.append("      EDM\n" + str(year))
            else:
                updated_labels.append("LAK EDM\n" + str(year))
        plt.xticks(x_pos, updated_labels)
        
        # Display percentages
        for conference in conferences:     
            for year in years:
                for genderType in genderTypes:
                    plotValue_map[conference][year][genderType] = len(plotValue_map[conference][year][genderType])
        
        threshold = 10
        for conference in conferences:     
            for year in years:
                total = 0
                for i in range(len(genderTypes)):
                    total += plotValue_map[conference][year][genderTypes[i]]
                if total > 0:
                    for i in range(len(genderTypes)):                        
                        y = sum([plotValue_map[conference][year][genderTypes[j]] for j in range(i)]) + plotValue_map[conference][year][genderTypes[i]] - 7
                        value = plotValue_map[conference][year][genderTypes[i]]
                        
                        if conference == 'LAK':
                            if value >= 100:
                                x = year - 2008 - 0.35
                            else:
                                x = year - 2008 - 0.32
                        if conference == 'EDM':
                            if value >= 100:
                                x = year - 2008 + 0.05
                            else:
                                x = year - 2008 + 0.10
                        
                        if value >= threshold:
                            plt.text(x, y, value, fontsize=9)
                            
        plt.ylabel('# Authors')        
        plt.legend()
        
        title = 'Researcher gender distribution.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
             
    # analyze_author_gender_number(data_repository)
    
    
    def analyze_author_genderDiversity_whole(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = {'Male':set(), 'Female':set(), 'Others':set()}
        
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2', 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:                        
                        try:                       
                            predictedGender = author_gender_map[author]
                            plotValue_map[conference][predictedGender].add(author)
                        except:
                            plotValue_map[conference]['Others'].add(author)
                
        
        genderTypes = ['Male', 'Female']
        for conference in conferences:
            for genderType in genderTypes:
                plotValue_map[conference][genderType] = len(plotValue_map[conference][genderType])
    
        for conference in conferences:
            diversityScore = skbio.diversity.alpha.simpson([plotValue_map[conference]['Male'],
                                                            plotValue_map[conference]['Female']])
            print('%s\t%.4f' % (conference, diversityScore))
            
    # analyze_author_genderDiversity_whole(data_repository)
    
    def analyze_author_gender_ratio_allTopics(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = {'Male':set(), 'Female':set(), 'Others':set()}
        
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2', 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:                        
                        try:                       
                            predictedGender = author_gender_map[author]
                            plotValue_map[conference][year][predictedGender].add(author)
                        except:
                            plotValue_map[conference][year]['Others'].add(author)
                
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
        genderTypes = ['Male', 'Female']
        
        # x-axis labels
        plt.xticks(x_pos, [str(year) for year in years])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:     
            for year in years:
                for genderType in genderTypes:
                    plotValue_map[conference][year][genderType] = len(plotValue_map[conference][year][genderType])
        
        for conference in conferences:
            valueArray = []     
            for year in years:                
                diversityScore = skbio.diversity.alpha.simpson([plotValue_map[conference][year]['Male'],
                                                                plotValue_map[conference][year]['Female']])
                valueArray.append(diversityScore)
                
            print('\t'.join([str(ele) for ele in valueArray]))
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'Female vs. male diversity (All topics).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    # analyze_author_gender_ratio_allTopics(data_repository)
            
    def analyze_author_gender_ratio_subTopics(data_repository):
        
        clusterNames = ['Predictive & Descriptive Analytics',
                        'Engagement Patterns & Resource Use',
                        'Multimodal LA & Collaborative Learning',
                        'Knowledge & Skill Modeling',
                        'Recommender Systems & LA Adoption',
                        'Effects on Teaching & Learning Practices',
                        'Reading & Writing Analytics',
                        'MOOCs & Social Learning',
                        'Assessment',
                        'Study Strategies',
                        'Affect Modeling']
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for i in range(len(clusterNames)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = dict()
                for year in years:
                    plotValue_map[i][conference][year] = {'Male':set(), 'Female':set(), 'Others':set()}
        
        # Gather authors' gender information
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v2', 'r', encoding='utf-8').read())          
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    authors = eleTuple['authors']                                          
                    for author in authors:
                        # predictedGender = author_gender_map[author]                        
                        # for clusterIndex in clusterIndexes:
                        #     plotValue_map[clusterIndex][conference][year][predictedGender].add(author)
                            
                        try:                       
                            predictedGender = author_gender_map[author]
                            for clusterIndex in clusterIndexes:
                                plotValue_map[clusterIndex][conference][year][predictedGender].add(author)
                        except:
                            plotValue_map[clusterIndex][conference][year]['Others'].add(author)
                
                
        # Plot -----------------------------------------------------------------
        genderTypes = ['Male', 'Female']
        
        # Line plot ------------------------------------------------------------
        for i in range(len(clusterNames)):
            for conference in conferences:
                for year in years:
                    for genderType in genderTypes:
                        plotValue_map[i][conference][year][genderType] = len(plotValue_map[i][conference][year][genderType])
        
        for i in range(len(clusterNames)):
            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
        
            for conference in conferences:
                valueArray = []     
                for year in years:
                    diversityScore = skbio.diversity.alpha.simpson([plotValue_map[i][conference][year]['Male'],
                                                                    plotValue_map[i][conference][year]['Female']])
                    
                    valueArray.append(diversityScore)
                    
                print('\t'.join([str(ele) for ele in valueArray]))
                                    
                if conference == 'LAK':
                    x_positions = x_pos[3:]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                    plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
                if conference == 'EDM':
                    x_positions = x_pos
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray, kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                    plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                                
            # x-axis labels
            plt.xticks(x_pos, [str(year) for year in years])
            plt.legend()
            
            title = 'Female vs. male diversity (' + clusterNames[i] + ').png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                         
            plt.show()    
     
    analyze_author_gender_ratio_subTopics(data_repository)      

'''
def predict_author_regionOriginNamSor(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_regionOriginNamSor_' + '_'.join(conferences)):
        author_regionOrigin_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_regionOriginNamSor_' + '_'.join(conferences), 'r', encoding='utf-8').read())
    else:
        author_regionOrigin_map = dict()
        
    headers = {'accept': 'application/json',
               'X-API-KEY': '5ce43ddc8d386a06c88e677145102a76'
               }
    
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                        
                    name = author['AuN'].split()                      
                    
                    if author['AuN'] not in author_regionOrigin_map.keys():                        
                        try:
                            link = 'https://v2.namsor.com/NamSorAPIv2/api2/json/origin/' + name[0] + '/' + name[-1]                                                      
                            r = requests.get(link, headers=headers)                              
                            author_regionOrigin_map[author['AuN']] = r.json()
                        except:
                            print(r)                        
                
                    if len(author_regionOrigin_map.keys()) % 10 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_regionOriginNamSor_' + '_'.join(conferences), 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_regionOrigin_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_regionOriginNamSor_' + '_'.join(conferences), 'w', encoding='utf-8')
    outfile.write(json.dumps(author_regionOrigin_map))
    outfile.close()
    
    # Analyze results
    regionOrign_set = set()
    for author in author_regionOrigin_map.keys():
        regionOrign_set.add(author_regionOrigin_map[author]['regionOrigin'])    
    print(regionOrign_set)
    

def predict_author_RaceEthnicityNamSor(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_raceEthnicityNamSor_' + '_'.join(conferences)):
        author_raceEthnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_raceEthnicityNamSor_' + '_'.join(conferences), 'r', encoding='utf-8').read())
    else:
        author_raceEthnicity_map = dict()
        
    headers = {'accept': 'application/json',
               'X-API-KEY': '98a72909c1e9ee84787e579e6d8499a6'
               }
    
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                        
                    name = author['AuN'].split()                      
                    
                    if author['AuN'] not in author_raceEthnicity_map.keys():                        
                        try:
                            link = 'https://v2.namsor.com/NamSorAPIv2/api2/json/usRaceEthnicity/' + name[0] + '/' + name[-1]                                                      
                            r = requests.get(link, headers=headers)                              
                            author_raceEthnicity_map[author['AuN']] = r.json()
                        except:
                            print(r)                        
                
                    if len(author_raceEthnicity_map.keys()) % 10 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_raceEthnicityNamSor_' + '_'.join(conferences), 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_raceEthnicity_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_raceEthnicityNamSor_' + '_'.join(conferences), 'w', encoding='utf-8')
    outfile.write(json.dumps(author_raceEthnicity_map))
    outfile.close()
    
    # Analyze results
    raceEthnicity_count_map = defaultdict(int)
    for author in author_raceEthnicity_map.keys():
        raceEthnicity = author_raceEthnicity_map[author]['raceEthnicity']
        raceEthnicity_count_map[raceEthnicity] += 1
    for raceEthnicity in raceEthnicity_count_map.keys():
        print('%s\t%d\t%.2f' % (raceEthnicity, raceEthnicity_count_map[raceEthnicity], raceEthnicity_count_map[raceEthnicity] / float(len(author_raceEthnicity_map.keys())) * 100))                     


def analyze_author_raceEthnicity(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    def analyze_author_raceEthnicity_fraction(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        raceMapping = {'W_NL':'White',
                       'A':'Asian',
                       'HL':'Hispanic & Latino',
                       'B_NL':'Black'
                       }
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for key in raceMapping.keys():
                    plotValue_map[conference][year][raceMapping[key]] = set()
        
        author_raceEthnicity_map = json.loads(open(data_path + 'author_raceEthnicityNamSor_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:                        
                        predictedRaceEthnicity = raceMapping[author_raceEthnicity_map[author['AuN']]['raceEthnicity']]                
                        plotValue_map[conference][year][predictedRaceEthnicity].add(author['AuN'])
                        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                
        raceEthnicityTypes = [raceMapping[key] for key in raceMapping.keys()]
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff']
        
        for conference in conferences:
            for i in range(len(raceEthnicityTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                for j in range(i):
                    for year in years:
                        bottom_array[year-2008] += plotValue_map[conference][year][raceEthnicityTypes[j]]
                
                for year in years:
                    valueArray.append(plotValue_map[conference][year][raceEthnicityTypes[i]])
                
                if conference == 'LAK':
                    plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.4, linewidth=0.5, label=raceEthnicityTypes[i], edgecolor='#444444', bottom=bottom_array)
                if conference == 'EDM':
                    plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.4, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                
        
        # x-axis labels
        updated_labels = []
        for year in years:
            if year < 2011:
                updated_labels.append("      EDM\n" + str(year))
            else:
                updated_labels.append("LAK EDM\n" + str(year))
        plt.xticks(x_pos, updated_labels)
        
        # Display percentages        
        threshold = 10
        for conference in conferences:     
            for year in years:
                total = 0
                for i in range(len(raceEthnicityTypes)):
                    total += plotValue_map[conference][year][raceEthnicityTypes[i]]
                if total > 0:
                    for i in range(len(raceEthnicityTypes)):                        
                        y = sum([plotValue_map[conference][year][raceEthnicityTypes[j]] for j in range(i)]) + plotValue_map[conference][year][raceEthnicityTypes[i]] - 3
                        value = int(plotValue_map[conference][year][raceEthnicityTypes[i]])
                        
                        if conference == 'LAK':
                            if value >= 100:
                                x = year - 2008 - 0.35
                            else:
                                x = year - 2008 - 0.32
                        if conference == 'EDM':
                            if value >= 100:
                                x = year - 2008 + 0.05
                            else:
                                x = year - 2008 + 0.10
                        
                        if value >= threshold:
                            plt.text(x, y, value, fontsize=9)
                            
        plt.ylabel('% Authors')        
        plt.legend()
        
        title = 'Fraction of authors of different RaceEthinicity.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
                
    # analyze_author_raceEthnicity_fraction(data_repository)
        
    def analyze_author_raceEthinicityDiversity_allTopics(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        raceMapping = {'W_NL':'White',
                       'A':'Asian',
                       'HL':'Hispanic & Latino',
                       'B_NL':'Black'
                       }
        
        raceEthnicityTypes = [raceMapping[key] for key in raceMapping.keys()]
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for key in raceMapping.keys():
                    plotValue_map[conference][year][raceMapping[key]] = set()
        
        author_raceEthnicity_map = json.loads(open(data_path + 'author_raceEthnicityNamSor_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:                        
                        predictedRaceEthnicity = raceMapping[author_raceEthnicity_map[author['AuN']]['raceEthnicity']]                
                        plotValue_map[conference][year][predictedRaceEthnicity].add(author['AuN'])
                        
        for conference in conferences:
            for year in years:
                for key in plotValue_map[conference][year].keys():
                    plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key])
                                                    
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                
        # x-axis labels
        plt.xticks(x_pos, [str(year) for year in years])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:
            valueArray = []     
            for year in years:
                distribution_array = []
                for raceEthnicityType in raceEthnicityTypes:
                    distribution_array.append(plotValue_map[conference][year][raceEthnicityType])
                if sum(distribution_array) > 0:
                    diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                    valueArray.append(diversityScore)
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos[:-1]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'RaceEthinicity diversity (All topics).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    analyze_author_raceEthinicityDiversity_allTopics(data_repository)
    
    
    def analyze_author_raceEthinicityDiversity_subTopics(data_repository):
        
        clusterNames = ['Predictive & Descriptive Analytics',
                        'Engagement Patterns & Resource Use',
                        'Multimodal LA & Collaborative Learning',
                        'Knowledge & Skill Modeling',
                        'Recommender Systems & LA Adoption',
                        'Effects on Teaching & Learning Practices',
                        'Reading & Writing Analytics',
                        'MOOCs & Social Learning',
                        'Assessment',
                        'Study Strategies',
                        'Affect Modeling']
        
        raceMapping = {'W_NL':'White',
                       'A':'Asian',
                       'HL':'Hispanic & Latino',
                       'B_NL':'Black'
                       }
        
        raceEthnicityTypes = [raceMapping[key] for key in raceMapping.keys()]
        
        author_raceEthnicity_map = json.loads(open(data_path + 'author_raceEthnicityNamSor_' + '_'.join(conferences), 'r', encoding='utf-8').read())
                
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for i in range(len(clusterNames)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = dict()
                for year in years:
                    plotValue_map[i][conference][year] = dict()
                    for key in raceMapping.keys():
                        plotValue_map[i][conference][year][raceMapping[key]] = set()
                    
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    authors = eleTuple['authors']                                          
                    for author in authors: 
                        predictedRaceEthnicity = raceMapping[author_raceEthnicity_map[author['AuN']]['raceEthnicity']]                     
                        for clusterIndex in clusterIndexes:
                            plotValue_map[clusterIndex][conference][year][predictedRaceEthnicity].add(author['AuN'])
                
        # Plot -----------------------------------------------------------------
                
        # Line plot ------------------------------------------------------------
        for i in range(len(clusterNames)):
            for conference in conferences:
                for year in years:
                    for raceEthnicityType in raceEthnicityTypes:
                        plotValue_map[i][conference][year][raceEthnicityType] = len(plotValue_map[i][conference][year][raceEthnicityType])
        
        for i in range(len(clusterNames)):
            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
        
            for conference in conferences:
                valueArray = []     
                for year in years:
                    distribution_array = []                    
                    for raceEthnicityType in raceEthnicityTypes:
                        distribution_array.append(plotValue_map[i][conference][year][raceEthnicityType])
                    if sum(distribution_array) > 0:
                        diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                        valueArray.append(diversityScore)
                    else:
                        valueArray.append(0)                
                
                if conference == 'LAK':
                    x_positions = x_pos[3:]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                    plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
                if conference == 'EDM':
                    x_positions = x_pos[:-1]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[:-1], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                    plt.scatter(x_positions, valueArray[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
            # x-axis labels
            plt.xticks(x_pos, [str(year) for year in years])
            plt.legend()
            
            title = 'RaceEthinicity diversity (' + clusterNames[i] + ').png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + title, bbox_inches='tight', pad_inches = 0.05)
                         
            plt.show()
        
    analyze_author_raceEthinicityDiversity_subTopics(data_repository)
'''


def predict_author_nationalityNamePrism(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences)):
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
    else:
        author_nationality_map = dict()
        
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:
                    if author not in author_nationality_map.keys():                        
                        try:
                            link = 'http://www.name-prism.com/api_token/nat/json/a8bf670d77b1d810/' + author.replace(' ', '%20')
                            r = requests.get(link)                              
                            author_nationality_map[author] = r.json()
                        except:
                            print(r)
                            
                        time.sleep(1)                     
                
                    if len(author_nationality_map.keys()) % 10 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_nationality_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'w', encoding='utf-8')
    outfile.write(json.dumps(author_nationality_map))
    outfile.close()
    
    # Analyze results    
    nationality_count_map = defaultdict(int)
    for author in author_nationality_map.keys():
        sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
        nationality = sorted_tuple[0][0].split(',')[0]
        nationality_count_map[nationality] += 1
    for nationality in nationality_count_map.keys():
        print('%s\t%d\t%.2f' % (nationality, nationality_count_map[nationality], nationality_count_map[nationality] / float(len(author_nationality_map.keys())) * 100))                     
    

def analyze_author_nationality(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
        
    def analyze_author_nationality_fraction_all(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        # Nationality value set
        nationalityTypes = ['CelticEnglish', 'European', 'EastAsian', 'Hispanic', 'SouthAsian',
                            'Muslim', 'Greek', 'Nordic', 'African', 'Jewish']
        
        nationality_index_map = dict()
        for i in range(len(nationalityTypes)):
            nationality_index_map[nationalityTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for nationality in nationalityTypes:
                plotValue_map[conference][nationality] = set()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_nationality_map.keys():
                            sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            nationality = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][nationality].add(author)
        
        # Normalization
        for conference in conferences:            
            totalCount = 0
            for key in plotValue_map[conference].keys():                    
                totalCount += len(plotValue_map[conference][key])
            for key in plotValue_map[conference].keys():
                if totalCount > 0:
                    plotValue_map[conference][key] = len(plotValue_map[conference][key]) / float(totalCount) * 100
                else:
                    plotValue_map[conference][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(nationalityTypes)))
            
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5']
                    
        # Extract data
            
        for conference in conferences:
            valueArray = []
            for nationality in nationalityTypes:
                valueArray.append(plotValue_map[conference][nationality])
                
            # LAK
            if conference == 'LAK':                
                plt.bar(x_pos, valueArray, align='edge', color='#ff5858', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#ffdd67', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        plt.xticks(x_pos, nationalityTypes)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend()
        
        title = 'Fraction of authors of different nationalities (All).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    # analyze_author_nationality_fraction_all(data_repository)
        
    def analyze_author_nationality_fraction_by_years(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        # Nationality value set
        nationalityTypes = ['CelticEnglish', 'European', 'EastAsian', 'Hispanic', 'SouthAsian',
                            'Muslim', 'Greek', 'Nordic', 'African', 'Jewish']
        
        nationality_index_map = dict()
        for i in range(len(nationalityTypes)):
            nationality_index_map[nationalityTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for nationality in nationalityTypes:
                    plotValue_map[conference][year][nationality] = set()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_nationality_map.keys():
                            sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            nationality = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][year][nationality].add(author)
        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
        
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5']
                
        # Extract data
        updated_plotValue_map = dict()
        for conference in conferences:
            updated_plotValue_map[conference] = dict()
            for year in years:
                updated_plotValue_map[conference][year] = sorted(plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                        
        # LAK
        for j in range(len(nationalityTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['LAK'][year][k][1]                    
                valueArray.append(updated_plotValue_map['LAK'][year][j][1])                    
                colorArray.append(colors[nationality_index_map[updated_plotValue_map['LAK'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=nationalityTypes[j], edgecolor='#444444', bottom=bottom_array)
        
        # EDM
        for j in range(len(nationalityTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['EDM'][year][k][1]
                valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                colorArray.append(colors[nationality_index_map[updated_plotValue_map['EDM'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                    
        # x-axis labels
        updated_labels = []
        for year in years:
            if year < 2011:
                updated_labels.append("      EDM\n" + str(year))
            else:
                updated_labels.append("LAK EDM\n" + str(year))
        plt.xticks(x_pos, updated_labels)
        
        # Display percentages
        threshold = 10
        # LAK        
        for year in years:
            for j in range(len(nationalityTypes)):
                x = year - 2008 - 0.27
                y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                percentage = int(updated_plotValue_map['LAK'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        for year in years:
            for j in range(len(nationalityTypes)):
                x = year - 2008 + 0.03
                y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                percentage = int(updated_plotValue_map['EDM'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        '''          
        # LAK
        x_positions = [x-0.15 for x in x_pos][3:]
        y_positions = []
        for year in range(2011,2020):
            index = None
            for j in range(len(updated_plotValue_map['LAK'][year])):
                if updated_plotValue_map['LAK'][year][j][0] == targetNationality:
                    index = j
            y_positions.append(sum([updated_plotValue_map['LAK'][year][k][1] for k in range(index)]) + updated_plotValue_map['LAK'][year][index][1] / 2)
        
        x_positions.append(x_positions[-1] + 0.7)
        y_positions.append(y_positions[-1])            
        plt.text(x_positions[-1]+0.13, y_positions[-1]-1, 'LAK')
        
        x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
        f = interp1d(x_positions, y_positions, kind='quadratic')
        y_smooth = f(x_new)
        
        plt.plot(x_new, y_smooth, color='#444444')
        plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)    
        
        # EDM
        x_positions = [x+0.15 for x in x_pos]
        y_positions = []
        for year in years:
            index = None
            for j in range(len(updated_plotValue_map['EDM'][year])):
                if updated_plotValue_map['EDM'][year][j][0] == targetNationality:
                    index = j
            y_positions.append(sum([updated_plotValue_map['EDM'][year][k][1] for k in range(index)]) + updated_plotValue_map['EDM'][year][index][1] / 2)
        
        x_positions.append(x_positions[-1] + 0.4)
        y_positions.append(y_positions[-1])            
        plt.text(x_positions[-1]+0.1, y_positions[-1]+0.4, 'EDM') 
        
        x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
        f = interp1d(x_positions, y_positions, kind='quadratic')
        y_smooth = f(x_new)
        plt.plot(x_new, y_smooth, linestyle='dashed', color='#444444')
        plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
        '''
                    
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=5, mode="expand", borderaxespad=0.)
        
        title = 'Fraction of authors of different nationalities (By years).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()        
                
    # analyze_author_nationality_fraction_by_years(data_repository)
        
    def analyze_author_nationalityDiversity_whole(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        nationalityTypes = ['CelticEnglish', 'European', 'EastAsian', 'Hispanic', 'SouthAsian',
                            'Muslim', 'Greek', 'Nordic', 'African', 'Jewish']
        
        for conference in conferences:
            plotValue_map[conference] = dict()            
            for nationality in nationalityTypes:
                plotValue_map[conference][nationality] = set()
        
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_nationality_map.keys():
                            sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            nationality = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][nationality].add(author)
        
        for conference in conferences:
            for nationality in plotValue_map[conference].keys():
                plotValue_map[conference][nationality] = len(plotValue_map[conference][nationality])
                                                    
        for conference in conferences:            
            distribution_array = []
            for nationalityType in nationalityTypes:
                distribution_array.append(plotValue_map[conference][nationalityType])
            diversityScore = skbio.diversity.alpha.simpson(distribution_array)
            
            print('%s\t%.4f' % (conference, diversityScore))
            
    # analyze_author_nationalityDiversity_whole(data_repository)
        
    def analyze_author_nationalityDiversity_allTopics(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        nationalityTypes = ['CelticEnglish', 'European', 'EastAsian', 'Hispanic', 'SouthAsian',
                            'Muslim', 'Greek', 'Nordic', 'African', 'Jewish']
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for nationality in nationalityTypes:
                    plotValue_map[conference][year][nationality] = set()
        
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_nationality_map.keys():
                            sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            nationality = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][year][nationality].add(author)
        
        for conference in conferences:
            for year in years:
                for nationality in plotValue_map[conference][year].keys():
                    plotValue_map[conference][year][nationality] = len(plotValue_map[conference][year][nationality])
                                                    
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                
        # x-axis labels
        plt.xticks(x_pos, [str(year) for year in years])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:
            valueArray = []     
            for year in years:
                distribution_array = []
                for nationalityType in nationalityTypes:
                    distribution_array.append(plotValue_map[conference][year][nationalityType])
                
                diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                valueArray.append(diversityScore)
                    
            print('\t'.join([str(ele) for ele in valueArray]))
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'Nationality diversity (All topics).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    # analyze_author_nationalityDiversity_allTopics(data_repository)
        
    def analyze_author_nationalityDiversity_subTopics(data_repository):
        
        clusterNames = ['Predictive & Descriptive Analytics',
                        'Engagement Patterns & Resource Use',
                        'Multimodal LA & Collaborative Learning',
                        'Knowledge & Skill Modeling',
                        'Recommender Systems & LA Adoption',
                        'Effects on Teaching & Learning Practices',
                        'Reading & Writing Analytics',
                        'MOOCs & Social Learning',
                        'Assessment',
                        'Study Strategies',
                        'Affect Modeling']
        
        nationalityTypes = ['CelticEnglish', 'European', 'EastAsian', 'Hispanic', 'SouthAsian',
                            'Muslim', 'Greek', 'Nordic', 'African', 'Jewish']
                                
        author_nationality_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_nationalityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
                
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for i in range(len(clusterNames)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = dict()
                for year in years:
                    plotValue_map[i][conference][year] = dict()
                    for nationality in nationalityTypes:
                        plotValue_map[i][conference][year][nationality] = set()
                    
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    authors = eleTuple['authors']                                          
                    for author in authors:
                        if author in author_nationality_map.keys():
                            sorted_tuple = sorted(author_nationality_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            nationality = sorted_tuple[0][0].split(',')[0]             
                            for clusterIndex in clusterIndexes:
                                plotValue_map[clusterIndex][conference][year][nationality].add(author)
        
        for i in range(len(clusterNames)):
            for conference in conferences:
                for year in years:
                    for nationalityType in nationalityTypes:
                        plotValue_map[i][conference][year][nationalityType] = len(plotValue_map[i][conference][year][nationalityType])
        
        for i in range(len(clusterNames)):            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
        
            for conference in conferences:
                valueArray = []     
                for year in years:
                    distribution_array = []                    
                    for nationalityType in nationalityTypes:
                        distribution_array.append(plotValue_map[i][conference][year][nationalityType])
                    diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                    valueArray.append(diversityScore)
                    
                print('\t'.join([str(ele) for ele in valueArray]))
                    
                if conference == 'LAK':
                    x_positions = x_pos[3:]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                    plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
                if conference == 'EDM':
                    x_positions = x_pos
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray, kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                    plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
            # x-axis labels
            plt.xticks(x_pos, [str(year) for year in years])
            plt.legend()
            
            title = 'Nationality diversity (' + clusterNames[i] + ').png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                         
            plt.show()
        
    analyze_author_nationalityDiversity_subTopics(data_repository)


def predict_author_ethnicityNamePrism(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    if os.path.exists(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences)):
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
    else:
        author_ethnicity_map = dict()
        
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:
                    if author not in author_ethnicity_map.keys():                        
                        try:
                            link = 'http://www.name-prism.com/api_token/eth/json/a8bf670d77b1d810/' + author.replace(' ', '%20')                           
                            r = requests.get(link)                                                        
                            author_ethnicity_map[author] = r.json()                            
                        except:
                            print(r)
                            
                        time.sleep(1)                     
                
                    if len(author_ethnicity_map.keys()) % 10 == 0:
                        outfile = open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'w', encoding='utf-8')
                        outfile.write(json.dumps(author_ethnicity_map))
                        outfile.close()
    
    outfile = open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'w', encoding='utf-8')
    outfile.write(json.dumps(author_ethnicity_map))
    outfile.close()
    
    # Analyze results    
    ethnicity_count_map = defaultdict(int)
    for author in author_ethnicity_map.keys():
        sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
        ethnicity = sorted_tuple[0][0].split(',')[0]
        ethnicity_count_map[ethnicity] += 1
    for ethnicity in ethnicity_count_map.keys():
        print('%s\t%d\t%.2f' % (ethnicity, ethnicity_count_map[ethnicity], ethnicity_count_map[ethnicity] / float(len(author_ethnicity_map.keys())) * 100))                     


def analyze_author_ethnicity(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    '''
    def analyze_author_ethnicity_fraction(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
        
        ethnicity_index_map = dict()
        for i in range(len(ethnicityTypes)):
            ethnicity_index_map[ethnicityTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for ethnicity in ethnicityTypes:
                    plotValue_map[conference][year][ethnicity] = set()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][year][ethnicity].add(author)
        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------        
                
        for i in range(len(ethnicityTypes)):
            targetNationality = ethnicityTypes[i]
            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
            
            colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff']
                    
            # Extract data
            updated_plotValue_map = dict()
            for conference in conferences:
                updated_plotValue_map[conference] = dict()
                for year in years:
                    updated_plotValue_map[conference][year] = sorted(plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                            
            # LAK
            for j in range(len(ethnicityTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in years:
                    for k in range(j):
                        bottom_array[year-2008] += updated_plotValue_map['LAK'][year][k][1]                    
                    valueArray.append(updated_plotValue_map['LAK'][year][j][1])                    
                    colorArray.append(colors[ethnicity_index_map[updated_plotValue_map['LAK'][year][j][0]]])                
                plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=ethnicityTypes[j], edgecolor='#444444', bottom=bottom_array)
            
            # EDM
            for j in range(len(ethnicityTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in years:
                    for k in range(j):
                        bottom_array[year-2008] += updated_plotValue_map['EDM'][year][k][1]
                    valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                    colorArray.append(colors[ethnicity_index_map[updated_plotValue_map['EDM'][year][j][0]]])                
                plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                        
            # x-axis labels
            updated_labels = []
            for year in years:
                if year < 2011:
                    updated_labels.append("      EDM\n" + str(year))
                else:
                    updated_labels.append("LAK EDM\n" + str(year))
            plt.xticks(x_pos, updated_labels)
            
            # Display percentages
            threshold = 10
            # LAK        
            for year in years:
                for j in range(len(ethnicityTypes)):
                    x = year - 2008 - 0.27
                    y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                    percentage = int(updated_plotValue_map['LAK'][year][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
            
            for year in years:
                for j in range(len(ethnicityTypes)):
                    x = year - 2008 + 0.03
                    y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                    percentage = int(updated_plotValue_map['EDM'][year][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
                        
            # LAK
            x_positions = [x-0.15 for x in x_pos][3:]
            y_positions = []
            for year in range(2011,2020):
                index = None
                for j in range(len(updated_plotValue_map['LAK'][year])):
                    if updated_plotValue_map['LAK'][year][j][0] == targetNationality:
                        index = j
                y_positions.append(sum([updated_plotValue_map['LAK'][year][k][1] for k in range(index)]) + updated_plotValue_map['LAK'][year][index][1] / 2)
            
            x_positions.append(x_positions[-1] + 0.7)
            y_positions.append(y_positions[-1])
            
            plt.text(x_positions[-1]+0.13, y_positions[-1]-1, 'LAK')
            
            x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
            f = interp1d(x_positions, y_positions, kind='quadratic')
            y_smooth = f(x_new)
            
            plt.plot(x_new, y_smooth, color='#444444')
            plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)    
            
            # EDM
            x_positions = [x+0.15 for x in x_pos]
            y_positions = []
            for year in years:
                index = None
                for j in range(len(updated_plotValue_map['EDM'][year])):
                    if updated_plotValue_map['EDM'][year][j][0] == targetNationality:
                        index = j
                y_positions.append(sum([updated_plotValue_map['EDM'][year][k][1] for k in range(index)]) + updated_plotValue_map['EDM'][year][index][1] / 2)
            
            x_positions.append(x_positions[-1] + 0.4)
            y_positions.append(y_positions[-1])
            
            plt.text(x_positions[-1]+0.1, y_positions[-1]+0.4, 'EDM') 
            
            x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
            f = interp1d(x_positions, y_positions, kind='quadratic')
            y_smooth = f(x_new)
            plt.plot(x_new, y_smooth, linestyle='dashed', color='#444444')
            plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            # y-axix percentage
            points = 0   
            plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
            
            # plt.xlabel('Year')
             
            plt.ylabel('% Authors')           
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=5, mode="expand", borderaxespad=0.)
            
            title = 'Fraction of authors of different nationalities ' + str(ethnicityTypes[i]) + '.png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
                
            plt.show()        
                
    # analyze_author_ethnicity_fraction(data_repository)
    '''
    
    def analyze_author_ethnicity_fraction_all(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
        
        ethnicity_index_map = dict()
        for i in range(len(ethnicityTypes)):
            ethnicity_index_map[ethnicityTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for ethnicity in ethnicityTypes:
                plotValue_map[conference][ethnicity] = set()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][ethnicity].add(author)
        
        # Normalization
        for conference in conferences:            
            totalCount = 0
            for key in plotValue_map[conference].keys():                    
                totalCount += len(plotValue_map[conference][key])
            for key in plotValue_map[conference].keys():
                if totalCount > 0:
                    plotValue_map[conference][key] = len(plotValue_map[conference][key]) / float(totalCount) * 100
                else:
                    plotValue_map[conference][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(ethnicityTypes)))
        
        # Extract data    
        for conference in conferences:
            valueArray = []
            for ethnicity in ethnicityTypes:
                valueArray.append(plotValue_map[conference][ethnicity])
                
            # LAK
            if conference == 'LAK':                
                plt.bar(x_pos, valueArray, align='edge', color='#ff5858', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#ffdd67', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        plt.xticks(x_pos, ethnicityTypes)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend()
        
        title = 'Fraction of authors of different ethnicities (All).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    # analyze_author_ethnicity_fraction_all(data_repository)
    
    
    def analyze_author_ethnicity_fraction_by_years(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
        
        ethnicity_index_map = dict()
        for i in range(len(ethnicityTypes)):
            ethnicity_index_map[ethnicityTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for ethnicity in ethnicityTypes:
                    plotValue_map[conference][year][ethnicity] = set()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][year][ethnicity].add(author)
        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
        
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff']
                
        # Extract data
        updated_plotValue_map = dict()
        for conference in conferences:
            updated_plotValue_map[conference] = dict()
            for year in years:
                updated_plotValue_map[conference][year] = sorted(plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                        
        # LAK
        for j in range(len(ethnicityTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['LAK'][year][k][1]                    
                valueArray.append(updated_plotValue_map['LAK'][year][j][1])                    
                colorArray.append(colors[ethnicity_index_map[updated_plotValue_map['LAK'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=ethnicityTypes[j], edgecolor='#444444', bottom=bottom_array)
        
        # EDM
        for j in range(len(ethnicityTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['EDM'][year][k][1]
                valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                colorArray.append(colors[ethnicity_index_map[updated_plotValue_map['EDM'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                    
        # x-axis labels
        updated_labels = []
        for year in years:
            if year < 2011:
                updated_labels.append("      EDM\n" + str(year))
            else:
                updated_labels.append("LAK EDM\n" + str(year))
        plt.xticks(x_pos, updated_labels)
        
        # Display percentages
        threshold = 10
        # LAK        
        for year in years:
            for j in range(len(ethnicityTypes)):
                x = year - 2008 - 0.27
                y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                percentage = int(updated_plotValue_map['LAK'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        for year in years:
            for j in range(len(ethnicityTypes)):
                x = year - 2008 + 0.03
                y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                percentage = int(updated_plotValue_map['EDM'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=5, mode="expand", borderaxespad=0.)
        
        title = 'Fraction of authors of different ethnicities (By years).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()        
                
    # analyze_author_ethnicity_fraction_by_years(data_repository)
    
    
    def analyze_author_ethnicityDiversity_whole(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
        
        for conference in conferences:
            plotValue_map[conference] = dict()            
            for ethnicity in ethnicityTypes:
                plotValue_map[conference][ethnicity] = set()
        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][ethnicity].add(author)
        
        for conference in conferences:
            for ethnicity in plotValue_map[conference].keys():
                plotValue_map[conference][ethnicity] = len(plotValue_map[conference][ethnicity])
                                                    
        for conference in conferences:            
            distribution_array = []
            for ethnicityType in ethnicityTypes:
                distribution_array.append(plotValue_map[conference][ethnicityType])
            diversityScore = skbio.diversity.alpha.simpson(distribution_array)
            
            print('%s\t%.4f' % (conference, diversityScore))
            
    # analyze_author_ethnicityDiversity_whole(data_repository)    

    def analyze_author_ethnicityDiversity_allTopics(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for ethnicity in ethnicityTypes:
                    plotValue_map[conference][year][ethnicity] = set()
        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']                        
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]
                            plotValue_map[conference][year][ethnicity].add(author)
        
        # Normalization
        for conference in conferences:
            for year in years:
                for ethnicity in plotValue_map[conference][year].keys():
                    plotValue_map[conference][year][ethnicity] = len(plotValue_map[conference][year][ethnicity])
                                                    
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                
        # x-axis labels
        plt.xticks(x_pos, [str(year) for year in years])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:
            valueArray = []     
            for year in years:
                distribution_array = []
                for ethnicityType in ethnicityTypes:
                    distribution_array.append(plotValue_map[conference][year][ethnicityType])
                diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                valueArray.append(diversityScore)
                    
            print('\t'.join([str(ele) for ele in valueArray]))
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'Nationality diversity (All topics).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    # analyze_author_ethnicityDiversity_allTopics(data_repository)
    
    
    def analyze_author_ethnicityDiversity_subTopics(data_repository):
        
        clusterNames = ['Predictive & Descriptive Analytics',
                        'Engagement Patterns & Resource Use',
                        'Multimodal LA & Collaborative Learning',
                        'Knowledge & Skill Modeling',
                        'Recommender Systems & LA Adoption',
                        'Effects on Teaching & Learning Practices',
                        'Reading & Writing Analytics',
                        'MOOCs & Social Learning',
                        'Assessment',
                        'Study Strategies',
                        'Affect Modeling']
        
        ethnicityTypes = ['White', 'API', 'Hispanic', 'Black']
                        
        author_ethnicity_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_ethnicityNamePrism_' + '_'.join(conferences), 'r', encoding='utf-8').read())
                
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for i in range(len(clusterNames)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = dict()
                for year in years:
                    plotValue_map[i][conference][year] = dict()
                    for ethnicity in ethnicityTypes:
                        plotValue_map[i][conference][year][ethnicity] = set()
                    
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    authors = eleTuple['authors']                                          
                    for author in authors:
                        if author in author_ethnicity_map.keys():
                            sorted_tuple = sorted(author_ethnicity_map[author].items(), key=lambda kv: kv[1], reverse=True)        
                            ethnicity = sorted_tuple[0][0].split(',')[0]             
                            for clusterIndex in clusterIndexes:
                                plotValue_map[clusterIndex][conference][year][ethnicity].add(author)
                    
        # Plot -----------------------------------------------------------------
                
        # Line plot ------------------------------------------------------------
        for i in range(len(clusterNames)):
            for conference in conferences:
                for year in years:
                    for ethnicityType in ethnicityTypes:
                        plotValue_map[i][conference][year][ethnicityType] = len(plotValue_map[i][conference][year][ethnicityType])
        
        for i in range(len(clusterNames)):            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
        
            for conference in conferences:
                valueArray = []     
                for year in years:
                    distribution_array = []                    
                    for ethnicityType in ethnicityTypes:
                        distribution_array.append(plotValue_map[i][conference][year][ethnicityType])
                    diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                    valueArray.append(diversityScore)
                    
                print('\t'.join([str(ele) for ele in valueArray]))
                    
                if conference == 'LAK':
                    x_positions = x_pos[3:]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                    plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
                if conference == 'EDM':
                    x_positions = x_pos
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray, kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                    plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
            # x-axis labels
            plt.xticks(x_pos, [str(year) for year in years])
            plt.legend()
            
            title = 'Nationality diversity (' + clusterNames[i] + ').png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                         
            plt.show()
        
    analyze_author_ethnicityDiversity_subTopics(data_repository)
    

def analyze_author_overlappedAuthors(data_path):
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data ---------------------------------------------------------
    plotValue_map = dict()
    years = range(2011,2020)
            
    for conference in conferences:
        plotValue_map[conference] = dict()
        for year in years:
            plotValue_map[conference][year] = set()
        
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                    
                    plotValue_map[conference][year].add(author)
                
    # Plot ---------------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(years)))
                
    # x-axis labels
    plt.xticks(x_pos, [str(year) for year in years])
        
    # Line plot ----------------------------------------------------------------
    valueArray = []     
    for year in years:
        valueArray.append(len(plotValue_map['LAK'][year].intersection(plotValue_map['EDM'][year])))
    
    plt.bar(x_pos, valueArray, align='center', color='#ff8a5c', linewidth=0.5, edgecolor='#444444')
   
    title = 'Author overlap.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    
    
def analyze_author_authorComposition(data_path, fraction_mark):
   
    # 1. Authors that have published only in the same conference before
    # 2. Authors that have published in both of the two conferences before
    # 3. Authors that have published only in the other conference before
    # 4. Authors that have published in neither of the two conference before
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data ---------------------------------------------------------
    author_distribution_map = dict()
    years = range(2008,2020)
    
    for conference in conferences:
        author_distribution_map[conference] = dict()
        for year in years:
            author_distribution_map[conference][year] = set()
            
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                    
                    author_distribution_map[conference][year].add(author)
            # print((conference,year,len(author_distribution_map[conference][year])))
    
    pastAuthors_map = dict()
    for conference in conferences:
        pastAuthors_map[conference] = dict()
        for year in years:
            pastAuthors_map[conference][year] = set()
            for i in range(2008,year):
                pastAuthors_map[conference][year] = pastAuthors_map[conference][year].union(author_distribution_map[conference][i])
                              
    # Plot -----------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(years)))
            
    # x-axis labels
    plt.xticks(x_pos, [str(year) for year in years])
          
    # Plot value
    plotValue_map = dict()
    
    for conference in conferences:
        plotValue_map[conference] = dict()
        for year in years:
            plotValue_map[conference][year] = []
       
    for conference in conferences:
        for year in years:
            
            if conference == 'LAK':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][year].append(len(
                    author_distribution_map[conference][year].intersection(pastAuthors_map[conference][year]) - 
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['EDM'][year])
                    ))                
                           
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year].intersection(
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['EDM'][year]))))
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][year].append(len(
                    (author_distribution_map[conference][year] - pastAuthors_map[conference][year]).intersection(pastAuthors_map['EDM'][year])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year] - 
                                                           pastAuthors_map[conference][year] - 
                                                           pastAuthors_map['EDM'][year]))
                
            if conference == 'EDM':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][year].append(len(
                    author_distribution_map[conference][year].intersection(pastAuthors_map[conference][year]) - 
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['LAK'][year])
                    ))
                
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year].intersection(
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['LAK'][year]))))        
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][year].append(len(
                    (author_distribution_map[conference][year] - pastAuthors_map[conference][year]).intersection(pastAuthors_map['LAK'][year])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year] - 
                                                           pastAuthors_map[conference][year] - 
                                                           pastAuthors_map['LAK'][year]))
                
    # Test
    # print(len(author_distribution_map['LAK'][2011].intersection(pastAuthors_map['EDM'][2011])))
        
    colors = ['#eb7070', '#ffdd67', '#64c4ed', '#fac0e1']
    labels = ['Researchers that have published only in the same conference before',
              'Researchers that have published in both of the two conferences before',
              'Researchers that have published only in the other conference before',              
              'Researchers that have published in neither of the two conference before']
    
    if fraction_mark:
        # Calculate percentages
        for conference in conferences:
            for year in years:
                total = sum(plotValue_map[conference][year])
                if total > 0:
                    for i in range(len(plotValue_map[conference][year])):
                        plotValue_map[conference][year][i] = plotValue_map[conference][year][i] / float(total) * 100
        
    for conference in conferences:
        for i in range(len(colors)):
            bottom_array = [0] * len(years)
            valueArray = []
            for j in range(i):
                for year in years:
                    bottom_array[year-2008] += plotValue_map[conference][year][j]
            
            for year in years:
                valueArray.append(plotValue_map[conference][year][i])
            
            if conference == 'LAK':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.4, linewidth=0.5, label=labels[i], edgecolor='#444444', bottom=bottom_array)
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.4, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
    
    if fraction_mark:
        threshold = 5
    else:
        threshold = 10
        
    for conference in conferences:     
        for year in years:
            if sum(plotValue_map[conference][year]) > 0:
                for i in range(len(colors)):
                    if fraction_mark:                     
                        y = sum([plotValue_map[conference][year][j] for j in range(i)]) + plotValue_map[conference][year][i] - 3
                    else:
                        y = sum([plotValue_map[conference][year][j] for j in range(i)]) + plotValue_map[conference][year][i] - 7
                        
                    value = plotValue_map[conference][year][i]
                    
                    if conference == 'LAK':
                        if value >= 100:
                            x = year - 2008 - 0.35
                        else:
                            x = year - 2008 - 0.32
                    if conference == 'EDM':
                        if value >= 100:
                            x = year - 2008 + 0.05
                        else:
                            x = year - 2008 + 0.10
                    
                    if value >= threshold:
                        plt.text(x, y, ('%.0f' % value), fontsize=9)
                    
    # x-axis labels
    updated_labels = []
    for year in years:
        if year < 2011:
            updated_labels.append("      EDM\n" + str(year))
        else:
            updated_labels.append("LAK EDM\n" + str(year))
    plt.xticks(x_pos, updated_labels)
    
    # y-axix percentage
    if fraction_mark:
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])  
        
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)
    
    if fraction_mark:
        title = 'Research composition (fraction).png'
    else:
        title = 'Research composition (absolute).png'
    
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    

def analyze_author_authorAggregatedComposition(data_path, fraction_mark):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data ---------------------------------------------------------
    author_distribution_map = dict()
    years = range(2008,2020)
    
    step = 3
    num_stages = int(len(years)/step)
    
    for conference in conferences:
        author_distribution_map[conference] = dict()
        for i in range(num_stages):
            author_distribution_map[conference][i] = set()
            
    for conference in conferences:
        for year in years:
            index = int((year - 2008) / 3)
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                    
                    author_distribution_map[conference][index].add(author)   
        
    pastAuthors_map = dict()
    for conference in conferences:
        pastAuthors_map[conference] = dict()
        for i in range(num_stages):
            pastAuthors_map[conference][i] = set()
            for j in range(0,i):
                pastAuthors_map[conference][i] = pastAuthors_map[conference][i].union(author_distribution_map[conference][j])
                              
    # Plot -----------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(num_stages))
            
    # x-axis labels
    plt.xticks(x_pos, [str(year) for year in years])
          
    # Plot value
    plotValue_map = dict()    
    for conference in conferences:
        plotValue_map[conference] = dict()
        for i in range(num_stages):
            plotValue_map[conference][i] = []
       
    for conference in conferences:
        for i in range(num_stages):
            
            if conference == 'LAK':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i])
                    ))                
                           
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i]))))
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['EDM'][i])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['EDM'][i]))
                
            if conference == 'EDM':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i])
                    ))
                
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i]))))        
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['LAK'][i])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['LAK'][i]))
        
    colors = ['#eb7070', '#ffdd67', '#64c4ed', '#fac0e1']
    labels = ['Researchers that have published only in the same conference before',
              'Researchers that have published in both of the two conferences before',
              'Researchers that have published only in the other conference before',              
              'Researchers that have published in neither of the two conference before']
    
    if fraction_mark:
        for conference in conferences:
            for i in range(num_stages):
                total = sum(plotValue_map[conference][i])
                if total > 0:
                    for authorTypeIndex in range(len(plotValue_map[conference][i])):
                        plotValue_map[conference][i][authorTypeIndex] = plotValue_map[conference][i][authorTypeIndex] / float(total) * 100    
    
    for conference in conferences:
        for i in range(len(colors)):
            bottom_array = [0] * num_stages
            valueArray = []
            for j in range(i):
                for k in range(num_stages):
                    bottom_array[k] += plotValue_map[conference][k][j]
            
            for j in range(num_stages):
                valueArray.append(plotValue_map[conference][j][i])
            
            if conference == 'LAK':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.4, linewidth=0.5, label=labels[i], edgecolor='#444444', bottom=bottom_array)
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.4, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
    
    if fraction_mark:
        threshold = 5
    else:
        threshold = 15
        
    for conference in conferences:     
        for i in range(num_stages):
            if sum(plotValue_map[conference][i]) > 0:
                for j in range(len(colors)):
                    if fraction_mark:
                        y = sum([plotValue_map[conference][i][k] for k in range(j)]) + plotValue_map[conference][i][j] - 5
                    else:
                        y = sum([plotValue_map[conference][i][k] for k in range(j)]) + plotValue_map[conference][i][j] - 20
                        
                    value = plotValue_map[conference][i][j]
                    
                    if conference == 'LAK':
                        if value >= 100:
                            x = i - 0.25
                        else:
                            x = i - 0.23
                    if conference == 'EDM':
                        if value >= 100:
                            x = i + 0.15
                        else:
                            x = i + 0.17
                    
                    if value >= threshold:
                        plt.text(x, y, ('%.0f' % value), fontsize=9)           
    # x-axis labels
    updated_labels = []
    for i in range(num_stages):
        if i == 0:
            updated_labels.append("      EDM\nS" + str(i))
        else:
            updated_labels.append("LAK EDM\nS" + str(i))
    plt.xticks(x_pos, updated_labels)
    
    if fraction_mark:
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])  
        
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)
    
    if fraction_mark:
        title = 'Research aggregated composition (fraction).png'
    else:
        title = 'Research aggregated composition (absolute).png'
        
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    
        
def analyze_author_authorAggregatedTransition(data_path, fraction_mark):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data ---------------------------------------------------------
    author_distribution_map = dict()
    years = range(2008,2020)
    
    step = 3
    num_stages = int(len(years)/step)
    
    for conference in conferences:
        author_distribution_map[conference] = dict()
        for i in range(num_stages):
            author_distribution_map[conference][i] = set()
            
    for conference in conferences:
        for year in years:
            index = int((year - 2008) / 3)
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']                        
                for author in authors:                    
                    author_distribution_map[conference][index].add(author)   
        
    pastAuthors_map = dict()
    for conference in conferences:
        pastAuthors_map[conference] = dict()
        for i in range(num_stages):
            pastAuthors_map[conference][i] = set()
            if i > 0:
                for j in range(i-1,i):
                    pastAuthors_map[conference][i] = pastAuthors_map[conference][i].union(author_distribution_map[conference][j])
                              
    # Plot -----------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(num_stages))
            
    # x-axis labels
    plt.xticks(x_pos, [str(year) for year in years])
          
    # Plot value
    plotValue_map = dict()    
    for conference in conferences:
        plotValue_map[conference] = dict()
        for i in range(num_stages):
            plotValue_map[conference][i] = []
       
    for conference in conferences:
        for i in range(num_stages):
            
            if conference == 'LAK':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i])
                    ))                
                           
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i]))))
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['EDM'][i])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['EDM'][i]))
                
            if conference == 'EDM':                
                # 1. Authors that have published only in the same conference before
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i])
                    ))
                
                # 2. Authors that have published in both of the two conferences before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i]))))        
                
                # 3. Authors that have published only in the other conference before
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['LAK'][i])))
                
                # 4. Authors that have published in neither of the two conference before
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['LAK'][i]))
        
    colors = ['#eb7070', '#ffdd67', '#64c4ed', '#fac0e1']
    labels = ['Researchers that have published only in the same conference before',
              'Researchers that have published in both of the two conferences before',
              'Researchers that have published only in the other conference before',              
              'Researchers that have published in neither of the two conference before']
    
    if fraction_mark:
        for conference in conferences:
            for i in range(num_stages):
                total = sum(plotValue_map[conference][i])
                if total > 0:
                    for authorTypeIndex in range(len(plotValue_map[conference][i])):
                        plotValue_map[conference][i][authorTypeIndex] = plotValue_map[conference][i][authorTypeIndex] / float(total) * 100    
    
    for conference in conferences:
        for i in range(len(colors)):
            bottom_array = [0] * num_stages
            valueArray = []
            for j in range(i):
                for k in range(num_stages):
                    bottom_array[k] += plotValue_map[conference][k][j]
            
            for j in range(num_stages):
                valueArray.append(plotValue_map[conference][j][i])
            
            if conference == 'LAK':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.4, linewidth=0.5, label=labels[i], edgecolor='#444444', bottom=bottom_array)
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.4, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
    
    if fraction_mark:
        threshold = 5
    else:
        threshold = 15
        
    for conference in conferences:     
        for i in range(num_stages):
            if sum(plotValue_map[conference][i]) > 0:
                for j in range(len(colors)):
                    if fraction_mark:
                        y = sum([plotValue_map[conference][i][k] for k in range(j)]) + plotValue_map[conference][i][j] - 5
                    else:
                        y = sum([plotValue_map[conference][i][k] for k in range(j)]) + plotValue_map[conference][i][j] - 20
                        
                    value = plotValue_map[conference][i][j]
                    
                    if conference == 'LAK':
                        if value >= 100:
                            x = i - 0.25
                        else:
                            x = i - 0.23
                    if conference == 'EDM':
                        if value >= 100:
                            x = i + 0.15
                        else:
                            x = i + 0.17
                    
                    if value >= threshold:
                        plt.text(x, y, ('%.0f' % value), fontsize=9)           
    # x-axis labels
    updated_labels = []
    for i in range(num_stages):
        if i == 0:
            updated_labels.append("      EDM\nS" + str(i))
        else:
            updated_labels.append("LAK EDM\nS" + str(i))
    plt.xticks(x_pos, updated_labels)
    
    if fraction_mark:
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])  
        
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)
    
    if fraction_mark:
        title = 'Research aggregated transition (fraction).png'
    else:
        title = 'Research aggregated transition (absolute).png'
        
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    


def analyze_affiliationContinent(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Read the mapping between affiliations and continents
    affiliation_continent_map = dict()
    continentTypes = set()
    affiliations_file = open(data_path + 'LAK_EDM_Comparison/affiliations.csv', 'r', encoding='utf-8')
    reader = csv.reader(affiliations_file)
    next(reader,None)
    for row in reader:
        affiliation = row[1]
        continent = row[3]
        affiliation_continent_map[affiliation] = continent
        continentTypes.add(continent)
    
    continentTypes = ['North America', 'Europe', 'Oceania', 'East Asian', 'Latin America',
                      'Southeast Asian', 'Sub-Saharan Africa', 'South Asian', 'Middle East', 'Central Asian']
          
    def analyze_affiliation_continent_fraction_all(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        continent_index_map = dict()
        for i in range(len(continentTypes)):
            continent_index_map[continentTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()            
            for continent in continentTypes:
                plotValue_map[conference][continent] = set()
                
        for conference in conferences:
            for year in years:
                for eleTuple in data_repository[conference][year]:
                    affiliations = eleTuple['affiliations']                        
                    for affiliation in affiliations:
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    plotValue_map[conference][continent].add(subAffiliation)
                        elif affiliation is not None:
                            # print(affiliation)
                            continent = affiliation_continent_map[affiliation.lower()]
                            plotValue_map[conference][continent].add(affiliation)
        
        # Normalization
        for conference in conferences:            
            totalCount = 0
            for key in plotValue_map[conference].keys():                    
                totalCount += len(plotValue_map[conference][key])
            for key in plotValue_map[conference].keys():
                if totalCount > 0:
                    plotValue_map[conference][key] = len(plotValue_map[conference][key]) / float(totalCount) * 100
                else:
                    plotValue_map[conference][key] = 0
                        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(continentTypes)))
                    
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5']
        
        for conference in conferences:
            valueArray = []
            for continentType in continentTypes:
                valueArray.append(plotValue_map[conference][continentType])
                
            # LAK
            if conference == 'LAK':                
                plt.bar(x_pos, valueArray, align='edge', color='#ff5858', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#ffdd67', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        plt.xticks(x_pos, continentTypes, rotation=25)
        
        # Display percentages
        '''
        threshold = 10
        # LAK        
        for year in years:
            for j in range(len(continentTypes)):
                x = year - 2008 - 0.27
                y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                percentage = int(updated_plotValue_map['LAK'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        for year in years:
            for j in range(len(continentTypes)):
                x = year - 2008 + 0.03
                y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                percentage = int(updated_plotValue_map['EDM'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)                    
        '''
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
                 
        plt.ylabel('% Authors')           
        plt.legend()
        
        title = 'Fraction of affiliations of different continents (All).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    # analyze_affiliation_continent_fraction_all(data_repository) 
    
    
    def analyze_affiliation_continent_fraction_by_years(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        continent_index_map = dict()
        for i in range(len(continentTypes)):
            continent_index_map[continentTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for continent in continentTypes:
                    plotValue_map[conference][year][continent] = set()
                
        for conference in conferences:
            for year in years:
                for eleTuple in data_repository[conference][year]:
                    affiliations = eleTuple['affiliations']                        
                    for affiliation in affiliations:
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    plotValue_map[conference][year][continent].add(subAffiliation)
                        elif affiliation is not None:
                            # print(affiliation)
                            continent = affiliation_continent_map[affiliation.lower()]
                            plotValue_map[conference][year][continent].add(affiliation)
        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------        
            
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                    
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5']
                        
        # Extract data
        updated_plotValue_map = dict()
        for conference in conferences:
            updated_plotValue_map[conference] = dict()
            for year in years:
                updated_plotValue_map[conference][year] = sorted(plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                        
        # LAK
        for j in range(len(continentTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['LAK'][year][k][1]                    
                valueArray.append(updated_plotValue_map['LAK'][year][j][1])                    
                colorArray.append(colors[continent_index_map[updated_plotValue_map['LAK'][year][j][0]]])
            continentLabel = continentTypes[j]
            if 'Asian' in continentLabel:
                continentLabel = continentLabel.replace('Asian', 'Asia') 
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=continentLabel, edgecolor='#444444', bottom=bottom_array)
        
        # EDM
        for j in range(len(continentTypes)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in years:
                for k in range(j):
                    bottom_array[year-2008] += updated_plotValue_map['EDM'][year][k][1]
                valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                colorArray.append(colors[continent_index_map[updated_plotValue_map['EDM'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                    
        # x-axis labels
        updated_labels = []
        for year in years:
            if year < 2011:
                updated_labels.append("      EDM\n" + str(year))
            else:
                updated_labels.append("LAK EDM\n" + str(year))
        plt.xticks(x_pos, updated_labels)
        
        # Display percentages
        threshold = 10
        # LAK        
        for year in years:
            for j in range(len(continentTypes)):
                x = year - 2008 - 0.27
                y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                percentage = int(updated_plotValue_map['LAK'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        for year in years:
            for j in range(len(continentTypes)):
                x = year - 2008 + 0.03
                y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                percentage = int(updated_plotValue_map['EDM'][year][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)                    
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=5, mode="expand", borderaxespad=0.)
        
        title = 'Fraction of affiliations of different continents (By years).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    # analyze_affiliation_continent_fraction_by_years(data_repository)      
    
    
    
    '''  
    def analyze_affiliation_continent_fraction_subTopicTrend(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
                
        continent_index_map = dict()
        for i in range(len(continentTypes)):
            continent_index_map[continentTypes[i]] = i
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for continent in continentTypes:
                    plotValue_map[conference][year][continent] = set()
                
        for conference in conferences:
            for year in years:
                for eleTuple in data_repository[conference][year]:
                    affiliations = eleTuple['affiliations']                        
                    for affiliation in affiliations:
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    plotValue_map[conference][year][continent].add(subAffiliation)
                        elif affiliation is not None:
                            # print(affiliation)
                            continent = affiliation_continent_map[affiliation.lower()]
                            plotValue_map[conference][year][continent].add(affiliation)
        
        # Normalization
        for conference in conferences:
            for year in years:
                totalCount = 0
                for key in plotValue_map[conference][year].keys():                    
                    totalCount += len(plotValue_map[conference][year][key])
                for key in plotValue_map[conference][year].keys():
                    if totalCount > 0:
                        plotValue_map[conference][year][key] = len(plotValue_map[conference][year][key]) / float(totalCount) * 100
                    else:
                        plotValue_map[conference][year][key] = 0
                        
        # Plot -----------------------------------------------------------------
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5']
                           
        for i in range(len(continentTypes)):
            targetContinent = continentTypes[i]
            targetColor = colors[i]
            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
                          
            # Extract data
            updated_plotValue_map = dict()
            for conference in conferences:
                updated_plotValue_map[conference] = dict()
                for year in years:
                    updated_plotValue_map[conference][year] = []
            
            sorted_plotValue_map = dict()
            for conference in conferences:
                sorted_plotValue_map[conference] = dict()
                for year in years:
                    sorted_plotValue_map[conference][year] = sorted(plotValue_map[conference][year].items(), key=lambda kv: kv[1], reverse=True)
            
            for conference in conferences:
                for year in years:
                    for eleTuple in sorted_plotValue_map[conference][year]:
                        if eleTuple[0] == targetContinent:
                            updated_plotValue_map[conference][year].append(eleTuple)
            
            for conference in conferences:
                for year in years:
                    for eleTuple in sorted_plotValue_map[conference][year]:
                        if eleTuple[0] != targetContinent:
                            updated_plotValue_map[conference][year].append(eleTuple)
                            
            updated_continentTypes = [targetContinent]
            for continentType in continentTypes:
                if continentType != targetContinent:
                    updated_continentTypes.append(continentType)
                                       
            # LAK
            for j in range(len(updated_continentTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in years:
                    for k in range(j):
                        bottom_array[year-2008] += updated_plotValue_map['LAK'][year][k][1]                    
                    valueArray.append(updated_plotValue_map['LAK'][year][j][1])                    
                    colorArray.append(colors[continent_index_map[updated_plotValue_map['LAK'][year][j][0]]])
                continentLabel = updated_continentTypes[j]
                if 'Asian' in continentLabel:
                    continentLabel = continentLabel.replace('Asian', 'Asia') 
                plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=continentLabel, edgecolor='#444444', bottom=bottom_array)
            
            # EDM
            for j in range(len(updated_continentTypes)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in years:
                    for k in range(j):
                        bottom_array[year-2008] += updated_plotValue_map['EDM'][year][k][1]
                    valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                    colorArray.append(colors[continent_index_map[updated_plotValue_map['EDM'][year][j][0]]])                
                plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
                        
            # x-axis labels
            updated_labels = []
            for year in years:
                if year < 2011:
                    updated_labels.append("      EDM\n" + str(year))
                else:
                    updated_labels.append("LAK EDM\n" + str(year))
            plt.xticks(x_pos, updated_labels)
            
            # Display percentages
            threshold = 10
            # LAK        
            for year in years:
                for j in range(len(continentTypes)):
                    x = year - 2008 - 0.27
                    
                    if j == 0:
                        y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 6
                    else:
                        y = sum([updated_plotValue_map['LAK'][year][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year][j][1] - 3
                        
                    percentage = int(updated_plotValue_map['LAK'][year][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
            
            for year in years:
                for j in range(len(continentTypes)):
                    x = year - 2008 + 0.03
                    
                    if j == 0:
                        y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 6
                    else:
                        y = sum([updated_plotValue_map['EDM'][year][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year][j][1] - 3
                    
                    percentage = int(updated_plotValue_map['EDM'][year][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
                        
            # LAK
            x_positions = [x-0.15 for x in x_pos][3:]
            y_positions = []
            for year in range(2011,2020):
                index = None
                for j in range(len(updated_plotValue_map['LAK'][year])):
                    if updated_plotValue_map['LAK'][year][j][0] == targetContinent:
                        index = j
                y_positions.append(sum([updated_plotValue_map['LAK'][year][k][1] for k in range(index)]) + updated_plotValue_map['LAK'][year][index][1] - 2)
            
            x_positions.append(x_positions[-1] + 0.7)
            y_positions.append(y_positions[-1])
            
            plt.text(x_positions[-1]+0.13, y_positions[-1]-1, 'LAK')
            
            x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
            f = interp1d(x_positions, y_positions, kind='quadratic')
            y_smooth = f(x_new)
            
            plt.plot(x_new, y_smooth, color='#444444')
            plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)    
            
            # EDM
            x_positions = [x+0.15 for x in x_pos]
            y_positions = []
            for year in years:
                index = None
                for j in range(len(updated_plotValue_map['EDM'][year])):
                    if updated_plotValue_map['EDM'][year][j][0] == targetContinent:
                        index = j
                y_positions.append(sum([updated_plotValue_map['EDM'][year][k][1] for k in range(index)]) + updated_plotValue_map['EDM'][year][index][1] - 2)
            
            x_positions.append(x_positions[-1] + 0.4)
            y_positions.append(y_positions[-1])
            
            plt.text(x_positions[-1]+0.1, y_positions[-1]+0.4, 'EDM') 
            
            x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
            f = interp1d(x_positions, y_positions, kind='quadratic')
            y_smooth = f(x_new)
            plt.plot(x_new, y_smooth, linestyle='dashed', color='#444444')
            plt.scatter(x_positions[:-1], y_positions[:-1], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            # y-axix percentage
            points = 0   
            plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
            
            # plt.xlabel('Year')
             
            plt.ylabel('% Authors')           
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=5, mode="expand", borderaxespad=0.)
            
            title = 'Fraction of affiliations of different continents ' + str(continentTypes[i]) + ' - Trend.png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
                
            plt.show()
            
    # analyze_affiliation_continent_fraction_subTopicTrend(data_repository)
    '''
    
    def analyze_affiliation_continentDiversity_whole(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for continent in continentTypes:
                plotValue_map[conference][continent] = set()
                
        for conference in conferences:
            for year in years:
                for eleTuple in data_repository[conference][year]:
                    affiliations = eleTuple['affiliations']                        
                    for affiliation in affiliations:
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    plotValue_map[conference][continent].add(subAffiliation)
                        elif affiliation is not None:
                            continent = affiliation_continent_map[affiliation.lower()]
                            plotValue_map[conference][continent].add(affiliation)
        
        # Normalization
        for conference in conferences:
            for continent in plotValue_map[conference].keys():
                plotValue_map[conference][continent] = len(plotValue_map[conference][continent])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:
            valueArray = []     
            for year in years:
                distribution_array = []
                for continentType in continentTypes:
                    distribution_array.append(plotValue_map[conference][continentType])
                
                diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                valueArray.append(diversityScore)
                
            print('%s\t%.4f' % (conference, diversityScore))
                    
    # analyze_affiliation_continentDiversity_whole(data_repository)
    
    def analyze_affiliation_continentDiversity_allTopics(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = dict()
            for year in years:
                plotValue_map[conference][year] = dict()
                for continent in continentTypes:
                    plotValue_map[conference][year][continent] = set()
                
        for conference in conferences:
            for year in years:
                for eleTuple in data_repository[conference][year]:
                    affiliations = eleTuple['affiliations']                        
                    for affiliation in affiliations:
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    plotValue_map[conference][year][continent].add(subAffiliation)
                        elif affiliation is not None:
                            continent = affiliation_continent_map[affiliation.lower()]
                            plotValue_map[conference][year][continent].add(affiliation)
        
        # Normalization
        for conference in conferences:
            for year in years:
                for continent in plotValue_map[conference][year].keys():
                    plotValue_map[conference][year][continent] = len(plotValue_map[conference][year][continent])
                                                    
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
                
        # x-axis labels
        plt.xticks(x_pos, [str(year) for year in years])
        
        # Line plot ------------------------------------------------------------
        for conference in conferences:
            valueArray = []     
            for year in years:
                distribution_array = []
                for continentType in continentTypes:
                    distribution_array.append(plotValue_map[conference][year][continentType])
                
                diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                valueArray.append(diversityScore)
                    
            print('\t'.join([str(ele) for ele in valueArray]))
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'Affiliation continent diversity (All topics).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    # analyze_affiliation_continentDiversity_allTopics(data_repository)
    
    
    def analyze_affiliation_continentDiversity_subTopics(data_repository):
        
        clusterNames = ['Predictive & Descriptive Analytics',
                        'Engagement Patterns & Resource Use',
                        'Multimodal LA & Collaborative Learning',
                        'Knowledge & Skill Modeling',
                        'Recommender Systems & LA Adoption',
                        'Effects on Teaching & Learning Practices',
                        'Reading & Writing Analytics',
                        'MOOCs & Social Learning',
                        'Assessment',
                        'Study Strategies',
                        'Affect Modeling']
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for i in range(len(clusterNames)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = dict()
                for year in years:
                    plotValue_map[i][conference][year] = dict()
                    for continent in continentTypes:
                        plotValue_map[i][conference][year][continent] = set()
                    
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    affiliations = eleTuple['affiliations']                                          
                    for affiliation in affiliations:                        
                        if isinstance(affiliation, list):
                            for subAffiliation in affiliation:
                                if subAffiliation not in [' Inc.']:
                                    continent = affiliation_continent_map[subAffiliation.lower().strip()]
                                    for clusterIndex in clusterIndexes:
                                        plotValue_map[clusterIndex][conference][year][continent].add(subAffiliation)
                        elif affiliation is not None:
                            continent = affiliation_continent_map[affiliation.lower()]
                            for clusterIndex in clusterIndexes:
                                plotValue_map[clusterIndex][conference][year][continent].add(affiliation)    
        
        # Plot -----------------------------------------------------------------
                
        # Line plot ------------------------------------------------------------
        for i in range(len(clusterNames)):
            for conference in conferences:
                for year in years:
                    for continentType in continentTypes:
                        plotValue_map[i][conference][year][continentType] = len(plotValue_map[i][conference][year][continentType])
        
        for i in range(len(clusterNames)):            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
        
            for conference in conferences:
                valueArray = []     
                for year in years:
                    distribution_array = []                    
                    for continentType in continentTypes:
                        distribution_array.append(plotValue_map[i][conference][year][continentType])
                    diversityScore = skbio.diversity.alpha.simpson(distribution_array)
                    valueArray.append(diversityScore)
                    
                print('\t'.join([str(ele) for ele in valueArray]))
                    
                if conference == 'LAK':
                    x_positions = x_pos[3:]
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#ff8a5c', label='LAK')
                    plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
                if conference == 'EDM':
                    x_positions = x_pos
                    x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                    f = interp1d(x_positions, valueArray, kind='quadratic')
                    y_smooth = f(x_new)
                    plt.plot(x_new, y_smooth, color='#8559a5', label='EDM')
                    plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                
            # x-axis labels
            plt.xticks(x_pos, [str(year) for year in years])
            plt.legend()
            
            title = 'Affiliation continent diversity (' + clusterNames[i] + ').png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                         
            plt.show()
        
    analyze_affiliation_continentDiversity_subTopics(data_repository)
    

  
            
    
                      
    

def main():  
    
    data_path = '../data/'
    
    # Step 0: Authors - Gender
    # predict_author_gender_v1(data_path)
    # predict_author_gender_v2(data_path)
    # analyze_author_gender(data_path)
    
    # Step 1: Authors - Nationality
    # predict_author_nationalityNamePrism(data_path)
    # analyze_author_nationality(data_path)
   
    # Step 2: Authors - Ethnicity
    # predict_author_ethnicityNamePrism(data_path)
    # analyze_author_ethnicity(data_path)
    
    # Step 3: Authors - overlap
    # analyze_author_overlappedAuthors(data_path)
    
    # Step 4: Authors - Composition
    # analyze_author_authorComposition(data_path, True)
   
    # Step 5: Authors - Aggregated composition - 4 stages
    # analyze_author_authorAggregatedComposition(data_path, False)
    
    # Step 6: Authors - Aggregated transition - 4 stages
    # analyze_author_authorAggregatedTransition(data_path, False)
    
    # Step 7: Authors - Affiliations
    # analyze_affiliationContinent(data_path)
   
if __name__ == "__main__":
    main()
    











