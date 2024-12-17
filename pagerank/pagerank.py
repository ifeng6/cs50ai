import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
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
    distribution = {}
    links = corpus[page]
    pages = corpus.keys()
    # if no outgoing links, then all pages have equal probability
    if len(links) == 0:
        for p in pages:
            distribution[p] = (1/len(pages))
        return distribution
    
    # otherwise, initialize pages and with probability `1 - damping_factor`, choose
    # a link at random chosen from all pages in the corpus.
    for p in pages:
        distribution[p] = (1/len(pages)) * (1 - damping_factor)
    # With probability `damping_factor`, choose a link at random linked to by `page`
    for link in links:
        distribution[link] += (1/len(links)) * damping_factor
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = []
    for key in corpus.keys():
        pages.append(key)
    # initialize distributions (we will count how many times a page appears)
    pageranks = {}
    for page in pages:
        pageranks[page] = 0
    # start with a random page
    sample_page = pages[random.randrange(len(pages))]
    # go through n samples
    for _ in range(n):
        # print("---------------------------------")
        # choose next page to sample based on transition model
        distribution = transition_model(corpus, sample_page, damping_factor)
        # print(f"transition model based on page {sample_page}")
        rand_float = random.random()
        overall_proportion = 0
        for page, proportion in distribution.items():
            # print(f"checking page {page}")
            # print(f"rand float is {rand_float}")
            overall_proportion += proportion
            # print(f"overall proportion is {overall_proportion}")
            if rand_float <= overall_proportion:
                sample_page = page
                break
        # print(f"chose {sample_page}")
        pageranks[sample_page] += 1
    # convert from page counts to page ranks
    for page, count in pageranks.items():
        pageranks[page] = count/n
    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageranks = {}
    N = len(corpus)
    # initialize to 1 / N
    for page in corpus.keys():
        pageranks[page] = 1 / N
    # iterate
    converged = False
    while not converged:
        old_pageranks = copy.deepcopy(pageranks)
        for page in pageranks.keys():
            # get pages that have a link to the page in question
            has_link = []
            for origin, links in corpus.items():
                if page in links:
                    has_link.append(origin)
            # calculate new probability
            # cond 1
            prob_choose_from_all = (1 - damping_factor) / N
            # cond 2
            prob_follow_link = 0
            for page_link in has_link:
                prob_page_link = pageranks[page_link]
                num_links = len(corpus[page_link])
                prob_follow_link += prob_page_link / num_links
            # no link pages
            for page_link, links in corpus.items():
                if len(links) == 0:
                    prob_page_link = pageranks[page_link]
                    num_links = N
                    prob_follow_link += prob_page_link / num_links
            prob_follow_link *= damping_factor
            
            pageranks[page] = prob_choose_from_all + prob_follow_link
        # check convergence
        converged = True
        for page, old_prob in old_pageranks.items():
            new_prob = pageranks[page]
            if abs(new_prob - old_prob) > 0.001:
                converged = False
                break
    return pageranks


if __name__ == "__main__":
    main()
