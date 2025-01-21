import requests

def scraping_using_python_requests(url):
    """
    Retrieves the basic html of the specified url.
    Args:
        url (string): the specified url.
    """
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    print(response)
if __name__ == '__main__':
    scraping_using_python_requests("https://www.gulz.cz/")