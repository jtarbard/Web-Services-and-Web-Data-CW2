import os
import sys
import time
import pickle
import requests
import string
from bs4 import BeautifulSoup

class InvertedIndex:

    def __init__(self):
        self.root = ""
        self.documents = []
        self.index = {}

    def print(self):
        print("Directory Root:"+self.root)
        print(self.documents)
        print(self.index)

    def search(self):
        pass

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

    def prepSeed(self, seed):
        strippedSeed = seed.replace("http://", "")
        strippedSeed = strippedSeed.replace("https://", "")

        self.index.root = strippedSeed.split("/")[0]
        print("ROOT:"+self.index.root)
        print("SEED:"+strippedSeed.replace(self.index.root, ""))
        seed = strippedSeed.replace(self.index.root, "")

        try:            
            req = requests.get("https://"+seed)
            req.raise_for_status()
            
        except Exception as e:
            print("Seed preperation failed:", e) 
            exit()

        return seed

    def request(self, url):
        try:
            req = requests.get("https://"+url)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, "html.parser")

            return soup

        except Exception as e:
            print("Request failed:", e)
            exit()

    def enqueue(self, soup):
        for link in soup.find_all("a"):
            if "www." in link:
                continue

            self.index.documents.append(link)

    def parse(self, soup):
        try:
            navbar = soup.find(class_="navbar").decompose()
        except:
            pass

        allowed_tags = ["p", "a", "span", "h1", "h2", "h3", "h4", "h5", "h6", "li", "dt", "dd"]
        tags = soup.find_all(allowed_tags, recursive=True)
        content = []

        for tag in tags:
            if tag.text != "":
                text = tag.text.translate(str.maketrans("", "", string.punctuation))
                text = " ".join(text.split())
                content.extend(text.split(" "))
        
        print(content)


    def crawl(self, rawSeed, logging=None):

        self.seed = self.prepSeed(rawSeed)
        self.index.documents.append(self.seed)
        
        for link in self.index.documents:
            if logging:
                print(link, end="\r")
            
            time.sleep(1)
            
            soup = self.request("https://"+self.index.root+link)
            self.parse(soup)


def main():
    
    index = InvertedIndex()
    handler = InvertedIndexHandler()
    crawler = Crawler(index, handler)

    if len(sys.argv) == 1:
        print("No command, must be one of: 'build', 'load', 'print', or 'find'.")
    elif  sys.argv[1] == "find":
        index.search()
    elif  sys.argv[1] == "print":
        index.print()
    elif  sys.argv[1] == "load":
        index = handler.load()
    elif  sys.argv[1] == "build":
        if len(sys.argv) > 3:
            crawler.crawl(sys.argv[2], sys.argv[3])
        else:
            crawler.crawl(sys.argv[2])
    else:
        print("Unknown command, must be one of: 'build', 'load', 'print', or 'find'.")


if __name__ == "__main__":
    main()