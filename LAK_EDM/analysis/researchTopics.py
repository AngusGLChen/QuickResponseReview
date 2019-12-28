'''
Created on 26 Sep 2019

@author: gche0022
'''

import numpy
import matplotlib.pyplot as plt
from LAK_EDM.functions import read_selected_data

font = {'size': 11}
plt.rc('font', **font)


def analyze_average_num_covered_topics(data_path):
    # To analyze the average number of topics investigated by each paper
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
    # Plot ---------------------------------------------------------------------
    value_array = []
    for article in article_hltaCluster_map.keys():
        value_array.append(len(article_hltaCluster_map[article].intersection(set(clusterIDs))))
    
    print('Avg. # topics investigated by a paper:\t%.2f' % numpy.average(value_array))
    
    start = 0
    end = 8
    step = 1
    x_labels = list(range(start, end, step))
    bar_nums = [0] * (len(x_labels))
        
    for record_value in value_array:
        index = int(record_value / step) - 1
        bar_nums[index] += 1
        
    # Normalization
    bar_nums = [record_value/float(len(article_hltaCluster_map.keys()))*100 for record_value in bar_nums]
    x_pos = numpy.arange(len(x_labels)) + 1
    
    plt.figure(figsize=(12, 7.5))
    plt.bar(x_pos, bar_nums, width=0.8, linewidth=0.4, edgecolor='#444444', align='center', color='#40a798')
    
    for i in range(len(bar_nums)):
        plt.text(x_pos[i]-0.15, bar_nums[i]+0.25, ('%.1f' % bar_nums[i]) + '%')
    
    # x-axis labels
    updated_x_lables = []
    for i in range(len(x_labels)):
        updated_x_lables.append(str(x_labels[i] + 1))
    plt.xticks(x_pos, updated_x_lables)

    # y-axix percentage
    points = 0   
    plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
    
    plt.xlabel('# Topics')    
    plt.ylabel('% Papers')
    
    title = 'The average number of topics investigated by a paper.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
    
    plt.show() 


def analyze_tscore_overall(data_path):
    # To analyze T-Score of each topic in an overall manner    
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
            
    clusterNames = ['Predictive &\nDescriptive\nAnalytics',
                    'Engagement\nPatterns &\nResource Use',
                    'Multimodal LA &\nCollaborative\nLearning',
                    'Knowledge &\nSkill Modeling',
                    'Recommender\nSystems &\nLA Adoption',
                    'Effects on Teaching\n& Learning Practices',
                    'Reading &\nWriting Analytics',
                    'MOOCs &\nSocial Learning',
                    'Assessment',
                    'Study\nStrategies',
                    'Affect\nModeling']
    
    clusterNames = ['T1',
                    'T2',
                    'T3',
                    'T4',
                    'T5',
                    'T6',
                    'T7',
                    'T8',
                    'T9',
                    'T10',
                    'T11']
    
    conference_paper_map = dict()
    for conference in conferences:
        conference_paper_map[conference] = set()
        for year in data_repository[conference].keys():
            for eleTuple in data_repository[conference][year]:
                paperIndex = eleTuple['paperIndex']
                conference_paper_map[conference].add(paperIndex)
        # print("%s\t%d" % (conference, len(conference_paper_map[conference])))        
                
    plotValue_map = dict()
    for conference in conferences:
        plotValue_map[conference] = [0] * len(clusterIDs)
        for year in data_repository[conference].keys():
            for eleTuple in data_repository[conference][year]:
                paperIndex = eleTuple['paperIndex']
                clusterIndexes = eleTuple['clusterIndexes']
                for clusterIndex in clusterIndexes:
                    plotValue_map[conference][clusterIndex] += (1 / float(len(conference_paper_map[conference])) / len(clusterIndexes) * 100)
    
    # Print out T-Score for each topic
    print("\t".join([str(ele) for ele in plotValue_map['LAK']]))
    print("\t".join([str(ele) for ele in plotValue_map['EDM']]))
    
    # Plot ---------------------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(clusterIDs)))
    
    plt.bar(x_pos, plotValue_map['LAK'], align='edge', width=-0.4, color='#f23557', linewidth=0.5, label='LAK', edgecolor='#444444')
    plt.bar(x_pos, plotValue_map['EDM'], align='edge', width=0.4, color='#f0d43a', linewidth=0.5, label='EDM', edgecolor='#444444')
    
    # x-axis labels
    x_pos = [x for x in x_pos]
    # plt.xticks(x_pos, clusterNames, rotation=75)
    plt.xticks(x_pos, clusterNames)
    
    # Display percentages
    if False:    
        threshold = 0         
        for i in range(len(clusterIDs)):
            x = x_pos[i]
            # LAK
            lak_y = plotValue_map['LAK'][i] + 0.2
            percentage = plotValue_map['LAK'][i]
            if percentage >= threshold:                
                plt.text(x-0.35, lak_y, ('%.1f' % percentage))
            
            # EDM
            edm_y = plotValue_map['EDM'][i] + 0.2
            percentage = plotValue_map['EDM'][i]
            if percentage >= threshold:
                plt.text(x+0.12, edm_y, ('%.1f' % percentage))

    plt.ylabel('T-Score')    
    plt.legend()
    
    title = 'The overall T-Scores of different topics.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
         
    plt.show()


