import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from contextlib import asynccontextmanager

base_url = "https://www.jobstreet.co.id/id/jobs"
job_data = []

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

service = Service('drivers\chromedriver.exe')

async def fetch_job_data(driver, session, headers):
    driver.get(base_url)
    wait = WebDriverWait(driver, 10)

    page_number = 1
    job_id_counter = 0
    job_id_set = set()

    while page_number < 10:  # Assuming scraping 10 pages
        try:
            job_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="app"]/div/div[5]/div/section/div[2]/div/div/div/div/div/div[1]/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div/article')))
            for card in job_cards:
                job_link = card.find_element(By.XPATH, '//*[@id="app"]/div/div[5]/div/section/div[2]/div/div/div/div/div/div[1]/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div/article/div[3]/div/div/div[1]/div/div[1]/div/div/div[2]/div/div[1]/h3/a').get_attribute('href')

                async with session.get(job_link, headers=headers) as job_response:
                    job_html = await job_response.text()
                    job_soup = BeautifulSoup(job_html, 'html.parser')

                    job_details = {}
                    job_id = f"jt{job_id_counter}"
                    if job_id not in job_id_set:
                        job_details['id'] = job_id
                        job_data.append(job_details)
                        job_id_set.add(job_id)
                    job_id_counter += 1

                    job_title_element = job_soup.find('h1', class_='_1wkzzau0')  # Update class name here
                    job_title = job_title_element.text if job_title_element else ""
                    job_details['Job_title'] = job_title

                # Fetch other job details and append to job_data
            # Handle pagination here
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
            next_page_button.click()
            page_number += 1

        except Exception as e:
            print(f"An error occurred: {e}")

@asynccontextmanager
async def chrome_driver():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        yield driver
    finally:
        await driver.quit()

async def scrape_job_data():
    async with aiohttp.ClientSession() as session, chrome_driver() as driver:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
            # Add any other necessary headers here
        }
        await fetch_job_data(driver, session, headers)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_job_data())

    if job_data:
        with open('selenium.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to selenium.csv")
    else:
        print("No job data found to save.")
