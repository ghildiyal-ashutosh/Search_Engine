from extras import * 
import re

class Common:
    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.top_doc_count = 100

    def get_suggested_query_path(self, folder):
        return 'files/' + folder + '/spell-checker/query_suggestions'

    def get_evaluation_path(self, stem_folder, folder, filter_queries=False, query_expansion=None):
        filtered = ''
        expansion = ''
        if filter_queries:
            filtered = '/filtered'
        if query_expansion is not None:
            expansion = '/stemming' if query_expansion else '/psuedo-relevance'
        return 'files/' + folder + '/' + stem_folder + 'evaluation'  + filtered + expansion

    def get_raw_doc_path(self, stem_folder, folder):
        return 'files/' + folder + '/documents/' + stem_folder + 'raw-documents'

    def get_doc_content_path(self, stem_folder, folder):
        return 'files/' + folder + '/documents/' + stem_folder + 'document-content'

    def get_query_snippet_path(self, stem_folder, folder, score):
        return 'files/' + folder + '/' + stem_folder + 'snippets/' + score

    def get_query_snippet_summary_path(self, stem_folder, folder, score):
        return 'files/' + folder + '/' + stem_folder + 'snippets/summary/' + score

    def get_doc_length_path(self, stem_folder, folder):
        return 'files/' + folder + '/documents/' + ('stem_' if len(stem_folder) > 0 else '') + 'doc_length'

    def get_score_path(self, stem_folder, score, folder, filter_queries = False, query_expansion=None):
        expansion = ''
        if query_expansion is not None:
            expansion = 'stemming/' if query_expansion else 'psuedo-relevance/'
        filtered = 'stopping/' if filter_queries else ''
        return 'files/' + folder + '/scores/' +  expansion + filtered  + stem_folder + score

    def get_ngram_path(self, stem_folder, gram, folder):
        return 'files/' + folder + '/ngrams/' + stem_folder + 'gram-' + str(gram)

    def get_indexer_path(self, stem_folder, index_type, gram, folder):
        indexer = 'positional' if index_type else 'simple'
        return 'files/' + folder + '/indexes/' + stem_folder  +\
            indexer + '-index/' + 'gram_' + str(gram)

    def get_query_file_path(self, folder='test-collection', stem=False):
         return 'files/' + folder + '/' + ('stem_' if stem else '') + 'query.txt'

    def get_stopwords(self, folder='test-collection'):
        common_words_path = 'files/common_words'
        common_words = self.file_handling.read_file_lines(common_words_path)
        words = {}
        for w in common_words:
            words[w] = True
        return words

    def get_queries(self, stem=False, folder='test-collection'):
        query_file_path = self.get_query_file_path(folder=folder, stem=stem)
        print('\n' + self.utility.line_break + '\n' +\
            'Reading Queries from ' +\
                query_file_path)
        queries = self.file_handling.read_file_lines(query_file_path)
        return [re.sub(r'\W+', ' ',  x).lower() for x in queries]

    def filter_stopwords(self, stopwords, content):
        words = content.split()
        filtered_words = []
        for w in words:
            if w in stopwords:
                continue
            filtered_words.append(w)
        return ' '.join(filtered_words)

    def filter_stopwords_in_queries(self, stopwords, queries):
        filtered_queries = []
        for q in queries:
            filtered_query = self.filter_stopwords(stopwords, q)
            filtered_queries.append(filtered_query)
        return filtered_queries

    def process_test_queries(self):
        test_query_path = 'files/test-collection/unprocessed-query.txt'
        content = self.file_handling.read_file(test_query_path)
        start = 0
        queries = []
        index = content.find('<DOC>', start)
        while index != -1:
            end_index = content.find('</DOC>', start)
            temp_query = content[start + 5: end_index]
            doc_no_index = temp_query.find('</DOCNO>')
            query = temp_query[doc_no_index + 8:]
            queries.append(' '.join(query.split()))
            start = end_index + 6
            index = content.find('<DOC>', start)
        self.save_test_queries(queries)

    def save_test_queries(self, queries):
        test_query_path = 'files/test-collection/query.txt'
        data = ''
        for q in queries:
            data += q + '\n'
        self.file_handling.save_file(data, test_query_path)

    def read_top_documents_for_score(self, stem = False, folder='test-collection', query_index = 0,\
        top = 100, score='bm25', filter_queries=False, query_expansion=False):
        stem_folder = 'stem-' if stem else ''
        model_file_path = self.get_score_path(stem_folder, score, folder, filter_queries=filter_queries, query_expansion=query_expansion) + '/' + str(query_index)
        lines = self.file_handling.read_file_lines(model_file_path)
        top_docs = []
        i = 0
        for l in lines:
            if i == top:
                break
            data = l.split()
            top_docs.append({'doc': data[2], 'score': data[3]})
            i += 1
        return top_docs

    def get_document_lengths(self, stem_folder, folder):
        doc_length_file = self.get_doc_length_path(stem_folder, folder)
        lines = self.file_handling.read_file_lines(doc_length_file)
        doc_length = {}
        for l in lines:
            data = l.split()
            doc_length[data[0]] = int(data[1])
        return doc_length

    def get_total_document_length(self, doc_length):
        total = 0.0
        for d in doc_length:
            total += doc_length[d]
        return total