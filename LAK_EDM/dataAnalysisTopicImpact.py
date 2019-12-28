'''
Created on 12 Aug 2019

@author: gche0022
'''


import csv
import matplotlib.pyplot as plt

from scipy.stats import mannwhitneyu
from scipy.interpolate import interp1d

from LAK_EDM.functions import read_selected_data


# font = {'family' : 'normal',
#         'size'   : 12}
# plt.rc('font', **font)


def computAvg(lst):
    if sum(lst) > 0:
        return sum(lst) / len(lst)
    else:
        return 0


def analyze_topicImpact(data_path):    
    # Q: On average, how many citations can an article receive (over years)?
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
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
    
    def analyze_topicImpact_whole(data_repository):
        valueMap = dict()
                
        for clusterIndex in range(len(clusterNames)):
            valueMap[clusterIndex] = []
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    num_citations = eleTuple['num_citations']
                    for clusterIndex in clusterIndexes:
                        valueMap[clusterIndex].append(num_citations)                 
               
        for clusterIndex in range(len(clusterNames)):            
            avg = computAvg(valueMap[clusterIndex])
            print(avg)            
         
    # analyze_topicImpact_whole(data_repository)
    
    
    
    def analyze_topicImpact_allVenues(data_repository):
        valueMap = dict()
                
        for clusterIndex in range(len(clusterNames)):
            valueMap[clusterIndex] = dict()
            for year in years:
                valueMap[clusterIndex][year] = []
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    num_citations = eleTuple['num_citations']
                    for clusterIndex in clusterIndexes:
                        valueMap[clusterIndex][year].append(num_citations)                 
               
        for clusterIndex in range(len(clusterNames)):
            printString = clusterNames[clusterIndex] + '\t'
            for year in years:
                avg = computAvg(valueMap[clusterIndex][year])
                printString += ('%.2f' % avg) + '\t'
            print(printString)
         
    # analyze_topicImpact_allVenues(data_repository)
    
    
    
    def analyze_topicImpact_subVenueAllYear(data_repository):
        valueMap = dict()
        
        for conference in conferences:
            valueMap[conference] = dict()  
            for clusterIndex in range(len(clusterNames)):
                valueMap[conference][clusterIndex] = []
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    num_citations = eleTuple['num_citations']
                    for clusterIndex in clusterIndexes:
                        valueMap[conference][clusterIndex].append(num_citations)                 
                
        for clusterIndex in range(len(clusterNames)):
            printString = clusterNames[clusterIndex] + '\t'
            
            dif = computAvg(valueMap['LAK'][clusterIndex]) - computAvg(valueMap['EDM'][clusterIndex])
            
            try:
                (staticValue, pValue) = mannwhitneyu(valueMap['LAK'][clusterIndex], valueMap['EDM'][clusterIndex])
                if pValue < 0.001:
                    printString += ('**%.2f' % dif) + '\t'
                elif pValue < 0.01:
                    printString += ('*%.2f' % dif) + '\t'
                else:
                    printString += ('%.2f' % dif) + '\t'
            except:
                printString += ('%.2f' % dif) + '\t'            
                    
            print(printString)
            
    # analyze_topicImpact_subVenueAllYear(data_repository)
    
    
    def analyze_topicImpact_subVenueByYear(data_repository):
        valueMap = dict()
        
        for conference in conferences:
            valueMap[conference] = dict()  
            for clusterIndex in range(len(clusterNames)):
                valueMap[conference][clusterIndex] = dict()
                for year in years:
                    valueMap[conference][clusterIndex][year] = []
        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    clusterIndexes = eleTuple['clusterIndexes']
                    num_citations = eleTuple['num_citations']
                    for clusterIndex in clusterIndexes:
                        valueMap[conference][clusterIndex][year].append(num_citations)                 
                
        for clusterIndex in range(len(clusterNames)):
            printString = clusterNames[clusterIndex] + '\t'
            for year in range(2011,2020):
                dif = computAvg(valueMap['LAK'][clusterIndex][year]) - computAvg(valueMap['EDM'][clusterIndex][year])
                if len(valueMap['LAK'][clusterIndex][year]) >= 10 and len(valueMap['EDM'][clusterIndex][year]) >= 10:
                    try:
                        (staticValue, pValue) = mannwhitneyu(valueMap['LAK'][clusterIndex][year], valueMap['EDM'][clusterIndex][year])
                        if pValue < 0.001:
                            printString += ('**%.2f' % dif) + '\t'
                        elif pValue < 0.01:
                            printString += ('*%.2f' % dif) + '\t'
                        else:
                            printString += ('%.2f' % dif) + '\t'
                    except:
                        printString += ('%.2f' % dif) + '\t'
                else:
                    printString += ('%.2f' % dif) + '\t'
                    
            print(printString)
         
    # analyze_topicImpact_subVenueByYear(data_repository)
    
    '''
    def analyze_author_breadth_depth_allVenues(data_repository):
        
        # Prepare data ---------------------------------------------------------
        author_citation_map = dict()
        author_topic_map = dict()
                
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']
                    num_citations = eleTuple['num_citations']                        
                    clusterIndexes = eleTuple['clusterIndexes']
                    for author in authors:
                        if author not in author_citation_map.keys():
                            author_citation_map[author] = 0
                        author_citation_map[author] += num_citations
                        if author not in author_topic_map.keys():
                            author_topic_map[author] = set()
                        author_topic_map[author] = author_topic_map[author].union(set(clusterIndexes))
        
        fractions = [0.10, 0.20, 0.30, 0.50]
        sorted_authors = sorted(author_citation_map.items(), key=lambda kv: kv[1], reverse=True)        
        
        plotValue_map = dict()
        for fraction in fractions:
            plotValue_map[fraction] = [0] * len(clusterNames)
            
        for fraction in fractions:
            numAuthors = int(len(author_citation_map.keys())*fraction)
            for i in range(numAuthors):
                author = sorted_authors[i][0]
                numTopics = len(author_topic_map[author])
                plotValue_map[fraction][numTopics-1] += 1
                
        # Plot -----------------------------------------------------------------            
        fig = plt.figure(figsize=(12, 7.5))
        x_pos = list(range(len(clusterNames)))
        
        colors = ['#eb7070', '#ffdd67', '#64c4ed', '#fac0e1']
        
        for i in range(len(fractions)):
            updated_x_pos = [x+(i-2)*0.2 for x in x_pos]
            plt.bar(updated_x_pos, plotValue_map[fractions[i]], align='edge', color=colors[i], width=0.2, label=str(int(fractions[i]*100)) + '%', linewidth=0.2, edgecolor='#444444')
        
        # x-axis labels
        plt.xticks(x_pos, [str(x+1) for x in x_pos])
        
        plt.xlabel('# Topics')    
        plt.ylabel('# Authors')
        
        plt.legend()
        
        title = 'Breadth and Depth (All).png'    
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
        
    # analyze_author_breadth_depth_allVenues(data_repository)
    '''
    
    def analyze_author_breadth_depth(data_repository):
        # Retrieve authors that have published in (i) only LAK, (ii) only EDM, and (iii) both LAK and EDM
        authorTypes = ['All', 'LAK', 'EDM', 'Both']
        authorType_author_map = dict()
        for authorType in authorTypes:
            authorType_author_map[authorType] = set()
            
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']
                    for author in authors:
                        authorType_author_map[conference].add(author)
                        authorType_author_map['All'].add(author)
        
        authorType_author_map['Both'] = authorType_author_map['LAK'].intersection(authorType_author_map['EDM'])
        authorType_author_map['LAK'] = authorType_author_map['LAK'] - authorType_author_map['Both']
        authorType_author_map['EDM'] = authorType_author_map['EDM'] - authorType_author_map['Both']
        
        print('# authors:')
        for authorType in authorTypes:
            print('\t%s\t%d' % (authorType, len(authorType_author_map[authorType])))
        print('')
        
        # Retrieve the number of topics tackled by authors ---------------------
        author_topic_map = dict()            
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']
                    # num_citations = eleTuple['num_citations']                        
                    clusterIndexes = eleTuple['clusterIndexes']
                    for author in authors:
                        if author not in author_topic_map.keys():
                            author_topic_map[author] = set()
                        author_topic_map[author] = author_topic_map[author].union(set(clusterIndexes))
        
        # Q1: On average, how many topics are tackled by each author?
        authorType_topicArray_map = dict()
        for authorType in authorTypes:
            authorType_topicArray_map[authorType] = []
            for author in authorType_author_map[authorType]:
                authorType_topicArray_map[authorType].append(len(author_topic_map[author]))
        
        print('# Avg. topics tackled by authors:')
        for authorType in authorTypes:
            avg = computAvg(authorType_topicArray_map[authorType])
            printString = authorType + '\t'
            if authorType != 'All':
                (staticValue, pValue) = mannwhitneyu(authorType_topicArray_map['All'], authorType_topicArray_map[authorType])
                if pValue < 0.001:
                    printString += '**'
                elif pValue < 0.01:
                    printString += ' *'                    
            printString += ('%.2f' % avg)
            print(printString)
        print('')
        
        # Retrieve the number of citations of authors --------------------------
        author_citation_map = dict()        
        for conference in conferences:
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']
                    num_citations = eleTuple['num_citations']
                    for author in authors:
                        if author not in author_citation_map.keys():
                            author_citation_map[author] = 0
                        author_citation_map[author] += num_citations
                            
        # Q2: On average, how many citations does each author have?
        authorType_citationArray_map = dict()
        for authorType in authorTypes:
            authorType_citationArray_map[authorType] = []
            for author in authorType_author_map[authorType]:
                authorType_citationArray_map[authorType].append(author_citation_map[author])
        
        print('# Avg. citations authors have:')
        for authorType in authorTypes:
            avg = computAvg(authorType_citationArray_map[authorType])
            printString = authorType + '\t'
            if authorType != 'All':
                (staticValue, pValue) = mannwhitneyu(authorType_citationArray_map['All'], authorType_citationArray_map[authorType])
                if pValue < 0.001:
                    printString += '**'
                elif pValue < 0.01:
                    printString += ' *'                    
            printString += ('%.2f' % avg)
            print(printString)
        
        # The distribution of top-ranked authors--------------------------------
        sorted_authors = sorted(author_citation_map.items(), key=lambda kv: kv[1], reverse=True)   
        fractions = [0.10, 0.20, 0.30, 1.00]
        
        for authorType in authorTypes:
                       
            plotValue_map = dict()
            for fraction in fractions:
                plotValue_map[fraction] = [0] * len(clusterNames)
                
            selected_sorted_authors = []
            for author in sorted_authors:
                if author[0] in authorType_author_map[authorType]:
                    selected_sorted_authors.append(author[0])
            
            for fraction in fractions:
                numAuthors = int(len(authorType_author_map[authorType])*fraction)    
                for i in range(numAuthors):
                    author = selected_sorted_authors[i]                    
                    numTopics = len(author_topic_map[author])
                    plotValue_map[fraction][numTopics-1] += 1
                                        
            # Plot -----------------------------------------------------------------            
            fig = plt.figure(figsize=(12, 7.5))
            x_pos = list(range(len(clusterNames)))
            
            colors = ['#eb7070', '#ffdd67', '#64c4ed', '#fac0e1']
            
            for i in range(len(fractions)):
                updated_x_pos = [x+(i-2)*0.2 for x in x_pos]
                plt.bar(updated_x_pos, plotValue_map[fractions[i]], align='edge', color=colors[i], width=0.2, label=str(int(fractions[i]*100)) + '%', linewidth=0.2, edgecolor='#444444')
            
            # x-axis labels
            plt.xticks(x_pos, [str(x+1) for x in x_pos])
            
            plt.xlabel('# Topics')    
            plt.ylabel('# Authors')
            
            plt.legend()
            
            title = 'Breadth and Depth (' + authorType + ').png'    
            title = title.replace(" ", "_")
            plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
            
            plt.show()
        
    # analyze_author_breadth_depth(data_repository)
    
    
    def analyze_author_network(data_repository):        
        for conference in conferences:
            edge_array = []
            for year in years:  
                for eleTuple in data_repository[conference][year]:
                    authors = eleTuple['authors']
                    for i in range(len(authors)):
                        for j in range(i+1, len(authors)):
                            edge_array.append([authors[i], authors[j]])
            
            outFile = open(data_path + 'LAK_EDM_Comparison/' + conference +'_author_gephi.csv', 'w', encoding='utf-8')
            writer = csv.writer(outFile)
            writer.writerow(['Source', 'Target'])
            for edgeeTuple in edge_array:
                writer.writerow(edgeeTuple)
            outFile.close()
    
    # analyze_author_network(data_repository)
    
    

def main():  
    
    data_path = '../data/'
    
    # Step 0: Topics' impact - All
    analyze_topicImpact(data_path)
    
   
if __name__ == "__main__":
    main()
    











