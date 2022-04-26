import sys
import requests
from bs4 import BeautifulSoup

def find():
    """
    Finds word(s) in the inverted index and returns a list of all
    pages containing those word(s)

    words -- a list of strings to be searched
    """
    pass

def indexPrint():
    """
    Prints the inverted index for a particular word

    Keyword arguments:
    word -- single word to be searched for
    """
    pass

def load():
    """Loads the index from file system"""
    pass


def build(seed):
    """ 
    Builds an inverted index saving it to local file index.txt

    Keyword arguments:
    seed -- url origin point for the crawler
    """
    pass


def main():
    
    # Commands
    if sys.argv[1] == "find":
        pass
    elif sys.argv[1] == "print":
        pass
    elif sys.argv[1] == "load":
        pass
    elif sys.argv[1] == "build":
        pass
    else:
        return "Unknown command line argument, must be one of: 'build', 'load', 'print', or 'find'."
