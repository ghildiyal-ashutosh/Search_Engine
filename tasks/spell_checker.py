from extras import * 
from common import Common
from indexer import Indexer
import math
import operator
import nltk

class Spell_Checker:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()
        self.indexer = Indexer()

    def get_edit_distance(self, term1, term2):
        return nltk.edit_distance(term1, term2)

    def get_suggestions_for_query_term(self, stopwords, index, q):
        suggested_terms = []
        for i in index:
            if i not in stopwords and not i.isdigit():
                dis = self.get_edit_distance(i, q)
                if dis <= 3 and len(suggested_terms) <= 6:
                    suggested_terms.append(i)
        return '(' + ','.join(suggested_terms) + ')'

    def get_suggestions_for_query(self, stopwords, index, query):
        query_terms = query.split()
        suggested_query_terms = []
        for q in query_terms:
            term = q
            if q not in index and q not in stopwords:
                term = self.get_suggestions_for_query_term(stopwords, index, q)
            suggested_query_terms.append(term)
        return ' '.join(suggested_query_terms)

    def save_suggestions(self, folder, queries):
        suggested_queries_path = self.common.get_suggested_query_path(folder)
        data = ''
        print('\n' + self.utility.line_break + '\n' +\
            'Saving suggestios to ' + suggested_queries_path)
        for q in queries:
            data += 'Initial Query:  ' + q + '\nSuggestions:  ' + queries[q] +\
                '\n' +  self.utility.line_break + '\n\n'

        self.file_handling.save_file(data, suggested_queries_path)

    def run(self, queries, folder='test-collection'):
        print('\n' + self.utility.line_break + '\n' +\
            'Processing the given queries to generate suggestions...\n')
        index = self.indexer.read_index(folder)
        stop_words = self.utility.get_stop_list()
        corrected_queries = {}
        for q in queries:
            print('Processing ' + q + '....')
            corrected_query = self.get_suggestions_for_query(stop_words, index, q)
            corrected_queries[q] = corrected_query

        self.save_suggestions(folder, corrected_queries)