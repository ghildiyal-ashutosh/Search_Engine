from extras import * 
from common import Common
from indexer import Indexer
import math
from .baseline_runs import Baseline_Runs
from .query_highlight import Query_Highlight
import operator

class Evaluation:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()
        self.query_highlight = Query_Highlight()
        self.baseline_runs = Baseline_Runs()

    def filter_retrieved_docs(self, docs):
        filtered_docs = []
        for temp in docs:
            doc = temp['doc']
            score = temp['score']
            if score > 0:
                filtered_docs.append({'doc': doc, 'score': score})
        return filtered_docs

    def get_relevant_docs_information(self, snippets, retrieved_docs):
        relevant_docs = {}
        relevancy_count = [0.0]*len(retrieved_docs)
        # generate relevant docs
        for r in retrieved_docs:
            doc = r['doc']
            if doc in snippets:
                relevant_docs[doc] = snippets[doc]

        # generate relevant count
        start = 0.0
        i = 0
        for r in retrieved_docs:
            doc = r['doc']
            relevancy_count[i] = start
            if doc in relevant_docs:
                relevancy_count[i] += 1.0
            start = relevancy_count[i]
            i += 1
        return (relevant_docs, relevancy_count)
    
    def get_precision_in_top_k(self, k, relevancy_count):
        if k > len(relevancy_count):
            return 0.0
        return (relevancy_count[k - 1]/k)

    def get_average_precision(self, relevant_docs, retrieved_docs, relevancy_count):
        total = 0.0
        i = 0
        if len(relevant_docs) == 0:
            return 0.0
        for r in retrieved_docs:
            doc = r['doc']
            if doc in relevant_docs:
                total += (relevancy_count[i]*1.0)/(i + 1)
            i += 1
        return total/len(relevant_docs)

    def get_reciprocal_rank(self, relevant_docs, retrieved_docs):
        i = 0
        for r in retrieved_docs:
            doc = r['doc']
            if doc in relevant_docs:
                return 1.0/(i + 1)
            i += 1
        return 0.0

    def evaluate_model_for_query(self, snippets, retrieved_docs, i, q):
        (relevant_docs, relevancy_count) = self.get_relevant_docs_information(snippets, retrieved_docs)
        recall = len(retrieved_docs)
        precision = len(relevant_docs)
        precision_in_5 = self.get_precision_in_top_k(5, relevancy_count)
        precision_in_20 = self.get_precision_in_top_k(20, relevancy_count)
        average_precision = self.get_average_precision(relevant_docs, retrieved_docs, relevancy_count)
        reciprocal_rank = self.get_reciprocal_rank(relevant_docs, retrieved_docs)
        return (recall, precision, precision_in_5, precision_in_20, average_precision, reciprocal_rank)

    def evaluate_model(self, stem, score, queries, folder, filter_queries=False, query_expansion=None):  
        print('\n' + self.utility.line_break + '\n' +\
            'Evaluating the model: ' + score + '..')  
        mean_average_precision = 0.0
        mean_reciprocal_rank = 0.0    
        query_specific_scores = {}
        for i in range(len(queries)):
            q = queries[i]
            top_docs = self.common.read_top_documents_for_score(stem, folder, i,\
                self.common.top_doc_count, score)
            snippets = self.query_highlight.read_snippets_summary(stem, i, folder, score)
            retrieved_docs = self.filter_retrieved_docs(top_docs)
            (recall, precision,\
                precision_in_5, precision_in_20,\
                average_precision, reciprocal_rank) = self.evaluate_model_for_query(snippets, retrieved_docs, i, q)
            mean_average_precision += average_precision
            mean_reciprocal_rank += reciprocal_rank
            query_specific_scores[q] = {'recall': recall, 'precision': precision,\
                'p_in_5': precision_in_5, 'p_in_20': precision_in_20}
        mean_average_precision /= len(queries)*1.0
        mean_reciprocal_rank /= len(queries)*1.0
        self.save_evaluation_results(score, folder, query_specific_scores,\
            mean_average_precision, mean_reciprocal_rank, filter_queries=filter_queries, query_expansion=query_expansion)

    def save_evaluation_results(self, score, folder,\
        query_scores, mean_average_precision, mean_reciprocal_rank, filter_queries=False, query_expansion=None):
        evaluation_file_path = self.common.get_evaluation_path(self.stem_folder, folder, filter_queries=filter_queries, query_expansion=query_expansion) + '/' + score
        print('\n' + self.utility.line_break + '\n' +\
            'Saving Evaluation scores to ' + evaluation_file_path + '..')
        data = 'Evaluation Scores\n'
        data += self.utility.line_break + '\n' + score + '\n' + self.utility.line_break + '\n'
        data += 'Mean Average Precision:  ' + str(mean_average_precision)  + '\n'
        data += 'Mean Reciprocal Rank:  ' + str(mean_reciprocal_rank)  + '\n'
        data += '\n' + self.utility.line_break + '\nQuery Information\n' + self.utility.line_break + '\n'
        i = 0
        for s in query_scores:
            score = query_scores[s]
            data += 'Q' + str(i + 1) + '  |  Recall:  ' + str(score['recall']) +\
                '  |  Precision:  ' + str(score['precision']) +\
                '  |  Precision@K=5:  ' + str(score['p_in_5']) +\
                '  |  Precision@K=20:  ' + str(score['p_in_20']) + '\n'
            i += 1

        self.file_handling.save_file(data, evaluation_file_path)

    def run(self, stem=False, folder='test-collection'):
        self.stem_folder = 'stem-' if stem else ''
        queries = self.common.get_queries(stem, folder)
        scores = ['bm25', 'binary-independence', 'tf-idf']
        for score in scores:
            self.evaluate_model(stem, score, queries, folder)
            self.evaluate_model(stem, score, queries, folder, filter_queries=True)
            self.evaluate_model(stem, score, queries, folder, query_expansion=True)
            self.evaluate_model(stem, score, queries, folder, query_expansion=False)
            self.evaluate_model(stem, score, queries, folder, filter_queries=True, query_expansion=True)
            self.evaluate_model(stem, score, queries, folder, filter_queries=True, query_expansion=False)