import requests
from bs4 import BeautifulSoup
import datetime
from helper_files.calendar_creater import calendar_add_events

def convert_czech_date_to_iso(czech_date):

    month_map = {
        "leden": "01", "únor": "02", "březen": "03", "duben": "04",
        "květen": "05", "červen": "06", "červenec": "07", "srpen": "08",
        "září": "09", "říjen": "10", "listopad": "11", "prosinec": "12"
    }
        # Split the date string
    parts = czech_date.split()
    day = parts[0].strip(".")
    month = month_map[parts[1].lower()]
    year = parts[2]
    # Construct ISO 8601 string
    iso_date = f"{year}-{month}-{day}"
    return iso_date

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
    events_raw = []
    for row in rows[1:]:
        date = row.find_all("div", class_="mtr-cell-content")[0].find("span").decode_contents()
        name_of_event = row.find_all("div", class_="mtr-cell-content")[1].find("span").decode_contents()
        events_raw.append((date, name_of_event))
    events = []
    for event in events_raw:
        date = event[0]
        if "a" in date.split(" "):
            continue
        try:
            if "–" in date:
                days = "".join(date.split(" ")[:3]).split("–")
                ending = " ".join(date.split(" ")[3:])
                start = days[0] + " " + ending
                end = days[1] + " " + ending
            else:
                start = convert_czech_date_to_iso(event[0])
        except:
            continue
        name = event[1]
        events.append({"summary": name,
                       "start": {"date": start, 'timeZone': 'Europe/Berlin'},
                       "end": {"date": start, 'timeZone': 'Europe/Berlin'}})
    print(calendar_add_events(events))



if __name__ == '__main__':
    scraping_using_python_requests()