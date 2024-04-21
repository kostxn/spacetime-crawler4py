import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import requests


# def can_parse(url):
#     pass
def can_parse(url):
    parsed = urlparse(url)
    # Define which file extensions or URL patterns should not be parsed.
    if re.match(
        r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|"
        r"wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ps|eps|tex|ppt|"
        r"pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|"
        r"7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|"
        r"csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
        return False  # URL points to a file type that typically does not contain HTML content.

    # Ensure URL points to a parsable HTTP or HTTPS page
    if parsed.scheme in ["http", "https"]:
        return True  # The scheme indicates that the URL could point to an HTML page.

    return False  # Default to not parse if the URL scheme is not HTTP/HTTPS or it's a file type we do not want to parse.


def scraper(url, resp):
    # links = extract_next_links(url, resp)
    # return [link for link in links if is_valid(link)]
    pass

def extract_next_links(url, resp):
    if resp.status in range(200, 300):  # Check if the response status is OK
        try:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            links = set()
            for link in soup.find_all('a', href=True):  # Extract all hyperlinks
                abs_url = urlparse(link['href'], scheme=resp.raw_response.url.scheme, allow_fragments=False)
                if abs_url.netloc == '':  # Handle relative URLs
                    abs_url = resp.raw_response.urljoin(link['href'])
                else:
                    abs_url = abs_url.geturl()
                links.add(abs_url)
            return list(links)
        except Exception as e:
            print(f"Error parsing the content from {url}: {e}")
            return []
    else:
        return []  # If response is not OK, return an empty list

# def is_valid(url):
#     # Decide whether to crawl this url or not.
#     # If you decide to crawl it, return True; otherwise return False.
#     # There are already some conditions that return False.
#     try:
#         parsed = urlparse(url)
#         if parsed.scheme not in set(["http", "https"]):
#             return False
#         return not re.match(
#             r".*\.(css|js|bmp|gif|jpe?g|ico"
#             + r"|png|tiff?|mid|mp2|mp3|mp4"
#             + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
#             + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
#             + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
#             + r"|epub|dll|cnf|tgz|sha1"
#             + r"|thmx|mso|arff|rtf|jar|csv"
#             + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
#
#     except TypeError:
#         print ("TypeError for ", parsed)
#         raise
def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if re.match(r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4"
                    r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ps|eps|tex|ppt"
                    r"|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin"
                    r"|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar"
                    r"|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False  # Filter out URLs pointing to non-html files

        # Target domains
        if not re.search(
                r"^(.+\.)?(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu)$",
                parsed.netloc):
            return False

        # Additional checks can be added here if needed

        return True  # URL is valid
    except TypeError:
        print(f"TypeError for URL: {url}")
        raise
