# Control the page number to determine how much data is retrieved
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
import nest_asyncio

nest_asyncio.apply()

# Global variable to maintain the job ID counter
job_id_counter = 0

async def fetch_data(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_page(url, headers, job_data, page_number):
    async with aiohttp.ClientSession() as session:
        global job_id_counter
        response_text = await fetch_data(session, url, headers)
        soup = BeautifulSoup(response_text, 'lxml')

        job_cards = soup.find_all('div', class_="row opportunity-box")
        if not job_cards:
            print(f"No job listings found on page {page_number}. Exiting.")
            return

        for card in job_cards:
            job_link = "https://karir.com" + card.find('a').get("href")
            company_name = card.find('div', class_='tdd-company-name h8 --semi-bold').text.strip()
            job_title = card.find('h4', class_='tdd-function-name --semi-bold --inherit').text.strip()
            job_location = card.find('span', class_="tdd-location").text.strip()
            category = card.find('span', class_='tdd-company').text.strip()

            # From here, proceed to visit the links one by one
            job_response_text = await fetch_data(session, job_link, headers)
            job_soup = BeautifulSoup(job_response_text, 'lxml')
            job_details = {}

            job_details['id'] = f"kr{job_id_counter}"  # Assign the generated job ID
            job_id_counter += 1
                        
            job_details['Job_title'] = job_title
            job_details['Company'] = company_name
            job_details['Category'] = category
            job_details['Location'] = job_location
            job_details['Work_type'] = "Tidak ditampilkan"
            job_details['Working_type'] = "Tidak ditampilkan"
            salary_raw = job_soup.find('span', class_='salary').text
        	job_details['Salary'] = job_details['Salary'] = "Tidak ditampilkan" if salary_raw == "Gaji Kompetitif" else salary_raw.replace('IDR', 'Rp')
        	
        	experience_text = job_soup.find('li', class_="job--experience").text
        	job_details['Experience'] = "Tanpa pengalaman" if experience_text == "Setidaknya 0 tahun" else experience_text.replace("Setidaknya", "Minimal")

            footer_elements = job_soup.find_all('footer', class_="b-stat__footer")

            job_details['Skills'] = footer_elements[0].text.strip()
            job_details['Study_requirement'] = "Semua jenjang" if footer_elements[4].text.strip() == "Apa Saja" else footer_elements[4].text.strip()

            # Check if the element is found before calling get_text()
            description_card = job_soup.find_all('div', class_="b-matte")
            if description_card:
                desc = description_card[0].get_text() + ' ' + description_card[1].get_text()
                job_details['Desc'] = desc
            else:
                job_details['Desc'] = ''

            job_details['Link'] = job_link

            job_data.append(job_details)

async def main():
    base_url = "https://karir.com/search?"
    page_number = 1
    job_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://karir.com/",
    }

    while page_number < 2:
        url = f"{base_url}&page={page_number}"
        await scrape_page(url, headers, job_data, page_number)
        page_number += 1

    if job_data:
        with open('karirdotcom-data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to karirdotcom-data.csv")
    else:
        print("No job data found to save.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
