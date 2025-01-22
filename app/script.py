import requests
from bs4 import BeautifulSoup


def scraping_using_python_requests():
    """
    Retrieves the basic html of the specified url.
    Args:
        url (string): the specified url.
    """
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = "https://www.gulz.cz/"
    response = requests.get(url, headers=headers)
    #print(response.content)
    url += "studenti-a-rodice/organizace-skolniho-roku/"
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="mtr-table mtr-tr-th")
    rows = table.find_all("tr")
    for row in rows[1:]:
        date = row.find_all("div", class_="mtr-cell-content")[0].find("span").decode_contents()
        name_of_action = row.find_all("div", class_="mtr-cell-content")[1].find("span").decode_contents()
        print(date, name_of_action)

if __name__ == '__main__':
    scraping_using_python_requests()