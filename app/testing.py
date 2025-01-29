import requests
import os
from datetime import datetime


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
headers = {
    'Authorization': f'Bearer {access_token}'
}
url = "https://gulz.bakalari.cz/api/3/absence/student"
result = requests.request("GET", url, headers=headers)
absences_per_day = result.json()["Absences"]
absences_per_subject = result.json()["AbsencesPerSubject"]
for absence in absences_per_day:
    if absence["Unsolved"] != 0:
        print(f"{absence["Date"]} - Unresolved: {absence["Unsolved"]} hours.")
for absence in absences_per_subject:
    percentage = absence["Base"] / absence["LessonsCount"] * 100
    if 15 < percentage < 20:
        print(f"Still ok, but getting close: {absence["SubjectName"]} - {percentage}%")
    elif percentage >= 20:
        print(f"Might wanna start attending more {absence["SubjectName"]} classes. Your absence is {percentage}%")
    

    


