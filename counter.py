import re

class Counter:
    def __init__(self):
        self.links = set()
        self.unique_urls = set()
        self.ics_subdomains = {}
        self.words = {}
        self.longest_page = ("url", 0)
        self.stop_words = ["a", "about", "above", "after", "again", "against", "all", "am", "an",
                           "and",
                           "any", "are", "aren't", "as", "at", "be", "because", "been", "before",
                           "being",
                           "below", "between", "both", "but", "by", "can't", "cannot", "could",
                           "couldn't",
                           "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
                           "during",
                           "each", "few", "for", "from", "further", "had", "hadn't", "has",
                           "hasn't",
                           "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
                           "here",
                           "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
                           "i",
                           "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
                           "it's",
                           "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
                           "myself", "no",
                           "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
                           "our",
                           "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
                           "she'd",
                           "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
                           "that",
                           "that's", "the", "their", "theirs", "them", "themselves", "then",
                           "there",
                           "there's", "these", "they", "they'd", "they'll", "they're", "they've",
                           "this",
                           "those", "through", "to", "too", "under", "until", "up", "very", "was",
                           "wasn't",
                           "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
                           "what's",
                           "when", "when's", "where", "where's", "which", "while", "who", "who's",
                           "whom",
                           "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
                           "you'll",
                           "you're", "you've", "your", "yours", "yourself", "yourselves"]

    def update_unique_urls(self, url) -> None:

        # Make sure the url is not in the unique_urls set before adding it
        if url not in self.unique_urls:
            self.unique_urls.add(url)
            print(f"Added a unique url {url}!")
        else:
            print("URL not unique")

    def update_ics_subdomains(self, url):
        if url in self.ics_subdomains:
            self.ics_subdomains[url] += 1
        else:
            self.ics_subdomains[url] = 1

    def add_words(self, soup, url) -> None:
        word_count = 0
        word_pattern = re.compile(r"\b[a-zA-Z\'.]+\b")

        for tag in soup(['script', 'style']):
            tag.decompose()

        for thing in soup.find_all():
            # Extract the text of the element and split it into a list of strings
            wordy = word_pattern.findall(thing.get_text().lower())

            # Go through each word in the list
            for word in wordy:
                word_count += 1

                # Make sure the word is not a stop word
                if word not in self.stop_words:

                    # If the word is already in the word dictionary, increment it, if not set its count to 1
                    if word in self.words:
                        self.words[word] += 1
                    else:
                        self.words[word] = 1

        # Add a check to see if the word count of the current page is longer than the longest page
        if word_count > self.longest_page[1]:
            self.longest_page = (url, word_count)

    def get_50_most_common_words(self):
        # get 50 most common words from the dictionary and return it as a list of tuples with the word and the number



