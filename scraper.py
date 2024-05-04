import re
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup, SoupStrainer
import urllib.robotparser
import lxml
import counter
import urllib.error




# def scraper(url, resp):
#     linky = extract_next_links(url, resp)
#     return [link for link in linky if is_valid(link)]
def scraper(url, resp, counter_obj) -> list:
    # todo: only want to scrape the url and resp given in the parameter. the extract
    # next links function is used to find the subdomains of the url given
    # check text url to see if it has already been scraped before
    # check the parameter url is unique

    linky = extract_next_links(url, resp, counter_obj)
    counter_obj.update_unique_urls(url)
    check_ics_subdomain(resp, counter_obj)
    # for link in linky:
    #     if is_valid(link):
    #         # Normalize URL to handle duplicates based on the final URL form
    #         normalized_link = normalize_url(link)
    #         if subdomain:
    #             if subdomain in counter_obj.subdomain_pages and subdomain != 'www.ics.uci.edu':
    #                 counter_obj.subdomain_pages[subdomain] += 1
    #                 print(f' incremented one to {subdomain}: {normalized_link}')
    #             else:
    #                 counter_obj.subdomain_pages[subdomain] = 1
    #                 print(f'new subdomain to {subdomain}: {normalized_link}')
    return [link for link in linky if is_valid(link)]


def check_ics_subdomain(resp, counter_obj):
    # check if the resp.url is an ics subdomain and if it is, it will update the ics subdomain
    # dictionary of the counter object
    parsed = urlparse(resp.url)
    if parsed.netloc.endswith("ics.uci.edu"):
        counter_obj.update_ics_subdomains(parsed)



# using normalize_url
def extract_next_links(url, resp, counter_obj) -> list:
    links = set()
    if resp.status in range(200, 300):  # Check if the response status is OK
        if not has_minimal_content(resp.raw_response.content):
            print(f"Skipping dead or empty page at {url}")
            return []  # Skip processing this URL
        try:
            soup = BeautifulSoup(resp.raw_response.content, 'lxml')

            # Gets all the page data from the url and resp given
            save_data(resp.url, soup, counter_obj)

            for link in soup.find_all():  # Extract all hyperlinks

                if 'href' in link.attrs:
                    # Correct handling of relative URLs
                    abs_url = urljoin(resp.url, link['href'])
                    normalized_url = normalize_url(abs_url)  # Normalize the URL

                    if is_polite(normalized_url) and is_valid(normalized_url):  # Check the normalized URL
                        links.add(normalized_url)
                        print(f'Link added! {normalized_url}')

            return list(links)

        except Exception as e:
            print(f"Error parsing the content from {url}: {e}")
            return []
    else:
        print(f"Failed to process URL: {url} due to status: {resp.status}")
        return []  # If response is not OK, return an empty list


def is_valid(url) -> bool:
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

        if "php" in parsed.path.lower():
            return False

        # Additional checks can be added here if needed

        return True  # URL is valid
    except TypeError:
        print(f"TypeError for URL: {url}")
        return False


def is_polite(url) -> bool:
    """ Checks if the URL can be fetched according to the robots.txt rules. """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    # Initialize the parser
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)

    try:
        # Attempts to read and parse the robots.txt
        rp.read()
    except urllib.error.HTTPError as e:
        # Handle specific HTTP errors; e.g., 404 not found means no robots.txt
        if e.code == 404:
            print(f"No robots.txt found at {robots_url}: Assuming allowed to fetch.")
            return True
        else:
            print(
                f"HTTP error ({e.code}) when accessing robots.txt at {robots_url}: Assuming allowed to fetch.")
            return True
    except Exception as e:
        # Handle other exceptions that could occur during rp.read()
        print(
            f"Error reading or parsing robots.txt from {robots_url}: {e}. Assuming allowed to fetch.")
        return True

        # If the robots.txt was read successfully, check the fetch rule
    can_fetch = rp.can_fetch('*', url)
    # print(f"Can fetch {url}: {can_fetch}")
    return can_fetch


# first thing in the report number of unique URLs:


# newest version
def normalize_url(url) -> str:
    """Normalize a URL by removing the fragment, lowercasing it, and stripping unnecessary trailing slashes, especially for root domains."""
    parsed_url = urlparse(url)
    # Lowercase the scheme and netloc
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()

    # Handle trailing slashes for the root path
    path = parsed_url.path
    if path == '/' and not parsed_url.params and not parsed_url.query:
        path = ''  # If path is '/' and there are no parameters or query, treat it as an empty path for root domain

    # Reconstruct the URL without the fragment
    normalized_url = urlunparse((scheme, netloc, path, parsed_url.params, parsed_url.query, ''))
    return normalized_url



def has_minimal_content(html_content) -> bool:
    """ Check if the HTML content is empty or trivially small. """
    if len(html_content.strip()) == 0:
        return False
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(strip = True)
    # Check if the text content is too short, indicating a lack of real content
    if len(text) < 50:  # Example threshold, adjust based on typical content length
        return False
    return True





# Function to get and save the data of the websites encountered
def save_data(url, soup, counter_obj):
    counter_obj.update_unique_urls(url)
    counter_obj.add_words(soup, url)