def analyze_tscore_by_years(data_path):
    # To analyze T-Score of each topic aross different years   
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
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
    
    clusterNames = ['T1',
                    'T2',
                    'T3',
                    'T4',
                    'T5',
                    'T6',
                    'T7',
                    'T8',
                    'T9',
                    'T10',
                    'T11']
    
    plotValue_map = dict()
    years = range(2008,2020)

    for i in range(len(clusterIDs)):
        plotValue_map[i] = dict()
        for conference in conferences:
            plotValue_map[i][conference] = [0] * len(years)
            
    for conference in conferences:
        for year in years:                
            if year in data_repository[conference].keys():  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']                        
                    for clusterIndex in clusterIndexes:
                        paperValue = 1 / float(len(data_repository[conference][year])) * 100
                        plotValue_map[clusterIndex][conference][year-2008] += (paperValue / len(clusterIndexes))
    
    # Print TScore for each topic
    for year in range(len(years)):
        for conference in conferences:
            printValueArray = []
            for clusterID in clusterIDs:
                printValueArray.append(str(plotValue_map[clusterID_clusterIndex_map[clusterID]][conference][year]))
            print('\t'.join(printValueArray))        
          
    # Plot ---------------------------------------------------------------------    
    fig = plt.figure(figsize=(12, 7.5))
    x_pos = list(range(len(years)))
    
    colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5', '#f7ff56']
    
    # LAK    
    for i in range(len(clusterIDs)):
        bottom_array = [0] * len(years)
        for year in range(len(years)):
            for j in range(i):            
                bottom_array[year] += plotValue_map[j]['LAK'][year]
        plt.bar(x_pos, plotValue_map[i]['LAK'], align='edge', color=colors[i], width=-0.3, linewidth=0.5, label=clusterNames[i], edgecolor='#444444', bottom=bottom_array)
    
    # EDM
    for i in range(len(clusterIDs)):
        bottom_array = [0] * len(years)
        for year in range(len(years)):
            for j in range(i):            
                bottom_array[year] += plotValue_map[j]['EDM'][year]       
        plt.bar(x_pos, plotValue_map[i]['EDM'], align='edge', color=colors[i], width=0.3, linewidth=0.5, edgecolor='#444444', bottom=bottom_array)
    
    # x-axis labels
    updated_labels = []
    for year in years:
        if year < 2011:
            updated_labels.append("      EDM\n" + str(year))
        else:
            updated_labels.append("LAK EDM\n" + str(year))
    plt.xticks(x_pos, updated_labels)
    
    # Display percentages
    if False:
        threshold = 5    
        for year in years:
            for i in range(len(clusterIDs)):
                x = year - 2008 - 0.28
                y = sum([plotValue_map[j]['LAK'][year-2008] for j in range(i)]) + plotValue_map[i]['LAK'][year-2008] / 2
                percentage = int(plotValue_map[i]['LAK'][year-2008])
                if percentage >= threshold:
                    if percentage >= 10:
                        plt.text(x, y, percentage)
                    else:
                        plt.text(x + 0.06, y, percentage)        
        for year in years:
            for i in range(len(clusterIDs)):
                x = year - 2008 + 0.05
                y = sum([plotValue_map[j]['EDM'][year-2008] for j in range(i)]) + plotValue_map[i]['EDM'][year-2008] / 2
                percentage = int(plotValue_map[i]['EDM'][year-2008])
                if percentage >= threshold:
                    plt.text(x, y, percentage)  
    
    # y-axix percentage
    # points = 0   
    # plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
    
    plt.ylabel('T-Score')    
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=6, mode="expand", borderaxespad=0.)
    
    title = 'The T-Score of different topics across years.png'
    title = title.replace(" ", "_")
    plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
        
    plt.show()
     



def main():  
    
    data_path = '../../data/'    
    
    # analyze_average_num_covered_topics(data_path)
    # analyze_tscore_overall(data_path)
    analyze_tscore_by_years(data_path)
    
    
    
if __name__ == "__main__":
    main()
    