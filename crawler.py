import time
import pickle
from urllib.error import HTTPError
from urllib import robotparser, parse
import requests
from bs4 import BeautifulSoup
import string


class InvertedIndex:

    def __init__(self):
        
        self.documents = [] # ["https://example.com/", ...]
        self.postings = {}  # {"posting": {0:1, 1:1, 2:3}}

    def search(self, search_terms):
        if self.postings == {}:
            print("Inverted index is empty.")
            return -1

        if type(search_terms) != list:
            tmp = search_terms
            search_terms = []
            search_terms.append(tmp)

        valid_terms = True
        for term in search_terms:
            if self.postings.get(term) is None:
                valid_terms = False
                print(f"Search term '{term}' could not be found in any documents.")

        if valid_terms == True:
            unvalid_docs = []
            for i in range(len(search_terms)):
                term = search_terms[i]
                
                if i == 0:
                    valid_docs = list(self.postings[term].keys())
                else:
                    for doc_id in valid_docs.copy():
                        if doc_id not in self.postings[term].keys():
                            valid_docs.remove(doc_id)
            
            if valid_docs != []:
                results = {}
                scores = {}
                for doc_id in valid_docs:
                    for term in search_terms:
                        if results.get(self.documents[doc_id]):
                            results[self.documents[doc_id]][term] = self.postings[term][doc_id]
                        else:
                            results[self.documents[doc_id]] = {}
                            results[self.documents[doc_id]][term] = self.postings[term][doc_id]

                        if scores.get(self.documents[doc_id]):
                            scores[self.documents[doc_id]] += self.postings[term][doc_id]
                        else:
                            scores[self.documents[doc_id]] = self.postings[term][doc_id]

                count = 1
                while scores != {}:
                    doc = max(scores, key=scores.get)
                    score = scores.pop(doc)
                    print(f"\n{count}. {doc}")
                    print(f"Relevence Score: {score}, Occurances: {str(results[doc]).replace('{','').replace('}','')}")
                    count += 1

            
            else:
                print(f"No documents that contain all search terms could be found.")


    def print(self, term=None):
        if self.postings == {}:
            print("Inverted index is empty.")
            return -1

        if term:
            posting = self.postings.get(term)
            if posting:
                print(f"{term: <30} {str(self.postings.get(term)).replace('{','').replace('}','').replace(': ',':')}")
            else:
                print(f"No results found containing '{term}'.")
        else:
            for posting in self.postings:
                print(f"{posting: <30} {str(self.postings.get(posting)).replace('{','').replace('}','').replace(': ',':')}\n")


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
            pass
            

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
            if req.status_code == 429 and self.delay > 0:
                self.delay += 1
                time.sleep(self.delay)

        except Exception as e:
            print(e)


    def run(self, seed, polite=True):

        self.root = seed
        if polite == True:
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

    command = None

    while command != "exit":
        command = input("\nCommand: ").split()
        arguments = []
        if len(command) > 1:
            arguments = command[1:]
        command = command[0].lower()

        if command == "build":
            if arguments:
                if len(arguments) > 1:
                    crawler.run(arguments[0], arguments[1])
                else:
                    crawler.run(arguments[0])
            else:
                print("Building inverted index requires a seed as an argument.")
                    
        elif command == "load":
            index = handler.load()
            print("Load Complete.")

        elif command == "print":
            if arguments:
                index.print(arguments[0])
            else:
                index.print()

        elif command == "find":
            if arguments:
                index.search(arguments)
            else:
                print("Find requires search terms as an argument.")

        elif command == "exit":
            pass

        else:
            print("Invalid command. Accepted commands:'build', 'load', 'print', 'find', or 'exit'.")



if __name__ == "__main__":
    main()