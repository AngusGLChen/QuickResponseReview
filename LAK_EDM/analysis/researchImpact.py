'''
Created on 27 Sep 2019

@author: gche0022
'''

import matplotlib.pyplot as plt

from scipy.stats import mannwhitneyu
from LAK_EDM.functions import read_selected_data
from LAK_EDM.dataAnalysisTopicImpact import computAvg

font = {'size': 11}
plt.rc('font', **font)



def computAvg(lst):
    if sum(lst) > 0:
        return sum(lst) / len(lst)
    else:
        return 0


def analyze_research_impact(data_path):    
    
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
    
     
    def analyze_citation_difference_by_topics(data_repository):
        
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
            
            try:
                (staticValue, pValue) = mannwhitneyu(valueMap['LAK'][clusterIndex], valueMap['EDM'][clusterIndex])
                if pValue < 0.001:
                    printString = clusterNames[clusterIndex] + " **\t"
                elif pValue < 0.01:
                    printString = clusterNames[clusterIndex] + " *\t"
                else:
                    printString = clusterNames[clusterIndex] + "\t"
            except Exception as e:
                print(e)       
                        
            printString += str(computAvg(valueMap['LAK'][clusterIndex])) + '\t' + str(computAvg(valueMap['EDM'][clusterIndex]))
            print(printString)
            
            
    analyze_citation_difference_by_topics(data_repository)
    
    
   
def analyze_research_patterns(data_path):
    
    data_repository, article_hltaCluster_map, hltaCluster_article_map, clusterID_clusterIndex_map = read_selected_data(data_path)
    conferences = ['LAK','EDM']
    years = range(2008,2020)
    
    authorTypes = ['LAK', 'EDM']
    authorType_author_map = dict()
    for authorType in authorTypes:
        authorType_author_map[authorType] = set()
        
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:
                authors = eleTuple['authors']
                for author in authors:
                    authorType_author_map[conference].add(author)                    
        
    print('# Researchers:')
    for authorType in authorTypes:
        print('%s\t%d' % (authorType, len(authorType_author_map[authorType])))
    print('\n')
    
    # Retrieve the number of topics tackled by authors -------------------------
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
    
    # Q1: On average, how many topics are tackled by each researcher?
    authorType_topicArray_map = dict()
    for authorType in authorTypes:
        authorType_topicArray_map[authorType] = []
        for author in authorType_author_map[authorType]:
            authorType_topicArray_map[authorType].append(len(author_topic_map[author]))
        
    print('# Avg. topics investigated by each researcher:')
    print('%s\t%.2f' % ('LAK', computAvg(authorType_topicArray_map['LAK']))) 
    print('%s\t%.2f' % ('EDM', computAvg(authorType_topicArray_map['EDM'])))
    _, pValue = mannwhitneyu(authorType_topicArray_map['LAK'], authorType_topicArray_map['EDM'])
    if pValue < 0.001:
        print('**')
    elif pValue < 0.01:
        print(' *')    
    print('\n')
    
    # Retrieve the number of citations of authors ------------------------------
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
    
    print('# Avg. citations that each researcher has:')
    print('%s\t%.2f' % ('LAK', computAvg(authorType_citationArray_map['LAK']))) 
    print('%s\t%.2f' % ('EDM', computAvg(authorType_citationArray_map['EDM'])))
    _, pValue = mannwhitneyu(authorType_citationArray_map['LAK'], authorType_citationArray_map['EDM'])
    if pValue < 0.001:
        print('**')
    elif pValue < 0.01:
        print(' *')
    print('\n')
    
    # Retrieve the number of topics tackled by papers -------------------------
    paper_topic_map = {'LAK':[], 'EDM':[]}            
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:                                
                clusterIndexes = eleTuple['clusterIndexes']
                paper_topic_map[conference].append(len(clusterIndexes))
    
    # Q3: On average, how many topics are tackled by each paper?        
    print('# Avg. topics investigated by each paper:')
    print('%s\t%.2f' % ('LAK', computAvg(paper_topic_map['LAK']))) 
    print('%s\t%.2f' % ('EDM', computAvg(paper_topic_map['EDM'])))
    _, pValue = mannwhitneyu(paper_topic_map['LAK'], paper_topic_map['EDM'])
    if pValue < 0.001:
        print('**')
    elif pValue < 0.01:
        print(' *')
    print('\n')
    
    # Retrieve the number of citations of papers ------------------------------
    paper_citation_map = {'LAK':[], 'EDM':[]}            
    for conference in conferences:
        for year in years:  
            for eleTuple in data_repository[conference][year]:                                
                num_citations = eleTuple['num_citations']
                paper_citation_map[conference].append(num_citations)
                            
    # Q4: On average, how many citations does each paper has?
    print('# Avg. citations that each paper has:')
    print('%s\t%.2f' % ('LAK', computAvg(paper_citation_map['LAK']))) 
    print('%s\t%.2f' % ('EDM', computAvg(paper_citation_map['EDM'])))
    _, pValue = mannwhitneyu(paper_citation_map['LAK'], paper_citation_map['EDM'])
    if pValue < 0.001:
        print('**')
    elif pValue < 0.01:
        print(' *')
    print('\n')
        
    # Researcher patterns ------------------------------------------------------
    
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
        
        colors = ['#f23557', '#f0d43a', '#22b2da', '#3b4a6b']
        
        for i in range(len(fractions)):
            updated_x_pos = [x+(i-2)*0.23 for x in x_pos]
            plt.bar(updated_x_pos, plotValue_map[fractions[i]], align='edge', color=colors[i], width=0.23, label=str(int(fractions[i]*100)) + '%', linewidth=0.2, edgecolor='#444444')
        
        # x-axis labels
        plt.xticks(x_pos, [str(x+1) for x in x_pos])
        
        plt.xlabel('# Topics')    
        plt.ylabel('# Researchers')
        
        # plt.legend()
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=3, mode="expand", borderaxespad=0.)
    
        title = 'Research patterns (' + authorType + ').png'    
        title = title.replace(" ", "_")
        plt.savefig(data_path + 'LAK_EDM_Comparison/' + title, bbox_inches='tight', pad_inches = 0.05)
        
        plt.show()
    

    
    
    
    


def main():  
    
    data_path = '../../data/'    
    # analyze_research_impact(data_path)
    
    analyze_research_patterns(data_path)
   
if __name__ == "__main__":
    main()