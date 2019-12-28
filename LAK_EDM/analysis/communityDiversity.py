'''
Created on 27 Sep 2019

@author: gche0022
'''

import csv
import json
import numpy
import skbio
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d
from LAK_EDM.functions import read_selected_data

font = {'size': 11}
plt.rc('font', **font)



def analyze_researcher_gender(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    
    def analyze_researcher_gender(data_repository):
        # To analyze the number of researchers of different gender
        
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
        colors = ['#70a1d7', '#f47c7c', '#f7f48b']
        
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
        
        title = 'The number of researchers of different gender across years.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
             
    analyze_researcher_gender(data_repository)
        
    
    def analyze_researcher_gender_diversity_overall(data_repository): 
        
        # Prepare data ---------------------------------------------------------
        plotValue_map = dict()
        years = range(2008,2020)
        
        for conference in conferences:
            plotValue_map[conference] = {'Male':set(), 'Female':set(), 'Others':set()}
        
        author_gender_map = json.loads(open(data_path + 'LAK_EDM_Comparison/author_gender_' + '_'.join(conferences) + '_v1', 'r', encoding='utf-8').read())
        
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
                        
        genderTypes = ['Male', 'Female', 'Others']
        for conference in conferences:
            for genderType in genderTypes:
                plotValue_map[conference][genderType] = len(plotValue_map[conference][genderType])
    
        for conference in conferences:
            diversityScore = skbio.diversity.alpha.simpson([plotValue_map[conference]['Male'],
                                                            plotValue_map[conference]['Female']])
            sum = plotValue_map[conference]['Male'] + plotValue_map[conference]['Female'] + plotValue_map[conference]['Others']
            print('%s\t%.2f\t%.2f\t%.4f' % (conference, plotValue_map[conference]['Male']/float(sum)*100, plotValue_map[conference]['Female']/float(sum)*100, diversityScore))
            
    analyze_researcher_gender_diversity_overall(data_repository)
       
    
    def analyze_researcher_gender_diversity_by_years(data_repository): 
        
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
                
            # print('\t'.join([str(ele) for ele in valueArray]))
            print(valueArray)
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f23557', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f0d43a', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
        
        plt.ylabel('Simpson\'s index')
                  
        plt.legend()
        
        title = 'The gender diversity in LAK and EDM.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    analyze_researcher_gender_diversity_by_years(data_repository)
   
       

def analyze_researcher_nationality(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    
    def analyze_researcher_nationality_fraction(data_repository): 
        # To analyze the fraction of researchers of different nationality
        
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
        
        for conference in conferences:
            valueArray = []
            for nationality in nationalityTypes:
                valueArray.append(plotValue_map[conference][nationality])
                
            # LAK
            if conference == 'LAK':                
                plt.bar(x_pos, valueArray, align='edge', color='#f23557', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#f0d43a', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        plt.xticks(x_pos, nationalityTypes, rotation=15)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend()
        
        title = 'The fraction of researchers of different nationality.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    analyze_researcher_nationality_fraction(data_repository)
           
        
    def analyze_researcher_nationality_diversity_overall(data_repository): 
        
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
            
    analyze_researcher_nationality_diversity_overall(data_repository)
        
        
    def analyze_researcher_nationality_diversity_by_years(data_repository): 
        
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
                    
            # print('\t'.join([str(ele) for ele in valueArray]))
            print(valueArray)
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f23557', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f0d43a', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
        
        plt.ylabel('Simpson\'s index')
                  
        plt.legend()
        
        title = 'The nationality diversity in LAK and EDM.png'
        
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    analyze_researcher_nationality_diversity_by_years(data_repository)
       


def analyze_researcher_ethinicity(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    
    def analyze_researcher_ethnicity_fraction(data_repository): 
        
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
                plt.bar(x_pos, valueArray, align='edge', color='#f23557', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#f0d43a', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        ethnicityTypes = ['White', 'Asian / Pacific Islanders', 'Hispanic', 'Black']
        plt.xticks(x_pos, ethnicityTypes)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')
         
        plt.ylabel('% Authors')           
        plt.legend()
        
        title = 'The fraction of researchers of different ethnicity.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    analyze_researcher_ethnicity_fraction(data_repository)
    
    
    def analyze_researcher_ethinicity_diversity_overall(data_repository): 
        
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
            
            print('Overall ethnicity diversity: %s\t%.4f' % (conference, diversityScore))
            
    # analyze_researcher_ethinicity_diversity_overall(data_repository)    


    def analyze_researcher_ethinicity_diversity_by_years(data_repository): 
        
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
                    
            # print('\t'.join([str(ele) for ele in valueArray]))
            print(valueArray)
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f23557', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#0278ae', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.ylabel('Simpson\'s index')
                  
        plt.legend()
        
        title = 'The ethnicity diversity in LAK and EDM.png'
        
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    analyze_researcher_ethinicity_diversity_by_years(data_repository)
    
    
    
def analyze_affiliation_region(data_path):
    
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
    
         
    def analyze_affiliation_region_fraction(data_repository): 
        
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
        
        for conference in conferences:
            valueArray = []
            for continentType in continentTypes:
                valueArray.append(plotValue_map[conference][continentType])
                
            # LAK
            if conference == 'LAK':                
                plt.bar(x_pos, valueArray, align='edge', color='#f23557', width=-0.3, linewidth=0.5, label='LAK', edgecolor='#444444')
            
            # EDM
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color='#f0d43a', width=0.3, linewidth=0.5, label='EDM', edgecolor='#444444')
                        
        # x-axis labels
        updated_continentTypes = ['North\nAmerica', 'Europe', 'Oceania', 'East\nAsian', 'Latin\nAmerica',
                                  'Southeast\nAsian', 'Sub-Saharan\nAfrica', 'South\nAsian', 'Middle\nEast', 'Central\nAsian']
    
        
        plt.xticks(x_pos, updated_continentTypes, rotation=25)
        
        # y-axix percentage
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
                 
        plt.ylabel('% Affiliations')           
        plt.legend()
        
        title = 'The fraction of affiliations of different region.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
            
        plt.show()
    
    analyze_affiliation_region_fraction(data_repository) 
    
        
    def analyze_affiliation_region_diversity_overall(data_repository): 
        
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
                
            print('Overall diversity: %s\t%.4f' % (conference, diversityScore))
                    
    # analyze_affiliation_region_diversity_overall(data_repository)
    
    
    def analyze_affiliation_region_diversity_by_years(data_repository): 
        
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
                    
            # print('\t'.join([str(ele) for ele in valueArray]))
            print(valueArray)
            
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray[3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f23557', label='LAK')
                plt.scatter(x_positions, valueArray[3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, valueArray, kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color='#f0d43a', label='EDM')
                plt.scatter(x_positions, valueArray, marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
        plt.legend()
        
        title = 'The affiliation diversity in LAK and EDM.png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                     
        plt.show()
        
    analyze_affiliation_region_diversity_by_years(data_repository)
    
    
    
def merge_diversity_plots(data_path):
    
    gender_diversity_array = {'LAK':[None, None, None, 0.49972958355868036, 0.41907781741313244, 0.42759808912209263, 0.3832849387703572, 0.46487153433009143, 0.4729875821767713, 0.46200146092037975, 0.48786646801848443, 0.45253469685902115],
                              'EDM':[0.375, 0.4131944444444444, 0.4584889399597818, 0.3653260695401377, 0.4351999999999999, 0.35379972565157747, 0.44907197827071077, 0.4415209610014804, 0.4128922495274101, 0.460638683297966, 0.4123371108253051, 0.4328987354180962]}
     
    nationality_diversity_array = {'LAK':[None, None, None, 0.7458677685950413, 0.7293328708521216, 0.7729680107337052, 0.7295641114579721, 0.7092086140837628, 0.7712128629956969, 0.7286783854166667, 0.7500758477444047, 0.7858223567105732],
                                   'EDM':[0.7733491969066032, 0.7744, 0.6816666666666666, 0.7999033933099867, 0.7130267585322865, 0.6888514183693712, 0.7644123493853705, 0.7757631680123029, 0.7560113892160224, 0.7725, 0.7771157988705389, 0.7982619936799771]}
    
    ethinicity_diversity_array = {'LAK':[None, None, None, 0.16528925619834722, 0.29945658457625157, 0.2793588023444672, 0.40282113539137476, 0.3627295547628484, 0.39006416037517067, 0.404296875, 0.3566010875399659, 0.4884300462798149],
                                  'EDM':[0.5306365258774539, 0.40879999999999994, 0.505, 0.44704745803646906, 0.39224483255888465, 0.37185082324935537, 0.3915777516329263, 0.4460438292964243, 0.46373786914327453, 0.49898437500000004, 0.5026684003182673, 0.49849181269750065]}
    
    affiliation_diversity_array = {'LAK':[None, None, None, 0.5493827160493827, 0.5918367346938775, 0.5948392937980986, 0.5930309007232084, 0.6062809917355372, 0.6740828402366864, 0.6322120739585654, 0.668054110301769, 0.7061541692921655],
                                   'EDM':[0.2975206611570247, 0.7377777777777778, 0.49777777777777776, 0.6977777777777778, 0.32199546485260766, 0.35792549306062826, 0.5520523497917906, 0.60239445494644, 0.5501730103806228, 0.4614743856726363, 0.42455418381344323, 0.6383592373017146]}
    
    years = range(2008,2020)
    conferences = ['LAK','EDM']
    
    # Plot -----------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(years)))
    
    colors = ['#f23557', '#f0d43a', '#22b2da', '#3b4a6b']
    labels = ['Gender', 'Nationality', 'Ethnicity', 'Affiliation']
    data_array = [gender_diversity_array,
                  nationality_diversity_array,
                  ethinicity_diversity_array,
                  affiliation_diversity_array]
                
    # x-axis labels
    plt.xticks(x_pos, [str(year) for year in years])
    
    for i in range(len(labels)):
        for conference in conferences:        
            if conference == 'LAK':
                x_positions = x_pos[3:]
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, data_array[i][conference][3:], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color=colors[i], linestyle='-', linewidth=3, label=labels[i]+' - '+conference)
                plt.scatter(x_positions, data_array[i][conference][3:], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
            
            if conference == 'EDM':
                x_positions = x_pos
                x_new = numpy.linspace(min(x_positions), max(x_positions), 500)
                f = interp1d(x_positions, data_array[i][conference], kind='quadratic')
                y_smooth = f(x_new)
                plt.plot(x_new, y_smooth, color=colors[i], linestyle='--', linewidth=3, label=labels[i]+' - '+conference)
                plt.scatter(x_positions, data_array[i][conference], marker='o', s=50, facecolors='#ffffff', edgecolors='#444444', zorder=10)
                   
    # plt.legend()
    plt.legend(loc=4, ncol=2)
    
    title = 'The gender, nationality, ethnicity, and affiliation diversity in LAK and EDM.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
        
        
        
        
        
        
        
    
def main():  
    
    data_path = '../../data/'
    
    # analyze_researcher_gender(data_path)    
    analyze_researcher_nationality(data_path)
    analyze_researcher_ethinicity(data_path)
    # analyze_affiliation_region(data_path)
    
    merge_diversity_plots(data_path)
    
    
    
if __name__ == "__main__":
    main()