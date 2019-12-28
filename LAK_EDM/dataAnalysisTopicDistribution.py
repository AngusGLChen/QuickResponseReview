'''
Created on 24 Jul 2019

@author: gche0022
'''

import numpy, random
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from LAK_EDM.functions import read_selected_data

font = {'size': 11}
plt.rc('font', **font)


def analyze_topic_dynamics(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    clusterIDs = ['Z211','Z21','Z24','Z22','Z23','Z29','Z210','Z26','Z27','Z25','Z28']
    
    # Analysis =================================================================
    
    def analyze_topic_dynamics_overall(data_repository, clusterIDs):
        # Q: What are the fractions of each cluster/topic in both All/LAK/EDM?
        
        clusterNames = ['Pred. & Desc.\nAnalytics',
                        'Engage. Patterns &\nResource Use',
                        'Multimodal LA &\nColla. Learning',
                        'Knowledge &\nSkill Modeling',
                        'Recom. Systems &\nLA Adoption',
                        'Effects on Teach. & \n Learning Practices',
                        'Read. & Writ.\nAnalytics',
                        'MOOCs &\nSocial Learning',
                        'Assessment',
                        'Study\nStrategies',
                        'Affect\nModeling']
                
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
                    
        # paperValue = 1 / float(len(article_hltaCluster_map.keys())) * 100
        # paperValue = 1
        
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
        
        # Plot -----------------------------------------------------------------
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(clusterIDs)))
        
        plt.bar(x_pos, plotValue_map['LAK'], align='edge', width=-0.4, color='#ff5858', linewidth=0.5, label='LAK', edgecolor='#444444')
        
        print("\t".join([str(ele) for ele in plotValue_map['LAK']]))
        
        # EDM
        plt.bar(x_pos, plotValue_map['EDM'], align='edge', width=0.4, color='#ffdd67', linewidth=0.5, label='EDM', edgecolor='#444444')
        
        # x-axis labels
        x_pos = [x for x in x_pos]
        plt.xticks(x_pos, clusterNames, rotation=75)
        
        print("\t".join([str(ele) for ele in plotValue_map['EDM']]))
        
        # Display percentages
        '''     
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
        '''
        # y-axix percentage
        # points = 0   
        # plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Topics')    
        # plt.ylabel('TScore')
        
        plt.legend()
        
        title = 'TScores of different research themes (All).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
             
        plt.show()
        
    # analyze_topic_dynamics_overall(data_repository, clusterIDs)   
      
        
    ############################################################################ 
    def analyze_topic_dynamics_weights(data_repository, clusterIDs):
        # Q: What are the fractions of each cluster/topic in both All/LAK/EDM over years, i.e., researchers' different amount of efforts in the two conferences?
        
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
                    
        # Plot -----------------------------------------------------------------
        
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
        threshold = 5
        # LAK
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
        
        # plt.xlabel('Year')    
        # plt.ylabel('% Papers')
        
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=3, mode="expand", borderaxespad=0.)
        
        title = 'TScores of different research themes (weights).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
            
        plt.show()
        
    analyze_topic_dynamics_weights(data_repository, clusterIDs)
    

    
    def analyze_topic_dynamics_priorities(data_repository, clusterIDs):
        # Q: What are the fractions of each cluster/topic in both All/LAK/EDM over years, i.e., their research priorities?
        
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
                
        plotValue_map = dict()
        years = range(2008,2020)
    
        for i in range(len(clusterIDs)):
            plotValue_map[i] = dict()
            for conference in conferences:
                plotValue_map[i][conference] = [0] * len(years)
                
        for conference in conferences:
            for year in years:                
                if year in data_repository[conference].keys():                    
                    num_papers = len(data_repository[conference][year])
                    if num_papers > 0:
                        paperValue = 1 / float(num_papers) * 100
                        paperValue = 1                  
                        for eleTuple in data_repository[conference][year]:
                            clusterIndexes = eleTuple['clusterIndexes']                        
                            for clusterIndex in clusterIndexes:
                                plotValue_map[clusterIndex][conference][year-2008] += (paperValue / len(clusterIndexes))
                        
        # Plot -----------------------------------------------------------------
        '''
        for i in range(len(clusterIDs)):
            targetClusterID = clusterIDs[i]
            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(years)))
            
            colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#f3a953', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5', '#f7ff56']
        
            # Extract data
            updated_plotValue_map = dict()
            for conference in conferences:
                updated_plotValue_map[conference] = dict()
                for year in range(len(years)):
                    updated_plotValue_map[conference][year] = dict()
                    for clusterID in clusterIDs:
                        updated_plotValue_map[conference][year][clusterID] = plotValue_map[clusterID_clusterIndex_map[clusterID]][conference][year]
                    updated_plotValue_map[conference][year] = sorted(updated_plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                            
            # LAK
            for j in range(len(clusterIDs)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in range(len(years)):
                    for k in range(j):
                        bottom_array[year] += updated_plotValue_map['LAK'][year][k][1]
                    valueArray.append(updated_plotValue_map['LAK'][year][j][1])
                    colorArray.append(colors[clusterID_clusterIndex_map[updated_plotValue_map['LAK'][year][j][0]]])                
                plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=clusterNames[j], edgecolor='#444444', bottom=bottom_array)
            
            # EDM
            for j in range(len(clusterIDs)):
                bottom_array = [0] * len(years)
                valueArray = []
                colorArray = []
                for year in range(len(years)):
                    for k in range(j):
                        bottom_array[year] += updated_plotValue_map['EDM'][year][k][1]
                    valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                    colorArray.append(colors[clusterID_clusterIndex_map[updated_plotValue_map['EDM'][year][j][0]]])                
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
                for j in range(len(clusterIDs)):
                    x = year - 2008 - 0.27
                    y = sum([updated_plotValue_map['LAK'][year-2008][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year-2008][j][1] - 3
                    percentage = int(updated_plotValue_map['LAK'][year-2008][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
            
            for year in years:
                for j in range(len(clusterIDs)):
                    x = year - 2008 + 0.03
                    y = sum([updated_plotValue_map['EDM'][year-2008][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year-2008][j][1] - 3
                    percentage = int(updated_plotValue_map['EDM'][year-2008][j][1])
                    if percentage >= threshold:
                        plt.text(x, y, percentage)
            
            # Line plots
            colors.reverse()
            
            # LAK
            x_positions = [x-0.15 for x in x_pos][3:]
            y_positions = []
            for year in range(3,len(years)):
                index = None
                for j in range(len(updated_plotValue_map['LAK'][year])):
                    if updated_plotValue_map['LAK'][year][j][0] == targetClusterID:
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
            for year in range(len(years)):
                index = None
                for j in range(len(updated_plotValue_map['EDM'][year])):
                    if updated_plotValue_map['EDM'][year][j][0] == targetClusterID:
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
            # points = 0   
            # plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
            
            # plt.xlabel('Year')    
            # plt.ylabel('% Papers')
            
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=3, mode="expand", borderaxespad=0.)
            
            title = 'TScores of different research themes (priorities) ' + str(clusterNames[i]) + '.png'
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
                
            plt.show()
        '''
                                
        # Print TScore for each topic
        for year in range(len(years)):
            for conference in conferences:
                printValueArray = []
                for clusterID in clusterIDs:
                    printValueArray.append(str(plotValue_map[clusterID_clusterIndex_map[clusterID]][conference][year]))
                print('\t'.join(printValueArray))
                                
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(years)))
        
        colors = ['#ff5858', '#ffdd67', '#ff8a5c', '#b0deff', '#4f81c7', '#a1dd70', '#caa5f1', '#fac0e1', '#24BFA8', '#A74AB5', '#f7ff56']
    
        # Extract data
        updated_plotValue_map = dict()
        for conference in conferences:
            updated_plotValue_map[conference] = dict()
            for year in range(len(years)):
                updated_plotValue_map[conference][year] = dict()
                for clusterID in clusterIDs:
                    updated_plotValue_map[conference][year][clusterID] = plotValue_map[clusterID_clusterIndex_map[clusterID]][conference][year]
                updated_plotValue_map[conference][year] = sorted(updated_plotValue_map[conference][year].items(), key=lambda kv: kv[1])
                            
        # LAK
        for j in range(len(clusterIDs)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in range(len(years)):
                for k in range(j):
                    bottom_array[year] += updated_plotValue_map['LAK'][year][k][1]
                valueArray.append(updated_plotValue_map['LAK'][year][j][1])
                colorArray.append(colors[clusterID_clusterIndex_map[updated_plotValue_map['LAK'][year][j][0]]])                
            plt.bar(x_pos, valueArray, align='edge', color=colorArray, width=-0.3, linewidth=0.5, label=clusterNames[j], edgecolor='#444444', bottom=bottom_array)
        
        # EDM
        for j in range(len(clusterIDs)):
            bottom_array = [0] * len(years)
            valueArray = []
            colorArray = []
            for year in range(len(years)):
                for k in range(j):
                    bottom_array[year] += updated_plotValue_map['EDM'][year][k][1]
                valueArray.append(updated_plotValue_map['EDM'][year][j][1])
                colorArray.append(colors[clusterID_clusterIndex_map[updated_plotValue_map['EDM'][year][j][0]]])                
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
        '''
        threshold = 10
        # LAK        
        for year in years:
            for j in range(len(clusterIDs)):
                x = year - 2008 - 0.27
                y = sum([updated_plotValue_map['LAK'][year-2008][k][1] for k in range(j)]) + updated_plotValue_map['LAK'][year-2008][j][1] - 3
                percentage = int(updated_plotValue_map['LAK'][year-2008][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        
        for year in years:
            for j in range(len(clusterIDs)):
                x = year - 2008 + 0.03
                y = sum([updated_plotValue_map['EDM'][year-2008][k][1] for k in range(j)]) + updated_plotValue_map['EDM'][year-2008][j][1] - 3
                percentage = int(updated_plotValue_map['EDM'][year-2008][j][1])
                if percentage >= threshold:
                    plt.text(x, y, percentage)
        '''
    
        # y-axix percentage
        # points = 0   
        # plt.gca().set_yticklabels([('{:.' + str(points) + 'f}%').format(x) for x in plt.gca().get_yticks()])
        
        # plt.xlabel('Year')    
        # plt.ylabel('% Papers')
        
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=3, mode="expand", borderaxespad=0.)
        
        title = 'TScores of different research themes (priorities).png'
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
            
        plt.show()
        
    analyze_topic_dynamics_priorities(data_repository, clusterIDs)
    
    





def main():  
    
    data_path = '../data/'
    
    # Step 0: Topic dynamics
    analyze_topic_dynamics(data_path)  
   
   
if __name__ == "__main__":
    main()
    











