import requests
from bs4 import BeautifulSoup

import datetime
import os
from dotenv import load_dotenv

from helper_files.calendar_creater import (calendar_add_events,
                                           convert_czech_date_to_iso)

from helper_files.proccess_bakalari import (proccess_marks,
                                            calculate_what_do_I_need_to_improve)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import xlsxwriter

load_dotenv()


def scraping_using_python_requests():
    """
    Retrieves the basic html of the specified url.

    Returns:
        None
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
                start = convert_czech_date_to_iso(days[0] + " " + ending)
                end = convert_czech_date_to_iso(days[1] + " " + ending)
            else:
                start = convert_czech_date_to_iso(event[0])
                end = start
        except:
            continue
        name = event[1]
        events.append({"summary": name,
                       "start": {"date": start, 'timeZone': 'Europe/Berlin'},
                       "end": {"date": end, 'timeZone': 'Europe/Berlin'}})
    print(calendar_add_events(events))


def scraping_using_apis():
    """Retrieve information directly from the database using APIs."""
    # Authentication
    def authenticate():
        """Retrieve the token for the API.

        Returns:
            str: The token for the API.
        """
        login = os.getenv("LOGIN")
        password = os.getenv("PASSWORD")
        url = "https://gulz.bakalari.cz/api/login"

        payload = f'client_id=ANDR&grant_type=password&username={login}&password={password}'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ASP.NET_SessionId=20ptxqgvkgffnkvs2jgbqn0s'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            return response.json()["access_token"]
    access_token = authenticate()
    # Get marks
    def get_marks(access_token: str) -> dict:
        """Retrieve the marks from the API.
        Args:
            access_token (str): A valid access token for authenticating with the API.

        Returns:
            dict: The marks from the API.
        """
        url = "https://gulz.bakalari.cz/api/3/marks"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            return response.json()
    marks = get_marks(access_token)

    # Process the marks
    current_vysvedceni = proccess_marks(marks)
    room_for_improvement = False
    for index, (key, value) in enumerate(current_vysvedceni.items()):
        if round(float(value[0].replace(",", "."))) != 1.0:
            room_for_improvement = True
        print(f"{index + 1} {key}: {round(float(value[0].replace(',', '.')))}")
    if room_for_improvement:
        while True:
            improve_subjects = input("""Here is how your mark certificate looks like right now. Would you like to improve it?
