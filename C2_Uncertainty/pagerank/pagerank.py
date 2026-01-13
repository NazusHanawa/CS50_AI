import os
import random
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DAMPING = 0.85
SAMPLES = 10000


def main():
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python pagerank.py corpus")
    directory = BASE_DIR + "/corpus0"
    corpus = crawl(directory)
    
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
        
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    linked_pages = corpus[page]
    
    if len(linked_pages) == 0:
        total_corpus_chance = 1
    else:
        total_corpus_chance = 1 - damping_factor
        
    total_linked_chance = 1 - total_corpus_chance
    
    corpus_chance = total_corpus_chance / len(corpus)
    linked_chance = total_linked_chance / len(linked_pages)
    
    pages_chance = {}
    for page in corpus:
        page_chance = corpus_chance
        if page in linked_pages:
            page_chance += linked_chance
            
        pages_chance[page] = page_chance
    
    return pages_chance


def sample_pagerank(corpus, damping_factor, n):
    """ 
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_pages_tuple = tuple(corpus.keys())
    
    pages_chance = {page: 0 for page in corpus}
    
    next_page = corpus_pages_tuple[0]
    for _ in range(n):
        weights = transition_model(corpus, next_page, damping_factor)
        
        weights_tuple = tuple(weights.values())
        next_page = random.choices(corpus_pages_tuple, weights_tuple)[0]
        
        pages_chance[next_page] += 1 / n
    
    return pages_chance


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    total_pages = len(corpus)
    corpus_chance = (1 - damping_factor) / total_pages

    pagerank = {page: corpus_chance for page in corpus}
    
    backlinks = {}
    for page in corpus:
        for linked_page in corpus[page]:
            if linked_page not in backlinks:
                backlinks[linked_page] = []
            backlinks[linked_page].append(page)    
    
    while True:
        last_pagerank = pagerank.copy()
        
        for p in corpus:
            pagerank[p] = corpus_chance
            for page_linked_to_p in backlinks[p]:
                pagerank[p] += damping_factor * pagerank[page_linked_to_p] / len(corpus[page_linked_to_p])
        
        total_variation = 0
        for page in pagerank:
            variation = abs(last_pagerank[page] - pagerank[page])
            total_variation += variation

        if total_variation < 0.001:
            break
        
    return pagerank
        
if __name__ == "__main__":
    main()
