import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv

base_url = "https://www.loker.id/"

job_data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://www.loker.id/",
}

async def fetch_job_data(url, session):
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        job_cards = soup.find_all('div', class_="m-b-40")

        for job_card in job_cards:
            links = job_card.find_all('a', href=True)
            for link in links:
                href_value = link.get('href')[1]
                job_link = href_value
                job_details = {'Links': job_link}

                async with session.get(job_link, headers=headers) as job_response:
                    job_html = await job_response.text()
                    job_soup = BeautifulSoup(job_html, 'html.parser')

                    company_name_element = job_soup.find('div', class_='inline-block margin-right-1em')
                    company_name = company_name_element.text if company_name_element else ""

                    job_title_element = job_soup.find('h1', class_='h2')
                    job_title = job_title_element.text if job_title_element else ""

                    job_details['Company'] = company_name
                    job_details['Job_title'] = job_title

                    location_element = job_soup.select_one('.inline-block a')
                    location = location_element.text if location_element else ""

                    job_details['Location'] = location
                    job_data.append(job_details)

async def main():
    page_number = 1
    async with aiohttp.ClientSession() as session:
        tasks = []
        while page_number < 2:  # Limiting to 1 page for now, change as needed
            url = f"{base_url}cari-lowongan-kerja/page/{page_number}?q&lokasi=0"
            tasks.append(fetch_job_data(url, session))
            page_number += 1
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

    if job_data:
        with open('lokerid-data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to lokerid-data.csv")
    else:
        print("No job data found to save.")