If so, state comma separated indexes of the subjects you want to improve: """)
            if improve_subjects:
                try:
                    improve_subjects = map(int, [i.strip() for i in improve_subjects.split(",")])
                    break
                except:
                    "That is not the correct format."
            else:
                print("Well, as you wish!")
                break
    else:
        print("Nothing to be improved, you are doing great, keep it up!")
    if room_for_improvement:
        for index in improve_subjects:
            subject_key = list(current_vysvedceni.keys())[index - 1]
            print(subject_key)
            print("-" * len(subject_key))
            result = calculate_what_do_I_need_to_improve(current_vysvedceni[subject_key][1])
            for key, value in result.items():
                print("If you want to improve to", key)
                for mark in value:
                    print(f"\t You would need Mark: {mark[0]} Weight: {mark[1]}")
            print("-" * len(subject_key))
            print("\n")
    # Check the schedule
    def get_schedule(access_token: str):
        """Retrieve the schedule from the API.
        Args:
            access_token (str): A valid access token for authenticating with the API.

        Returns:
            dict: The schedule from the API.
        """
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        url = f"https://gulz.bakalari.cz/api/3/timetable/actual?date={year}-{month}-{day}"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        result = requests.request("GET", url, headers=headers)
        return result.json()
    day_in_week = datetime.datetime.now().weekday()
    schedule = get_schedule(access_token)["Days"]
    today = schedule[day_in_week]["Atoms"]
    print("Today´s changes in schedule:")
    for d in today:
        s = d["Change"]
        if d["Change"] != None:
            print(s["Hours"], s["ChangeType"], s["Description"])
    # Check absence
    def get_absence(access_token: str):
        """Retrieve the absence from the API.
        Args:
            access_token (str): A valid access token for authenticating with the API.

        Returns:
            dict: The absence from the API.
        """
        url = "https://gulz.bakalari.cz/api/3/absence/student"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        result = requests.request("GET", url, headers=headers)
        return result.json()
    result = get_absence(access_token)
    absences_per_day = result["Absences"]
    absences_per_subject = result["AbsencesPerSubject"]
    for absence in absences_per_day:
        if absence["Unsolved"] != 0:
            print(f"{absence['Date']} - Unresolved: {absence['Unsolved']} hours.")
    for absence in absences_per_subject:
        percentage = absence["Base"] / absence["LessonsCount"] * 100
        if 15 < percentage < 20:
            print(f"Still ok, but getting close: {absence['SubjectName']} - {percentage}%")
        elif percentage >= 20:
            print(f"Might wanna start attending more {absence['SubjectName']} classes. Your absence is {percentage}%")


def scraping_using_selenium():
    """
    Retrieve information using Selenium.

    Returns:
        None
    """
    driver = webdriver.Chrome()
    workbook = xlsxwriter.Workbook("Luxor_books.xlsx")
    worksheet = workbook.add_worksheet("Data")
    database = workbook.add_worksheet("Database")
    wait = WebDriverWait(driver, 10)

    index = 0
    column = 0
    for i in range(1):
        driver.get(f"https://www.luxor.cz/c/9548/knihy?pi={i + 1}")
        time.sleep(2)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-list")))
        books = [book.find_element(By.CLASS_NAME, "product-box").find_element(By.CLASS_NAME, "product-box__title").get_attribute("href") for book in
                 driver.find_element(By.CLASS_NAME, "product-list").find_elements(By.TAG_NAME, "cmp-product-box")]
        for book in books:
            detaily = {}
            driver.get(book)
            time.sleep(2)
            try:
                detaily["title"] = driver.find_element(By.TAG_NAME, "h1").text
            except:
                print(book)
            details = driver.find_elements(By.XPATH, ".//div[@class='detail-info__item']")
            for detail in details[1:]:
                detail = detail.text
                detaily[detail.split(":")[0]] = detail.split(":")[1].strip()
            if not detaily.get("Edice"):
                detaily["Edice"] = ""
            if not detaily.get("Série"):	
                detaily["Série"] = ""
            detaily["current_price"] = driver.find_element(By.XPATH, ".//div[@class='prices__item prices__item--main']").get_attribute("innerHTML").replace("&nbsp;", "")
            try:
                detaily["base_price"] = driver.find_element(By.XPATH, ".//div[@class='prices__base']").find_element(By.XPATH, ".//div[@class='prices__item prices__item--base']").get_attribute("innerHTML").replace("&nbsp;", "")
            except:
                detaily["base_price"] = detaily["current_price"]
            detaily["url"] = book
            detaily["image"] = driver.find_element(By.XPATH, ".//img[@class='lg-object lg-image']").get_attribute("src")
            rezervation_element = driver.find_element(By.XPATH, ".//button[@class='btn-cart btn-cart--reserve btn-cart--big']")
            try:
                rezervation_element.click()
                time.sleep(2)
                possible_pickup = [store.find_element(By.CLASS_NAME, "modal-store-list__title").get_attribute("innerHTML") 
                                for store in driver.find_elements(By.XPATH, ".//div[@class='modal-store-list__item']")]
            except:
                possible_pickup = ["No stores available for reservation."]
            if index == 0:
                for i, key in enumerate(detaily.keys()):
                    worksheet.write(0, i, key)
                index += 1
            for i, value in enumerate(detaily.values()):
                worksheet.write(index, i, value)
            index += 1
            database.write(0, column, detaily["title"])
            for row, pickup in enumerate(possible_pickup):
                database.write(row + 1, column, pickup)
            column += 1
    workbook.close()
            

if __name__ == '__main__':
    scraping_using_python_requests()
    scraping_using_apis()
    scraping_using_selenium()
