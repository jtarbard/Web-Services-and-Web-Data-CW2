import os
import sys
import time
import pickle
from urllib.error import HTTPError
from urllib import robotparser, parse
import requests
import random
from bs4 import BeautifulSoup
import string


class InvertedIndex:

    def __init__(self):
        
        self.documents = [] # ["https://example.com/", ...]
        self.postings = {}  # {"posting": {0:1, 1:1, 2:3}}

    def search(self, search_terms):


        # Check against search term conditions
        if type(search_terms) != list:
            tmp = search_terms
            search_terms = []
            search_terms.append(tmp)
            
        for term in search_terms:
            if len(term) < 2:
                sys.exit(f"Search terms of length less than two, '{term}', not accepted.")
        

        # Obtain search results
        search_results = {}
        search_successes = []
        output = {}

        for term in search_terms:
            result = self.postings.get(term)

            if result:
                search_results[term] = result
                search_successes.append(term)
            else:
                sys.exit(f"No results found containing '{term}'.")
            

        for doc_id in search_results.get(search_successes[0]):
            found = True    
            result = {}
            for term in search_results:
                if doc_id not in search_results.get(term).keys():
                    found = False
                result[term] = search_results.get(term).get(doc_id)
            
            if found: 
                output[self.documents[doc_id]] =  result


        # Display search results
        for doc in output:
            print(
                "\n" +
                doc +
                "\n" +
                "Search term occurences - " + 
                str(output.get(doc)).replace("{", "").replace("}", "")
                )
            

    def print(self, term=None):
        if term:
            posting = self.postings.get(term)
            if posting:
                print(
                    f"{term: <30}    " +
                    str(self.postings.get(term)).replace('{','').replace('}','').replace(': ',':')
                    )
            else:
                print(f"No results found containing '{term}'.")
        else:
            for posting in self.postings:
                print(
                    f"{posting: <30}    " +
                    str(self.postings.get(posting)).replace('{','').replace('}','').replace(': ',':')
                    )


class InvertedIndexHandler:

    def __init__(self):
        pass

    def save(self, index):
        try:
            with open("index.pkl", "wb") as f:
                pickle.dump(index, f)

        except Exception as e:
            print("Saving index failed:", e)

    def load(self):
        try:
            with open("index.pkl", "rb") as f:
                return pickle.load(f)

        except Exception as e:
            print("Loading index failed:", e)

    def remove(self):
        if os.path.exists("index.pkl"):
            os.remove("index.pkl")
        else:
            print("Index file could not be deleted as it does not exist.")


class Crawler:

    def __init__(self, index, handler):
        self.index = index
        self.handler = handler

        self.root = ""
        self.frontier = []
        self.scraped = []
        self.delay = 0
        self.req_time = 0


    def robots(self):
        try:
            parser = robotparser.RobotFileParser()
            parser.set_url(parse.urljoin(self.root, "robots.txt"))
            parser.read()
            self.delay = parser.crawl_delay("")

        except Exception as e:
            print("Robots.txt could not be found.", e)
            

    def parse(self, soup, docId):

            text = soup.get_text(separator="\n", strip=True)
            
            content = []
            punc_translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
            digit_translator = str.maketrans(string.digits, ' '*len(string.digits))
            text = text.translate(punc_translator)
            text = text.translate(digit_translator)
            text.replace("\"", "")
            text.replace("'", "")
            content.extend(text.split())

            for text in content:
                if len(text) > 1:

                    if self.index.postings.get(text):
                        if self.index.postings.get(text).get(docId):
                            self.index.postings[text][docId] += 1
                        else:
                            self.index.postings[text][docId] = 1
                    else:
                        self.index.postings[text] = {docId: 1}


    def crawl(self, url):
        try:
            print(f"----> {len(self.scraped): <3} {url: <100}", end="\r")
            
            if self.delay and time.time() - self.req_time >= self.delay:
                req = requests.get(parse.urljoin(self.root, url))
            elif self.delay:
                time.sleep(self.delay - (time.time() - self.req_time))
                req = requests.get(parse.urljoin(self.root, url))
            else:
                req = requests.get(parse.urljoin(self.root, url))
            
            self.req_time = time.time()
            req.raise_for_status()

            soup = BeautifulSoup(req.text, "html.parser")
            self.scraped.append(parse.urljoin(self.root, url))
            doc_id = self.scraped.index(parse.urljoin(self.root, url))
            
            self.parse(soup, doc_id)

            for link in soup.find_all("a"):
                link = link["href"]

                if "http" not in link and link.startswith("/"):
                    link = link.split("?")[0]

                    if parse.urljoin(self.root, link) not in self.scraped and parse.urljoin(self.root, link) not in self.frontier:
                        self.frontier.append(parse.urljoin(self.root, link))

        except requests.exceptions.HTTPError as e:
            if req.status_code == 429:
                print("Too many requests response recieved, increasing delay.")
                self.delay += 1
                time.sleep(self.delay)

        except Exception as e:
            print(e)


    def run(self, seed, polite=True):

        self.root = seed
        if polite:
            self.robots()
        self.frontier.append("/")
        start = time.time()

        while self.frontier != []:
            self.crawl(self.frontier.pop(0))

        self.index.documents = self.scraped
        self.handler.save(self.index)

        print("\nDocuments crawled: "+str(len(self.scraped)))
        print(f"Time taken = {time.time() - start:.10f}")

def main():
    index = InvertedIndex()
    handler = InvertedIndexHandler()
    crawler = Crawler(index, handler)


if __name__ == "__main__":
    main()