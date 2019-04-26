from extras import * 
from tasks import Common
from time import sleep

class Crawler:

    def __init__(self):
        """
        Constructor: Used to initialize all the class variables
        """
        self.utility = Utility()
        self.file_handling = FileHandling()
        self.common = Common()

    def save_document_content(self, folder, tag = 'pre'):
        content_path = self.common.get_doc_content_path(self.stem_folder, folder) + '/'
        raw_html_path = self.common.get_raw_doc_path(self.stem_folder, folder) + '/'
        docs = self.file_handling.get_all_files(raw_html_path)
        print('\n' + self.utility.line_break + '\n' +\
            'Processing the Raw HTML. Parsing and tokenizing the article.' +\
                'Processed data is available under ' + content_path)
        for d in docs:
            print('\nReading ' + d + '...')
            html_content = self.file_handling.read_file(raw_html_path + d)
            content = self.utility.getAllHTMLTags(html_content, tag)
            data = ''
            for c in content:
                data += self.utility.parse(c.get_text()) + ' '
            tokenized_data = self.utility.tokenize(data).strip()
            print('Saving Document content...')
            self.file_handling.save_file(tokenized_data, content_path + d)
    
    def get_header(self, content):
        headers = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        for header in headers:
            content = self.utility.getAllHTMLTags(content, header)
            if len(content) > 0:
                return content[0].get_text().replace(' ', '_')
        return self.utility.get_random_string()

    def crawl_urls(self, folder, urls, stem=False):
        self.stem_folder = 'stem-' if stem else ''
        raw_html_path = self.common.get_raw_doc_path(self.stem_folder, folder) + '/'
        print('\n' + self.utility.line_break + '\n' +\
            'Processing Url and saving the raw html content.' +\
                'Processed data is available under ' + raw_html_path)
        for url in urls:
            html = self.utility.getHtml(url)
            header = self.get_header(html)
            self.file_handling.save_file(html, raw_html_path + header)
            sleep(1)

    def save_doc_length(self, stem=False, folder='test-collection'):
        self.stem_folder = 'stem-' if stem else ''
        gram_path = self.common.get_ngram_path(self.stem_folder, 1, folder) + '/'
        doc_length_file = self.common.get_doc_length_path(self.stem_folder, folder)
        docs = self.file_handling.get_all_files(gram_path)
        data = ''
        print('\n' + self.utility.line_break + '\n' +\
            'Saving document length to .' + doc_length_file)
        for d in docs:
            unigrams = self.file_handling.read_file_lines(gram_path + d)
            doc_length = len(unigrams)
            data += d + ' ' + str(doc_length) + '\n'
        self.file_handling.save_file(data, doc_length_file)

    def process_stem_documents(self, folder='test-collection'):
        content_path = self.common.get_doc_content_path('stem-', folder) + '/'
        stem_doc_path = 'files/' + folder + '/stem.txt'
        print('\n' + self.utility.line_break + '\n' +\
            'Processing the stem text file. Saving each document\'s text separately.' +\
                'Processed data is available under ' + stem_content_path)
        lines = self.file_handling.read_file_lines(stem_doc_path)
        i = 0
        while i < len(lines):
            l = lines[i].split()
            if l[0] == '#' and l[1].isdigit():
                doc_id = 'DOC-' + l[1]
                print('Saving ' + doc_id + '...')
                i += 1
                data = ''
                while True and i < len(lines):
                    l = lines[i].split()
                    if l[0] == '#' and l[1].isdigit():
                        break
                    i += 1
                    line_data = ''.join(l)
                    if line_data.isdigit():
                        continue
                    data += ' '.join(l) + ' '
                self.file_handling.save_file(data, stem_content_path + doc_id)

    def run(self, folder='test-collection', stem=False, tag='p'):
        self.stem_folder = 'stem-' if stem else ''
        self.save_document_content(folder, tag)