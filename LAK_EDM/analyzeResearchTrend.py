'''
Created on 24 Aug 2019

@author: gche0022
'''


import json, re, string
from _collections import defaultdict
from nltk.corpus import stopwords
from nltk import bigrams, trigrams
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer


def preprocess_text_data(stopwords_set, text):
    # print(text)
    # Lower case
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuations
    text = text.translate(str.maketrans('','',string.punctuation))  
    # Remove whitespace & linebreaks  
    text = text.strip() 
    text = text.replace('\n', ' ').replace('\r', '')       
    # Remove stopwords
    tokens = word_tokenize(text)
    tokens = [i for i in tokens if not i in stopwords_set]
    # Stemming
    # stemmer= PorterStemmer()
    # tokens = [stemmer.stem(token) for token in tokens] 
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]                
    # print(tokens)
    # print('')        
    return tokens


def analyzeResearchTrend(data_path):
    
    conferences = ['LAK','EDM']    
    lda_data_array = json.loads(open(data_path + 'LAK_EDM_Comparison/lda_data_array_' + "_".join(conferences) + '.txt', 'r', encoding='utf-8').read())
    
    '''
    # Data format
    lda_data_array.append({'title':title,
                           'abstract':abstract,
                           'citation_count':citation_count,
                           'keywords':keywords,
                           'bodyText':bodyText,
                           'authors_affiliations':authors_affiliations,
                           'RId':RId,
                           'conference':conference,
                           'year':year,
                           'clusters':clusters})
    '''
    
    print('# All papers:\t%d' % len(lda_data_array))
    
    data_repository = dict()
    for year in range(2008,2020):
        data_repository[year] = []
    
    num_trendText = 0   
        
    for eleTuple in lda_data_array:
        trendText = ''        
        for section in eleTuple['bodyText']:
            section_title = section['section_title'].lower().strip()
            section_text = section['section_text']
            
            # if 'limitation' in section_title or \
            #    'discussion' in section_title or \
            #    'future' in section_title:                
            #     trendText += section_text + ' '
            if 'future' in section_title:                
                trendText += section_text + ' ' 
                       
                        
        if trendText != '': 
            num_trendText += 1
            
            year = eleTuple['year']            
            data_repository[year].append(trendText)
    
    print('# papers with Limitation/Discussion/Future:\t%d' % num_trendText)    
    
    # Generate frequent n-grams
    stopwords_set = set(stopwords.words('english'))
    
    for year in range(2015,2020):
        # unigrams &  bigrams & trigrams ---------------------------------------
        unigram_words = defaultdict(int)
        bigram_words = defaultdict(int)
        trigram_words = defaultdict(int)
        
        for trendText in data_repository[year]:
            words = preprocess_text_data(stopwords_set, trendText) 
                
            try:
                for word in set(words):
                    unigram_words[word] += 1
                
                bi_tokens = bigrams(words)
                bi_tokens = set(bi_tokens)
                for bi_token in bi_tokens:
                    bigram_words[bi_token] += 1
                
                tri_tokens = trigrams(words)
                tri_tokens = set(tri_tokens)
                for tri_token in tri_tokens:
                    trigram_words[tri_token] += 1                
            except Exception as e:
                print('Preprocess:\t' + str(e) + '\t' + str(words))
            
        topK = 100
    
        unigram_words = [(k,v) for (k,v) in Counter(unigram_words).most_common(topK)]
        bigram_words = [(k,v) for (k,v) in Counter(bigram_words).most_common(topK)]
        trigram_words = [(k,v) for (k,v) in Counter(trigram_words).most_common(topK)]
        
        # print(bigram_words)
        # print(trigram_words)
    
        unigram_words = [k for (k,v) in unigram_words]
        bigram_words = [" ".join(k) for (k,v) in bigram_words]
        trigram_words = [" ".join(k) for (k,v) in trigram_words]
        
        num_display = 10
        def show_frequent_ngrams(num_display, ngrams):
            printString = ''
            for ngram in ngrams:
                if 'limitation' not in ngram and \
                   'discussion' not in ngram and \
                   'future' not in ngram and \
                   'result' not in ngram and \
                   'et al' not in ngram and \
                   'sydney' not in ngram and \
                   'lak' not in ngram and \
                   'march' not in ngram and \
                   'also' not in ngram and \
                   'nsw' not in ngram and \
                   'science' not in ngram and \
                   'acknowledgment' not in ngram:
                    printString += ngram + '\t'
                    num_display -= 1
                    if num_display == 0:
                        break
            # print(printString)
                    
        # print('Year\t%s' % year)
        # print("\t".join(unigram_words))
        # print("\t".join(bigram_words))
        # print("\t".join(trigram_words))
        
        show_frequent_ngrams(num_display, bigram_words)
        show_frequent_ngrams(num_display, trigram_words)        
        
        print('\n\n')
        
    print('---------------------------------------------------------------')
    years = [2016, 2017, 2018, 2019]
    matchedString = 'paragraph'
    
    #for year in years:
    #    for trendText in data_repository[year]:
    #        
    #        if matchedString in trendText.lower():
    #            print(year)
    #            print(trendText)
    
    for year in years:           
        for eleTuple in lda_data_array:
            if eleTuple['year'] == year:
                checkedText = ''
                for section in eleTuple['bodyText']:
                    section_title = section['section_title'].lower().strip()
                    section_text = section['section_text']
                    if 'future' in section_title:                
                        checkedText += section_text + ' ' 
                        
                if matchedString in checkedText.lower():
                    print(eleTuple['title'])
                    print(eleTuple['conference'])
                    print(checkedText)
                    print('')
    
                
    
   



def main():  
    
    data_path = '../data/'
    
    analyzeResearchTrend(data_path)
    
   
if __name__ == "__main__":
    main()