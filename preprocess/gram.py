from extras import * 
from tasks import Common

class Gram:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()
        self.stopwords = {}

    def set_stopwords(self, stopwords):
        self.stopwords = stopwords

    def get_ngrams_formatted(self, ngrams):
        data = ''
        for n in ngrams:
            data += ('$'.join(n)) + '\n'
        return data

    def generate_n_grams(self, folder, gram = 1):
        content_path = self.common.get_doc_content_path(self.stem_folder, folder) + '/'
        gram_path = self.common.get_ngram_path(self.stem_folder, gram, folder) + '/'
        docs = self.file_handling.get_all_files(content_path)
        print('\n' + self.utility.line_break + '\n' +\
            'Processing the document content to create ' + str(gram) + '-grams.' +\
                'Processed data is available under ' + gram_path)
        for d in docs:
            print('\nReading ' + d + '...')
            content = self.file_handling.read_file(content_path + d)
            content = self.common.filter_stopwords(self.stopwords, content)
            ngrams = self.utility.get_and_process_ngrams(content, gram)
            data = self.get_ngrams_formatted(ngrams)
            print('Saving ' + str(gram) + '-grams...')
            self.file_handling.save_file(data, gram_path + d)

    def run(self, stem = False, folder = 'test-collection', grams = [1]):
        self.stem_folder = 'stem-' if stem else ''
        for g in grams:
            self.generate_n_grams(folder, g)

