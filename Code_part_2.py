
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import pandas as pd
import os

options = Options()
driver = webdriver.Chrome()
csv_file = "apnews_war_articles.csv"
file_exists = os.path.isfile(csv_file)
data = []
url = f"https://apnews.com/hub/archive"    
driver.get(url)
time.sleep(3)
# page load more
for i in range(600):
     try:
         button = WebDriverWait(driver, 10).until(
             EC.element_to_be_clickable((By.CLASS_NAME, 'Button'))
             )
         button.click()
         print("Button clicked successfully.")
         time.sleep(2) 
     except Exception as e:
        print(f"Could not click button: {e}")
     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
     time.sleep(2)
#data Extracting
soup = BeautifulSoup(driver.page_source, 'html.parser')
articles = soup.find_all(class_='PageList-items-item')
for article in articles:
    title_tag = article.find(class_='PagePromo-title')
    link_tag = article.find(class_='Link')
    time_tag = article.find('bsp-timestamp')
    if time_tag and title_tag:
        title = title_tag.get_text(strip=True)
        link = link_tag['href'] if link_tag else "No link"
        print(link)
        full_link = f"https://apnews.com{link}" if link.startswith("/") else link
        timestamp = int(time_tag['data-timestamp'])
        date = datetime.fromtimestamp(timestamp / 1000).date()
        try:
            driver.get(link)
            time.sleep(3)
            article_soup = BeautifulSoup(driver.page_source, "html.parser")
            desc_tag = article_soup.find("div", class_="Article")
            first_p = desc_tag.find("p") if desc_tag else None
            description = first_p.get_text(strip=True) if first_p else "No description found"
        except Exception as e:
            description = f"Failed to get description: {e}"
        driver.back()
        time.sleep(4)
        articles = driver.find_elements(By.CLASS_NAME, 'PagePromo')
        data.append([title, date, full_link, description])
print("data saved to apnews.csv")      
driver.quit()
# data append
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow(["title", "date", "url", "description"])
    writer.writerows(data)
print(f"{len(data)} new rows added to {csv_file}")
driver.quit()
# dublicate drop
df = pd.read_csv("apnews_war_articles.csv")
df.drop_duplicates(inplace=True)
df.to_csv("apnews_war_articles.csv", index=False)