from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import pandas as pd

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome()

data = []
for i in range(1,3):
    url = f"https://apnews.com/search?q=politics&s=2&p{i}"
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.find_all(class_='PagePromo-content')

    for article in articles:
        title_tag = article.find(class_='PagePromo-title')
        desc_tag = article.find(class_="PagePromo-description")
        link_tag = article.find('a')
        time_tag = article.find('bsp-timestamp')
        if time_tag and title_tag:
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            link = link_tag['href'] if link_tag else "No link"
            description = desc_tag.get_text(strip=True) if desc_tag else "No description"
            full_link = f"https://apnews.com{link}" if link.startswith("/") else link
     
            date_str = time_tag['data-timestamp']
            date_str_2= int(date_str)
            date_have=date_str_2 / 1000
            datetime_obj = datetime.fromtimestamp(date_have)
            date=datetime_obj.date()
            data.append([title, date, link, title])
     # direct data enter into csv file instead of convert data to html than in csv
with open("apnews.csv", mode= "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(data)
print("data saved to apnews.csv")
driver.quit()

df = pd.read_csv("apnews.csv")
df.drop_duplicates(subset=["title"], inplace=True)
df.to_csv("apnews.csv", index=False)

print("Duplicates removed and final data saved.")
