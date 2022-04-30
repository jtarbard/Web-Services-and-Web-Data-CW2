import os
import sys
import time
import asyncio
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
        seed = strippedSeed.replace(self.index.root, "")

        try:            
            req = requests.get("http://"+self.index.root+seed)
            req.raise_for_status()
            
        except Exception as e:
            print("Seed preperation failed:", e) 
            exit()

        return seed

    def soup(self, url):
        try:
            req = requests.get(url)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, "html.parser")

            return soup

        except Exception as e:
            print("Request failed:", e)
            exit()

    async def enqueue(self, soup):
        for link in soup.find_all("a"):
            link = link["href"]

            if "www." in link:
                continue
            
            link = link.split("?")[0]

            if link in self.index.documents:
                continue

            self.index.documents.append(link)

    async def parse(self, soup, docId):

        allowed_tags = ["p", "a", "span", "h1", "h2", "h3", "h4", "h5", "h6", "li", "dt", "dd", "td"]
        tags = soup.find_all(allowed_tags, recursive=True)
        content = []

        for tag in tags:
            if tag.text != "":
                text = tag.text.translate(str.maketrans("", "", string.punctuation))
                text = text.translate(str.maketrans("", "", string.digits))
                text = " ".join(text.split())
                content.extend(text.split(" "))

        for text in content:
            if self.index.index.get(text):
                self.index.index[text][str(docId)] += 1
            else:
                self.index.index[text] = {str(docId): 1}
        
        
    async def crawl(self, link, docId, logging):
        if logging:
                print(link, end="\n")
            
        soup = self.soup("http://"+self.index.root+link)
        await self.enqueue(soup)
        # await self.parse(soup, docId) 

    async def start(self, rawSeed, logging=None):

        self.seed = self.prepSeed(rawSeed)
        self.index.documents.append(self.seed)
        docId = len(self.index.documents)
        
        for link in self.index.documents:
            await self.crawl(link, docId, logging)
            time.sleep(1)

        self.handler.save(self.index)


async def main():
    
    index = InvertedIndex()
    handler = InvertedIndexHandler()
    crawler = Crawler(index, handler)

    if len(sys.argv) == 1:
        print("No command, must be one of: 'build', 'load', 'print', or 'find'.")
    elif  sys.argv[1] == "find":
        index = handler.load()
        index.search()
    elif  sys.argv[1] == "print":
        index = handler.load()
        index.print()
    elif  sys.argv[1] == "load":
        index = handler.load()
    elif  sys.argv[1] == "build":
        if len(sys.argv) > 3:
            await crawler.start(sys.argv[2], sys.argv[3])
        else:
            await crawler.start(sys.argv[2])
    else:
        print("Unknown command, must be one of: 'build', 'load', 'print', or 'find'.")


if __name__ == "__main__":
    asyncio.run(main())