from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time

# 1. Initialize Driver
driver = webdriver.Chrome() 

# 2. Login (Manual or automated)
driver.get("https://www.linkedin.com/login")

username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")

username_field.send_keys("putrabina0@gmail.com")
password_field.send_keys("Scr@pG@s123")

time.sleep(10)

login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()

time.sleep(10)

# linkedin_scraper('https://api.scraperapi.com?api_key=d8373ff0b8ada8d4b604c1069c022019&url=htasdps://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Product%20Management&location=San%20Francisco%20Bay%20Area&geoId=90000084&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start=', 0)