'''
Created on 26 Sep 2019

@author: gche0022
'''

import matplotlib.pyplot as plt
from LAK_EDM.functions import read_selected_data

font = {'size': 11}
plt.rc('font', **font)


def analyze_paper_distribution(data_path):
    # To analyze the number of papers accepted by LAK/EDM in the years between 2008 and 2019
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    plotValue_map = dict()
    years = range(2008,2020)
        
    for conference in conferences:
        plotValue_map[conference] = [0] * len(years)
        for year in data_repository[conference].keys():
            plotValue_map[conference][year-2008] = len(data_repository[conference][year])
            
    # for conference in conferences:
    #     print(plotValue_map[conference])
    
    plotValue_map['LAK'] = [0, 0, 0, 16, 34, 39, 34, 59, 62, 63, 60, 69]
    plotValue_map['EDM'] = [17, 20, 23, 37, 32, 49, 57, 91, 82, 50, 60, 64]
    
    # Plot ---------------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(years)))  
        
    for conference in conferences:        
        if conference == 'LAK':
            plt.bar(x_pos, plotValue_map[conference], align='edge', color='#f23557', width=-0.4, linewidth=0.5, label='LAK', edgecolor='#444444')
        if conference == 'EDM':
            plt.bar(x_pos, plotValue_map[conference], align='edge', color='#f0d43a', width=0.4, linewidth=0.5, label='EDM', edgecolor='#444444')
        
    # x-axis labels
    updated_labels = []
    for year in years:
        if year < 2011:
            updated_labels.append("      EDM\n" + str(year))
        else:
            updated_labels.append("LAK EDM\n" + str(year))
    plt.xticks(x_pos, updated_labels)
    
    plt.ylabel('# Papers')        
    plt.legend()
        
    title = 'The number of papers accepted by LAK and EDM.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)        
        
    plt.show()


def main():  
    
    data_path = '../../data/'    
    analyze_paper_distribution(data_path)
   
if __name__ == "__main__":
    main()
    