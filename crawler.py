from copyreg import pickle
from logging import raiseExceptions
from operator import contains
import sys
import json
import requests
from bs4 import BeautifulSoup

class InvertedIndex:

    def __init__(self):
        self.documents = []
        self.terms = {}

    def print(self):
        pass

    def search(self):
        pass


class Crawler:

    def __init__(self):
        self.queue = []
        self.index = InvertedIndex()

    def build(self, seed):
        self.crawl(seed)

    def load(self):
        try:
            with open("index.pkl", "wb") as f:
                self.index = pickle.load(f)
        except Exception as e:
            raiseExceptions(e)
            exit()

    def updateIndex(self):
        try:
            with open("index.pkl", "wb") as f:
                pickle.dump(self.index)
        except Exception as e:
            raiseExceptions(e)
            exit()

    def crawl(self, url):
        try:
            req = requests.get(url)
            req.raise_for_status()
        
            soup = BeautifulSoup(req.text, "html.parser")
            for link in soup.find_all("a"):
                if url in link:
                    pass
                elif "www." in link:
                    pass # Skip external link
                else:
                    url+link


                if link not in queue:
                    queue.append(link.get("href"))
            
        except Exception as err:
            # log error
            pass


def main():
    
    crawler = Crawler()
    
    while(True):

        command = input()

        if command == "find":
            crawler.index.search()
        elif command == "print":
            crawler.index.print()
        elif command == "load":
            crawler.load()
        elif command == "build":
            seed = input("URL: ")
            crawler.build(seed)
        elif command == "exit":
            exit()
        else:
            print("Unknown command, must be one of: 'build', 'load', 'print', 'find', or 'exit'.")


if __name__ == "__main__":
    main()