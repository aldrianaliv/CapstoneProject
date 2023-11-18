import asyncio
import aiohttp
import csv
import nest_asyncio
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver

nest_asyncio.apply()

# initialize the number of scroll times & waiting time for the webpage to load data
scroll_total = 10
wait_time = 0.3

# Browser initialization
driver = webdriver.Chrome()

url = 'https://kerja.kitalulus.com/id/lowongan?job_functions=&sort_by=isHighlighted'
driver.get(url)
for i in range(scroll_total):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)

html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

# Tutup browser
driver.quit()

# Global variable to maintain the job ID counter
job_id_counter = 0

async def fetch_data(session, url, headers):
  async with session.get(url, headers=headers) as response:
      return await response.text()

async def scrape_page(job_data, soup, headers):
    async with aiohttp.ClientSession() as session:
        global job_id_counter
        job_cards = soup.find_all('div', class_="CardRectangleStyled__Container-sc-1lom4v1-0 blExM")

        for card in job_cards:
            job_link = "https://kerja.kitalulus.com" + card.find('a').get("href")

            company_name = card.find('p', class_='TextStyled__Text-sc-18vo2dc-0 ceCju').text.strip()
            job_title = card.find('p', class_='TextStyled__Text-sc-18vo2dc-0 ldPCOk').text.strip()

            front_detail = card.find_all('p', class_='CardRectangleStyled__Text-sc-1lom4v1-8 esjHJy')

            job_location = front_detail[0].text.strip()
            study_req = front_detail[1].text.strip()
            salary = front_detail[2].text.strip() if len(front_detail) > 2 else "Tidak ditampilkan"

            # From here, proceed to visit the links one by one
            job_response_text = await fetch_data(session, job_link, headers)
            job_soup = BeautifulSoup(job_response_text, 'lxml')
            job_details = {}
            
            job_details['id'] = f"kt{job_id_counter}"  # Assign the generated job ID
            job_id_counter += 1
            
            job_details['Job_title'] = job_title
            job_details['Company'] = company_name
            job_details['Category'] = "Tidak ditampilkan"
            job_details['Location'] = job_location
            
            workt_type_card = job_soup.find('div', class_="VacancyTitleAndInfoStyled__BoxInfo-sc-1rqk80v-6 iKmXIN")
            workt_type_div = workt_type_card.find_all('p', class_="TextStyled__Text-sc-18vo2dc-0 ceCju")
            work_type_string = workt_type_div[1].get_text()
            split_strings = work_type_string.split(" • ")
            job_details['Work_type'] = split_strings[0]
            job_details['Working_type'] = split_strings[1]      
            job_details['Salary'] = salary
            
            exp_card = job_soup.find_all('div', class_="VacancyRequirementStyled__Items-sc-1xx03pf-1 vqqtD")
            exp_div = exp_card[3].find_all('p', class_="TextStyled__Text-sc-18vo2dc-0 ceCju")
            job_details['Experience'] = exp_div[1].get_text()

            skills_box = job_soup.find_all('span', class_="TagStyled__TagContainer-j4aip1-0 dPleZn")

            job_details['Skills'] = ', '.join([box.text.strip() for box in skills_box if box is not None])
            job_details['Study_requirement'] = study_req.replace('Minimal ', '')
            
            # Check if the element is found before calling get_text()
            description_div = job_soup.find('div', class_="VacancyDescriptionStyled__FormattedDescriptionWrapper-sc-13uwtyz-5 iGbbFQ")
            if description_div:
                job_details['Desc'] = description_div.get_text()
            else:
                job_details['Desc'] = ''

            job_details['Link'] = job_link

            job_data.append(job_details)

async def main():
  job_data = []
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
      "Referer": "https://kerja.kitalulus.com/id",
  }
  await scrape_page(job_data, soup, headers)

  if job_data:
      with open('kitalulus-data.csv', 'w', newline='', encoding='utf-8') as csvfile:
          fieldnames = job_data[0].keys()
          writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
          writer.writeheader()
          for job in job_data:
              writer.writerow(job)
      print("Data has been scraped and saved to kitalulus-data.csv")
  else:
      print("No job data found to save.")

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
