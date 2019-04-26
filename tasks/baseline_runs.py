from extras import * 
from common import Common
from indexer import Indexer
import math
from .query_expansion import *
import operator

class Baseline_Runs:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()
        self.indexer = Indexer()
        self.query_expansion_object = Query_Expansion()

    def run_bm25_for_query_and_document(self, query, doc, total_doc_length, doc_length, total_docs, index):
        k1 = 1.2
        b = 0.75
        k2 = 100.0
        r = 0.0
        R = 0.0
        qf = 1.0
        N = total_docs*1.0
        dl = doc_length*1.0
        avdl = (total_doc_length*1.0)/N
        query_terms = query.split()
        K = k1 * ((1 - b) + (b* (dl/avdl)))
        bm25 = 0.0
        for q in query_terms:
            n = 0.0
            f = 0.0
            if q in index:
                n = len(index[q])*1.0
                if doc in index[q]:
                    f = index[q][doc]*1.0
            bm25 += (math.log(((r + 0.5)/(R - r + 0.5))/((n - r + 0.5)/(N - n - R + r + 0.5))) * (((k1 + 1)*f)/(K + f)) * (((k2 + 1)*qf)/(k2 + qf)))
        return bm25

    def run_bm25(self, queries, folder='test-collection'):
        bm25_path = self.common.get_score_path(self.stem_folder, 'bm25', folder,\
            self.filter_queries, self.query_expansion) + '/'
        doc_length = self.common.get_document_lengths(self.stem_folder, folder)
        total_doc_length = self.common.get_total_document_length(doc_length)
        unigram_path = self.common.get_ngram_path(self.stem_folder, 1, folder)
        docs = self.file_handling.get_all_files(unigram_path)
        index = self.indexer.read_index(folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Processing unigrams index and running BM25...' +\
                '\nProcessed data is available under ' + bm25_path)
        for i in range(len(queries)):
            q = queries[i].lower().strip()
            bm25 = {}
            for d in docs:
                bm25[d] = self.run_bm25_for_query_and_document(q, d,\
                    total_doc_length, doc_length[d], len(docs), index)
            
            self.save_score(bm25_path + str(i), bm25, str(i), 'BM25')

    def get_docs_by_relevancy(self, index, docs, query):
        query_terms = query.split()
        relevant = []
        non_relevant = []
        threshold = 0.3
        total_terms = len(query_terms)*1.0
        for d in docs:
            total = 0.0
            for q in query_terms:
                if q in index and d in index[q]:
                    total += 1.0
            if total/total_terms >= threshold:
                relevant.append(d)
            else:
                non_relevant.append(d)
        return (relevant, non_relevant)

    def get_probability_for_docs(self, index, docs, query):
        query_terms = query.split()
        prob = []
        total_docs = len(docs)*1.0
        for q in query_terms:
            total = 0.0
            for d in docs:
                if q in index and d in index[q]:
                    total += 1.0
            if total_docs == 0:
                prob.append(0.0)
            else:
                prob.append(total/total_docs)
        return prob

    def run_binary_independence_model_for_query_and_document(self, index, doc, query,\
        prob_relevant, non_prob_relevant, prob_relevant_docs, prob_non_relevant_docs):
        query_terms = query.split()
        score = prob_relevant_docs/prob_non_relevant_docs
        for i in range(len(query_terms)):
            q = query_terms[i]
            if q in index and doc in index[q]:
                score *= (prob_relevant[i]/non_prob_relevant[i])
        return score

    # https://web.cs.dal.ca/~anwar/ir/lecturenotes/l4.pdf
    def run_binary_independence_model(self, queries, folder='test-collection'):
        bim_path = self.common.get_score_path(self.stem_folder, 'binary-independence', folder,\
            self.filter_queries, self.query_expansion) + '/'
        unigram_path = self.common.get_ngram_path(self.stem_folder, 1, folder)
        docs = self.file_handling.get_all_files(unigram_path)
        index = self.indexer.read_index(folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Processing unigrams index and running Binary Independence Model.' +\
                '\nProcessed data is available under ' + bim_path)
        for i in range(len(queries)):
            q = queries[i].lower().strip()
            relevant_docs, non_relevant_docs = self.get_docs_by_relevancy(index, docs, q)
            prob_relevant = self.get_probability_for_docs(index, relevant_docs, q)
            non_prob_relevant = self.get_probability_for_docs(index, non_relevant_docs, q)
            len_relevant_docs = len(relevant_docs)
            len_non_relevant_docs = len(non_relevant_docs)
            prob_relevant_docs = (len_relevant_docs*1.0)/(len_relevant_docs + len_non_relevant_docs)
            prob_non_relevant_docs = (len_non_relevant_docs*1.0)/(len_relevant_docs + len_non_relevant_docs)
            bim = {}
            for d in docs:
                bim[d] = self.run_binary_independence_model_for_query_and_document(index, q, d,\
                    prob_relevant, non_prob_relevant, prob_relevant_docs, prob_non_relevant_docs)
            self.save_score(bim_path + str(i), bim, str(i), 'Binary-Independence')

    def run_tf_idf_for_query_and_document(self, index, query, doc, doc_length, total_docs):
        query_terms = query.split()
        total = 0.0
        for q in query_terms:
            tf_idf = 0.0
            if q in index and doc in index[q]:
                tf_idf = (index[q][doc])/(doc_length*1.0)
            if q in index:
                tf_idf *= math.log((total_docs*1.0)/len(index[q]))
            total += tf_idf
        return total

    # http://www.tfidf.com/
    def run_tf_idf(self, queries, folder='test-collection'):
        tf_idf_path = self.common.get_score_path(self.stem_folder, 'tf-idf', folder,\
            self.filter_queries, self.query_expansion) + '/'
        unigram_path = self.common.get_ngram_path(self.stem_folder, 1, folder)
        docs = self.file_handling.get_all_files(unigram_path)
        doc_length = self.common.get_document_lengths(self.stem_folder, folder)
        index = self.indexer.read_index(folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Processing unigrams index and running TF-IDF Model.' +\
                '\nProcessed data is available under ' + tf_idf_path)
        for i in range(len(queries)):
            q = queries[i].lower().strip()
            tf_idf = {}
            for d in docs:
                tf_idf[d] = self.run_tf_idf_for_query_and_document(index, q, d, doc_length[d], len(docs))
            self.save_score(tf_idf_path + str(i), tf_idf, str(i), 'TF-IDF')

    def save_score(self, filename, scores, id, score_type):
        data = ''
        sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        for score in sorted_scores:
            data += id + '  Q0  ' + str(score[0]) + '  ' + str(score[1]) + '  ' + score_type + '\n'
        self.file_handling.save_file(data, filename)

    def run_models(self, queries, folder):
        self.run_bm25(queries, folder)
        self.run_tf_idf(queries, folder)
        self.run_binary_independence_model(queries, folder)

    def run(self, filter_queries=False, query_expansion=None,\
        stem= False, folder= 'test-collection'):
        self.stem_folder = 'stem-' if stem else ''
        self.filter_queries = filter_queries
        self.query_expansion = query_expansion
        queries = self.common.get_queries(stem, folder)
    
        if query_expansion is not None:
            if query_expansion:
                queries = self.query_expansion_object.expand_queries_using_stemming(queries[:])
                # query stemming expansion
            else:
                queries = self.query_expansion_object.expand_queries_using_pseduo_relevance(queries[:])

        if self.filter_queries:
            stopwords = self.common.get_stopwords()
            queries = self.common.filter_stopwords_in_queries(stopwords, queries)
        
        self.run_models(queries, folder)