import re
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup, SoupStrainer
import urllib.robotparser
import lxml

# def can_parse(url):
#     pass
# def can_parse(url):
#     parsed = urlparse(url)
#     # Define which file extensions or URL patterns should not be parsed.
#     if re.match(
#         r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|"
#         r"wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ps|eps|tex|ppt|"
#         r"pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|"
#         r"7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|"
#         r"csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
#         return False  # URL points to a file type that typically does not contain HTML content.
#
#     # Ensure URL points to a parsable HTTP or HTTPS page
#     if parsed.scheme in ["http", "https"]:
#         return True  # The scheme indicates that the URL could point to an HTML page.
#
#     return False  # Default to not parse if the URL scheme is not HTTP/HTTPS or it's a file type we do not want to parse.

links = set()

def scraper(url, resp):
    linky = extract_next_links(url, resp)
    return [link for link in linky if is_valid(link)]


def extract_next_links(url, resp):
    global links
    if resp.status in range(200, 300):  # Check if the response status is OK
        try:
            soup = BeautifulSoup(resp.raw_response.content, 'lxml')
            for link in soup.find_all('a', href=True):  # Extract all hyperlinks
                # Correct handling of relative URLs
                abs_url = urljoin(resp.url, link['href'])
                if is_polite(link) and is_valid(link):
                    if abs_url not in links:
                        links.add(abs_url)
                        print(f"Extracted URL: {abs_url}")  # Diagnostic print
            return list(links)
        except Exception as e:
            print(f"Error parsing the content from {url}: {e}")
            return []
    else:
        print(f"Failed to process URL: {url} due to status: {resp.status}")
        return []  # If response is not OK, return an empty list


# def extract_next_links(url, resp):
#     links = []
#     if resp.status in range(200, 300):  # Check if the response status is ok
#         try:
#             soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
#             for link in soup.find_all('a', href=True):  # Extract all hyperlinks
#                 abs_url = urljoin(url, link['href'])
#                 if is_valid(abs_url): #checks if valid
#                     links.append(abs_url)
#                     print(f"Valid URL extracted: {abs_url}")
#                     return links
#
#         except Exception as e:
#             print(f"Error parsing the content from {url}: {e}")
#     else:
#         print(f"Failed to process URL: {url} due to status: {resp.status}")
#         return links
#
# def normalize_url(url):
#     parsed_url = urlparse(url)
#     return urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", parsed_url.path)
#
# def get_domain(url):
#     parsed_url = urlparse(url)
#     return parsed_url.netloc
#
# def get_subdomain(url):
#     netloc = get_domain(url)
#     parts = netloc.split('.')
#     if len(parts) > 2:
#         return parts[0] + '.' + '.'.join(parts[1:])
#     return netloc


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
        if parsed.scheme not in {"http", "https"}:
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
        return False


def is_polite(url, user_agent='IR US24 47244932,40311531,89287168,62769628'):
    """ Checks if the URL can be fetched according to the robots.txt rules. """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    # Initialize the parser
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)

    try:
        # Fetches and parses the robots.txt file
        rp.read()
        # Check if the URL is allowed for the specified user agent
        can_fetch = rp.can_fetch(user_agent, url)
        print(f"Can fetch {url}: {can_fetch}")
        return can_fetch
    except Exception as e:
        print(f"Error reading or parsing robots.txt from {robots_url}: {e}")
        # Assume allowed if robots.txt is unreachable or there's an error parsing it
        # This is a common practice in web crawling to default to allowing access when robots.txt cannot be processed
        return True

#first thing in the report number of unique URLs:
def normalize_url(url):
    """ Normalize a URL by removing the fragment and lowercasing it. """
    parsed_url = urlparse(url)
    # Reconstruct the URL without the fragment
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, ''))
    return clean_url.lower()

# Initialize a set to track unique URLs
unique_urls = set()

def add_url(url):
    normalized = normalize_url(url)
    unique_urls.add(normalized)

