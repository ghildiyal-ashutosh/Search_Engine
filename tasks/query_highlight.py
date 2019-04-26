from extras import * 
from common import Common
from indexer import Indexer
import math
from .baseline_runs import Baseline_Runs
import operator

class Query_Highlight:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()
        self.indexer = Indexer()
        self.baseline_runs = Baseline_Runs()
        self.threshold_length = 20

    def find_index(self, index, content, end=False):
        if end:
            while index < len(content) and content[index] != ' ' and content[index] != '\n':
                index += 1
            if index >= len(content):
                return len(content)
            return index
        
            while index >= 0 and content[index] != ' ' and content[index] != '\n':
                index -= 1
            if index < 0:
                return 0
            return index - 1

    def get_total_hits(self, result):
        total = 0
        for r in result:
            total += len(result[r])
        return total

    def save_snippets(self, index, query, folder, result, score):
        query_snippet_path = self.common.get_query_snippet_path(self.stem_folder, folder, score) + '/' + str(index)
        data = 'Snippets for the query:  Q' + str(index) + '\n' + self.utility.line_break + '\n'
        total_hits = self.get_total_hits(result)
        print('Saving snippets for ' + query + ' to ' + query_snippet_path + '....')
        if total_hits == 0:
            data += 'No snippets found for the query..'
        else:
            data += 'Total Hits:  ' + str(total_hits) + '\n' + self.utility.line_break + '\n\n'
            for r in result:
                data += self.utility.line_break + '\nDocument:  ' + r + '\n' + self.utility.line_break
                for s in result[r]:
                    data += s + '\n' + self.utility.line_break + '\n'
                data += '\n'
        self.file_handling.save_file(data, query_snippet_path)

    def save_snippets_summary(self, index, query, folder, result, score):
        query_snippet_path = self.common.get_query_snippet_summary_path(self.stem_folder, folder, score) + '/' + str(index)
        data = ''
        for r in result:
            data += r + '  ' + str(len(result[r])) + '\n'
        self.file_handling.save_file(data, query_snippet_path)

    def read_snippets_summary(self, stem, index, folder, score):
        self.stem_folder = 'stem-' if stem else ''
        print('\n' + self.utility.line_break + '\n' +\
            'Reading Snippets Summary...')
        query_snippet_path = self.common.get_query_snippet_summary_path(self.stem_folder, folder, score) + '/' + str(index)
        lines = self.file_handling.read_file_lines(query_snippet_path)
        summary = {}
        for l in lines:
            data = l.split()
            summary[data[0]] = int(data[1])
        return summary        
    
    def find_terms_in_content(self, query_terms, content):
        content_terms = content.split()
        q_terms = 0.0
        t_terms = len(content_terms)*1.0
        for c in content_terms:
            if c in query_terms:
                q_terms += 1.0
        return (q_terms, t_terms)

    def get_snippet(self, beg, end, content):
        beg = self.find_index(beg - self.threshold_length, content)
        end = self.find_index(end + self.threshold_length, content, True)
        return content[beg: end + 1]

    def generate_query_snippet(self, query, content):
        query_terms = query.split()
        query_terms_map = {}
        for q in query_terms:
            query_terms_map[q] = -1
        for q in query_terms:
            term_index = content.find(q)
            query_terms_map[q] = term_index
        score = 0.0
        beg_ind = -1
        end_ind = -1
        snippet = ''
        for i in range(len(query_terms)):
            q1 = query_terms[i]
            if query_terms_map[q1] == -1:
                continue
            for j in range(i + 1, len(query_terms)):
                q2 = query_terms[j]
                if query_terms_map[q2] == -1 or q1 == q2:
                    continue
                beg = q1
                end = q2
                if query_terms_map[end] < query_terms_map[beg]:
                    beg = q2
                    end = q1
                q_terms, t_terms = self.find_terms_in_content(query_terms_map,\
                    content[query_terms_map[beg]: query_terms_map[end]])
                temp_score = (q_terms + 1)**2/(t_terms + 1)
                if temp_score > score:
                    score = temp_score
                    beg_ind = query_terms_map[beg]
                    end_ind = query_terms_map[end] + len(end)
                    snippet = self.get_snippet(beg_ind, end_ind, content)
        return (snippet, beg_ind, end_ind)

    def generate_query_snippets(self, query, folder, doc):
        raw_doc_path = self.common.get_raw_doc_path(self.stem_folder, folder) + '/' + doc
        raw_html_content = self.file_handling.read_file(raw_doc_path)
        html_tags = self.utility.getAllHTMLTags(raw_html_content, 'pre')
        content = ' '.join([x.get_text() for x in html_tags]).lower()
        end = 0
        beg = 0
        snippets = []
        while True:
            snippet, beg, end = self.generate_query_snippet(query, content)
            if beg == -1:
                break
            snippets.append(snippet)
            content = content[end:]
        return snippets

    def highlight_query(self, stem, index, query, folder, score):
        top_docs = self.common.read_top_documents_for_score(stem=stem, folder=folder, query_index=index,\
            top=self.common.top_doc_count, score=score)
        ngrams = self.utility.get_and_process_ngrams(query, 2)
        query_len = len(query)
        result = {}
        len_checked = 0
        print('\nProcessing ' + query + '...')
        for temp in top_docs:
            d = temp['doc']
            snippets = self.generate_query_snippets(query, folder, d)
            if d not in result:
                result[d] = []
            result[d] += snippets
        self.save_snippets_summary(index, query, folder, result, score)
        self.save_snippets(index, query, folder, result, score)

    def highlight_queries(self, score='bm25', folder='test-collection', stem= False, stopwords=[]):
        self.stem_folder = 'stem-' if stem else ''
        queries = self.common.get_queries(stem, folder)
        queries = self.common.filter_stopwords_in_queries(stopwords, queries)

        print('\n' + self.utility.line_break + '\n' +\
            'Processing queries  to generate snippets for ' + score + '...')
        for i in range(len(queries)):
            self.highlight_query(stem, i, queries[i], folder, score)
        

    