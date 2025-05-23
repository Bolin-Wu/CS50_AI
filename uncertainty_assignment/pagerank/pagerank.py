import os
import random
import re
import sys

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
    # raise NotImplementedError
    n_links = corpus[page]
    n_pages = len(corpus)
    distribution = dict()
    for p in corpus:
        distribution[p] = (1 - damping_factor) / n_pages
        if p in n_links:
            distribution[p] += damping_factor / len(n_links)
    return distribution
    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # raise NotImplementedError
    distribution = dict()
    for page in corpus:
        distribution[page] = 0
    page = random.choice(list(corpus.keys()))
    for _ in range(n):
        page = random.choices(list(corpus.keys()), weights=transition_model(corpus, page, damping_factor).values())[0]
        distribution[page] += 1
    for page in distribution:
        distribution[page] /= n
    return distribution

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # raise NotImplementedError
    distribution = dict()
    for page in corpus:
        distribution[page] = 1 / len(corpus)
    while True:
        print(f"Distribution: {distribution}")
        new_distribution = dict()
        for page in corpus:
            new_distribution[page] = (1 - damping_factor) / len(corpus)
            for p in corpus:
                if len(corpus[p]) == 0:
                    new_distribution[page] += damping_factor * distribution[p] / len(corpus)
                elif page in corpus[p]:
                    # If page is linked to by p, add the contribution from p
                    new_distribution[page] += damping_factor * distribution[p] / len(corpus[p])
        print(f"New Distribution: {new_distribution}")
        # Check for convergence
        diff = 0
        for page in new_distribution:
            diff += abs(new_distribution[page] - distribution[page])
        if diff < 0.001:
            break
        distribution = new_distribution
    return distribution


if __name__ == "__main__":
    main()
