from extras import * 
from common import Common
from indexer import Indexer
import math
import re
import nltk
import operator
from collections import defaultdict, OrderedDict
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet

class Query_Expansion:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.frequency_map = defaultdict()
        self.synonyms_map = defaultdict()
        self.file_handling = FileHandling()
        self.common = Common()
        self.indexer = Indexer()

    def generate_expected_words_for_expansion(self, queries):
        stopWords = self.utility.get_stop_list()
        stemmer = SnowballStemmer("english")
        for i in range (0,len(queries)):
            query = queries[i]
            listofwords = []
            words = query.split()
            for word in words:
                word = word.lower()
                stem = stemmer.stem(word)
                expected = self.fetch_expected_words(word,stem)
                if expected not in stopWords:
                    frequency = self.generate_frequency_map(word,expected)
                    if frequency > 0:
                        listofwords.append(expected)

            self.frequency_map[i+1] = listofwords
        return self.frequency_map

    def generate_frequency_map(self,word,stem):
        occurrences = 0
        if stem in self.positional_index and word in self.positional_index:
            dict_stem = self.positional_index[stem]
            dict_word = self.positional_index[word]

            for doc in dict_word:
                if doc in dict_stem:
                    list1 = dict_word[doc]
                    list2 = dict_stem[doc]
                    pos1 = 0
                    for i in range(0, len(list1)):
                        pos1 = pos1 + list1[i]
                        pos2 = 0
                        for j in range(0, len(list2)):
                            pos2 = pos2 + list2[j]
                            if abs(pos1 - pos2) <= 12:
                                occurrences = occurrences + 1
                                break
        return occurrences

    def fetch_expected_words(self,word,stem):
        if self.utility.check_word_exist(stem):
            return stem
        else:
            return nltk.stem.WordNetLemmatizer().lemmatize(word)

    def expand_queries_using_stemming(self, queries):
        self.positional_index  = self.indexer.read_index(index_type=True)
        print('\n' + self.utility.line_break + '\n' +\
            'Running Query Expansion using Stemming..')
        stem_map = self.generate_expected_words_for_expansion(queries)
        updated_query_map = defaultdict(set)
        for i in range(len(queries)):
            stop_words = self.utility.get_stop_list()
            listofwords = stem_map[i+1]
            for word in listofwords:
                for syn in wordnet.synsets(word):
                    for l in syn.lemmas():
                        if str(l.name) not in  queries[i] and '_' not in str(l.name) and str(l.name) not in stop_words:
                            updated_query_map[i+1].add(l.name())
                            if (len(updated_query_map[i+1])) > 4:
                                break
                    if len(updated_query_map[i+1]) > 4:
                        break

        new_queries = []

        for i in range (len(queries)):
            old_query = queries[i]
            new_query = old_query
            for word in updated_query_map[i+1]:
                new_query = new_query + " "+ str(word)
            new_queries.append(new_query)
        return new_queries
    
    def create_tf(self,inverted_index):
        tf = {}
        for term in inverted_index:
            c = 0
            doc_to_frequency = inverted_index[term]
            for doc in doc_to_frequency:
                c = c + doc_to_frequency[doc]
            tf[term] = c
        return self.generatePotentialQuery(tf)

    # generating potential query words by evaluating term frequency and removing stop words
    def generatePotentialQuery(self,tf):
        terms = []
        total = 0
        for key, value in tf.items():
            total = total + value
        potentialList = []
        for key, value in tf.items():
            if key not in self.utility.get_stop_list() and len(key) > 4:
                potentialList.append(key)
        return potentialList

    # calculating dice's co-efficient for different terms
    def diceCoff(self,list1, list2, invertedIndex):
        associationDict = {}
        for i in list1:
            if i != "in" and i in invertedIndex:
                docList = invertedIndex[i]
                sum = 0
                for j in list2:
                    docList2 = invertedIndex[j]
                    sum = 0
                    for k in docList2:
                        if k in docList:
                            sum = sum + 1
                    if sum > 10:
                        associationDict[i + "   " + j] = sum * 1.0 / (len(docList) + len(docList2))
        sorted_dict = OrderedDict(associationDict)
        return sorted_dict

    def expand_queries_using_pseduo_relevance(self, queries):
        print('\n' + self.utility.line_break + '\n' +\
            'Running Query Expansion using Pseduo Relevance..')
        docs = self.common.read_top_documents_for_score(top=40)
        relevant_docs = []
        for record in docs:
            relevant_docs.append((record.values()[0]))

        self.indexer.create_save_indexer_with_relevant_docs(relevant_docs)
        inverted_index = self.indexer.read_simple_index()

        potential_list = self.create_tf(inverted_index)
        updated_query_list = []
        
        for i in range(len(queries)):
            query = queries[i]
            query = query.lower()
            words_from_query = []
            word_array = query.split()
            for word in word_array:
                word = re.sub(r'\W+', ' ', word)
                if word not in self.utility.get_stop_list():
                    words_from_query.append(word)
            updatedQuery = query
            suggested_words = self.diceCoff(words_from_query,potential_list,inverted_index).items()
            k = 0
            for value in suggested_words:
                if k > 8:
                    break
                else:
                    words = value[0].split()
                    if words[1] not in updatedQuery:
                        updatedQuery = updatedQuery + ' ' + words[1]
                        k = k + 1
            updated_query_list.append(updatedQuery)
        return updated_query_list