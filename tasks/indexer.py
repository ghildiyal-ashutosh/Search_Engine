from extras import * 
from common import Common

class Indexer:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()

    def update_index(self, grams, doc):
        for i in range(len(grams)):
            gram = grams[i]
            if gram.strip() is '':
                continue
            if gram not in self.indexer:
                self.indexer[gram] = {}
            if doc not in self.indexer[gram]:
                self.indexer[gram][doc] = []
            ln = len(self.indexer[gram][doc])
            ind = i
            if ln > 0:
                ind += self.indexer[gram][doc][ln - 1]
            self.indexer[gram][doc].append(ind)

    def create_indexer(self, path, docs):
        for d in docs:
            print('Updating the index with ' + d + '...')
            content = self.file_handling.read_file_lines(path + d)
            self.update_index(content, d)

    def create_save_indexer(self, folder, grams):
        for gram in grams:
            self.indexer = {}
            print('\n' + self.utility.line_break + '\n' +\
            'Processing the ' + str(gram) + '-grams to create a index.')
            ngram_path = self.common.get_ngram_path(self.stem_folder, gram, folder) + '/'
            docs = self.file_handling.get_all_files(ngram_path)
            self.create_indexer(ngram_path, docs)
            self.save_index(folder, gram)
            self.save_index(folder, gram, True)

    def create_save_indexer_with_relevant_docs(self, docs, stem=False, folder='test-collection', grams=[1]):
        self.stem_folder = 'stem-' if stem else ''
        for gram in grams:
            self.indexer = {}
            print('\n' + self.utility.line_break + '\n' +\
            'Processing the ' + str(gram) + '-grams to create a index using the relevant documents.')
            ngram_path = self.common.get_ngram_path(self.stem_folder, gram, folder) + '/'
            self.create_indexer(ngram_path, docs)
            self.save_index(folder, gram)
            self.save_index(folder, gram, True)

    def save_index(self, folder, gram, positional = False):
        indexer_file = self.common.get_indexer_path(self.stem_folder,\
            True if positional else False, gram, folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Saving ' + ('positional' if positional else 'simple') + ' index..' + '\n' +\
            'Processed data is available under ' + indexer_file)
        data = ''
        for term in self.indexer:
            data += term + ' ' + str(len(self.indexer[term])) + '\n'
            for doc in self.indexer[term]:
                data += doc + ' ' + str(len(self.indexer[term][doc])) + '\n'
                if positional:
                    data += ','.join([str(x) for x in self.indexer[term][doc]]) + '\n'
        self.file_handling.save_file(data, indexer_file)

    def read_simple_index(self, folder='test-collection', gram=1): 
        indexer_file = self.common.get_indexer_path(self.stem_folder, False, gram, folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Reading simple index from ' + indexer_file)
        lines = self.file_handling.read_file_lines(indexer_file)
        indexer = {}
        i = 0
        while i < len(lines):
            data = lines[i].split()
            term = data[0]
            indexer[term] = {}
            doc_freq = int(data[1])
            i += 1
            for j in range(doc_freq):
                data = lines[i].split()
                indexer[term][data[0]] = int(data[1])
                i += 1 
        return indexer

    def read_positional_index(self, folder='test-collection', gram=1):
        indexer_file = self.common.get_indexer_path(self.stem_folder, True, gram, folder)
        print('\n' + self.utility.line_break + '\n' +\
            'Reading positional index from ' + indexer_file)
        lines = self.file_handling.read_file_lines(indexer_file)
        indexer = {}
        i = 0
        while i < len(lines):
            data = lines[i].split()
            term = data[0]
            indexer[term] = {}
            doc_freq = int(data[1])
            i += 1
            for j in range(doc_freq):
                data = lines[i].split()
                i += 1
                positions = lines[i].split(',')
                indexer[term][data[0]] = [int(x) for x in positions]
                i += 1
        return indexer

    def read_index(self, folder='test-collection', index_type=False, stem=False, gram=1):
        self.stem_folder = 'stem-' if stem else ''
        if index_type:
            return self.read_positional_index(folder, gram)
        return self.read_simple_index(folder, gram)

    def run(self, stem= False, folder='test-collection', grams=[1]):
        self.stem_folder = 'stem-' if stem else ''
        self.create_save_indexer(folder, grams)