from bs4 import BeautifulSoup
import requests
import random
import re
import nltk
from py2casefold import casefold
from nltk.corpus import stopwords, words

"""
Utility Crawler class which is called for all the different
types of crawler  (i.e. DFS, BFS or Focused) This class is open to customization
based on the arguements passed. Furthermore, it can be extended by child classes to
make it more customizable
"""
class Utility:
    
    def __init__(self):
        self.line_break = '************************'

    def process_url(self, url, html):
        """
        Process a URL to get all the Links available on the page
        """
        html = self.getHtmlContent(html, 'content')
        new_urls = self.getValidUrlsFromHtml(html)
        return new_urls

    def getValidUrlsFromHtml(self, content):
        """
        Get all the valid URLs from the given html content
        """
        a_tags = content.find_all('a')
        urls = []
        for a_tag in a_tags:
            url = a_tag.get('href')
            if self.isUrlValid(url):
                urls.append(self.getFilteredUrl(url.lower()))
        return urls

    def isUrlValid(self, url):
        """
        Returns true iff and only if the url passed is valid according to 
        the conditions given in the question
        """
        if url is None:
            return False
        elif url.startswith('//'):
            return False
        elif ':' in url:
            return False
        elif url.startswith('/wiki'):
            return True
        elif 'en.wikipedia.org/wiki/' not in url:
            return False
        return True

    def getFilteredUrl(self, url):
        """
        Filter the URL to return it in it's correct form.
        Removing things like hyperlink on a different section of a page
        or missing https://
        """
        url = url.split('#')[0]
        if url.startswith('/wiki'):
            return ('https://en.wikipedia.org' + url)
        if 'en.wikipedia.org/wiki/' not in url:
            return ('https://en.wikipedia.org/wiki' + url)
        return url

    def getUrlHeader(self, head):
        if head.string is None:
            print('Header not found. Generating a random string.\n')
            return ''.join(random.choice('abcdnefiwnfnwe356435234fgrbeirfnd23435t') for _ in range(10))
        return head.string

    def getHtml(self, url):
        """
        Get HTML Contents from the crawled url.
        Returns the content with the content block only.
        """
        r = requests.get(url)
        html = r.content
        return html

    def getAllHTMLTags(self, html, tag):
        """
        Get HTML Contents from the crawled url.
        Returns all data for the given tag
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find_all(tag)
        return content
    
    def getHTMLTag(self, html, tag):
        """
        Get HTML Contents from the crawled url.
        Returns all the p tags
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find(tag)
        return content

    """
    Gets HTML Content for the given id
    """
    def getHtmlContent(self, html, id = 'body'):
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find(id=id)
        return content

    """
    Parse the given data. Performs Casefolding, and punctation removal
    """
    def parse(self, data):
        # case-fold handled
        data = casefold(data) 
         # encode to utf-8
        data = data.encode('utf-8')
        # punctation removed
        data = re.sub(r'\W+', ' ',  data)       
        # lowercase
        return data.lower().strip()

    """
    Tokenize the data using NLTK Library
    """
    def tokenize(self, data):
        print('Tokenizing...')
        if data is None:
            return ''
        tokens = nltk.word_tokenize(data)
        return ' '.join(tokens)

    """
    Generate trigram for the given data using NLTK Library
    """
    def get_and_process_ngrams(self, data, grams):
        print('Generating ' + str(grams) + '-grams...')
        ngrams = nltk.ngrams(data.split(), grams)
        processed_ngrams = []
        for ng in ngrams:
            if len(ng) > 0:
                processed_ngrams.append(ng)
        return processed_ngrams

    """
    Initialize a dict with the given length and value
    """
    def init_dict(self, keys, value):
        idict = {}
        for k in keys:
            idict[k] = value
        return idict

    def get_random_string(self):
        return ''.join(random.choice('abcdnefiwnfnwe356435234fgrbeirfnd23435t') for _ in range(10))

    def get_stop_list(self):
        return set(stopwords.words('english'))

    def check_word_exist(self, word):
        return word in words.words()