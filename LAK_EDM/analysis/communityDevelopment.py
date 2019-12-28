'''
Created on 27 Sep 2019

@author: gche0022
'''

import numpy
import matplotlib.pyplot as plt
from LAK_EDM.functions import read_selected_data

font = {'size': 11}
plt.rc('font', **font)


    
def analyze_researcher_composition(data_path, fraction_mark=False):
    
    # To analyze the composition of the researchers
   
    # 1. Researchers that had published in the same conference before;
    # 2. Researchers that had published in both LAK or EDM before;
    # 3. Researchers that had published in the other conference before;
    # 4. Researchers that had never published in LAK or EDM before.
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data -------------------------------------------------------------
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
                              
    # Plot ---------------------------------------------------------------------
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
                # 1. Researchers that had published in the same conference before;
                plotValue_map[conference][year].append(len(
                    author_distribution_map[conference][year].intersection(pastAuthors_map[conference][year]) - 
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['EDM'][year])
                    ))                
                           
                # 2. Researchers that had published in both LAK or EDM before;
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year].intersection(
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['EDM'][year]))))
                
                # 3. Researchers that had published in the other conference before;
                plotValue_map[conference][year].append(len(
                    (author_distribution_map[conference][year] - pastAuthors_map[conference][year]).intersection(pastAuthors_map['EDM'][year])))
                
                # 4. Researchers that had never published in LAK or EDM before.
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year] - 
                                                           pastAuthors_map[conference][year] - 
                                                           pastAuthors_map['EDM'][year]))
                
            if conference == 'EDM':                
                # 1. Researchers that had published in the same conference before;
                plotValue_map[conference][year].append(len(
                    author_distribution_map[conference][year].intersection(pastAuthors_map[conference][year]) - 
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['LAK'][year])
                    ))
                
                # 2. Researchers that had published in both LAK or EDM before;
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year].intersection(
                    pastAuthors_map[conference][year].intersection(pastAuthors_map['LAK'][year]))))        
                
                # 3. Researchers that had published in the other conference before;
                plotValue_map[conference][year].append(len(
                    (author_distribution_map[conference][year] - pastAuthors_map[conference][year]).intersection(pastAuthors_map['LAK'][year])))
                
                # 4. Researchers that had never published in LAK or EDM before.
                plotValue_map[conference][year].append(len(author_distribution_map[conference][year] - 
                                                           pastAuthors_map[conference][year] - 
                                                           pastAuthors_map['LAK'][year]))
                
    # Test
    # print(len(author_distribution_map['LAK'][2011].intersection(pastAuthors_map['EDM'][2011])))
        
    colors = ['#70a1d7', '#f47c7c', '#f7f48b', '#a1de93']
    labels = ['Authors that had published in the same conference before',
              'Authors that had published in both LAK or EDM before',
              'Authors that had published in the other conference before',              
              'Authors that had never published in LAK or EDM before']
    
    if fraction_mark:
        # Calculate fractions
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
    
    '''
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
    '''
                             
    # x-axis labels
    updated_labels = []
    for year in years:
        if year < 2011:
            updated_labels.append("      EDM\n" + str(year))
        else:
            updated_labels.append("LAK EDM\n" + str(year))
    plt.xticks(x_pos, updated_labels)
    
    if fraction_mark:
        plt.ylabel('% Authors')
    else:
        plt.ylabel('# Authors')  

    if fraction_mark:
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])  
        
    # plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)
    plt.legend()
    
    if fraction_mark:
        title = 'The composition of researchers in LAK and EDM (Fraction).png'
    else:
        title = 'The composition of researchers in LAK and EDM (Absolute).png'
    
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    
    

def analyze_researcher_aggregatedComposition(data_path, fraction_mark=False):
    
    # To analyze the composition of the researchers in an yearly-aggregated manner 
   
    # 1. Researchers that had published in the same conference before;
    # 2. Researchers that had published in both LAK or EDM before;
    # 3. Researchers that had published in the other conference before;
    # 4. Researchers that had never published in LAK or EDM before.
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    # Prepare data --------------------------------------=----------------------
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
                              
    # Plot ---------------------------------------------------------------------
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
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i])
                    ))                
                
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['EDM'][i]))))
                
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['EDM'][i])))
                
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['EDM'][i]))
                
            if conference == 'EDM':
                plotValue_map[conference][i].append(len(
                    author_distribution_map[conference][i].intersection(pastAuthors_map[conference][i]) - 
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i])
                    ))
                
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i].intersection(
                    pastAuthors_map[conference][i].intersection(pastAuthors_map['LAK'][i]))))        
                
                plotValue_map[conference][i].append(len(
                    (author_distribution_map[conference][i] - pastAuthors_map[conference][i]).intersection(pastAuthors_map['LAK'][i])))
                
                plotValue_map[conference][i].append(len(author_distribution_map[conference][i] - 
                                                           pastAuthors_map[conference][i] - 
                                                           pastAuthors_map['LAK'][i]))
        
    colors = ['#70a1d7', '#f47c7c', '#f7f48b', '#a1de93']
    labels = ['Authors that had published in the same conference before',
              'Authors that had published in both LAK or EDM before',
              'Authors that had published in the other conference before',              
              'Authors that had never published in LAK or EDM before']
    
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
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=-0.3, linewidth=0.5, label=labels[i], edgecolor='#444444', bottom=bottom_array)
            if conference == 'EDM':
                plt.bar(x_pos, valueArray, align='edge', color=colors[i], width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
    
    '''
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
    '''
                
    # x-axis labels
    updated_labels = ["              EDM\nP0: 2008 - 2010",
                      "LAK       EDM\nP1: 2011 - 2013",
                      "LAK       EDM\nP2: 2014 - 2016",
                      "LAK       EDM\nP3: 2017 - 2019"]
    plt.xticks(x_pos, updated_labels)
    
    if fraction_mark:
        plt.ylabel('% Authors')
    else:
        plt.ylabel('# Authors')  

    if fraction_mark:
        points = 0   
        plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])  
           
    if fraction_mark:
        title = 'The aggregated composition of researchers (Fraction).png'
    else:
        title = 'The aggregated composition of researchers (Absolute).png'
        
    plt.legend()
        
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                 
    plt.show()
    
    








def main():  
    
    data_path = '../../data/'    
    
    analyze_researcher_composition(data_path)
    analyze_researcher_aggregatedComposition(data_path)
    
    
if __name__ == "__main__":
    main()
