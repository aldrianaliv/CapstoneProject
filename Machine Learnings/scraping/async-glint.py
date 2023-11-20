# Control the page number to determine how much data is retrieved
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv

# Global variable to maintain the job ID counter
job_id_counter = 0
async def fetch_data(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_page(url, headers, job_data, page_number):
    global job_id_counter
    async with aiohttp.ClientSession() as session:
        global job_id_counter
        response_text = await fetch_data(session, url, headers)
        soup = BeautifulSoup(response_text, 'lxml')

        job_cards = soup.find_all('div', class_="JobCardsc__JobcardContainer-sc-hmqj50-0 iirqVR CompactOpportunityCardsc__CompactJobCardWrapper-sc-dkg8my-2 bMyejJ compact_job_card")
        if not job_cards:
            print(f"No job listings found on page {page_number}. Exiting.")
            return

        for card in job_cards:
            job_link = "https://glints.com" + card.find('a').get("href")
            company_name = card.find('a', class_='CompactOpportunityCardsc__CompanyLink-sc-dkg8my-10 iTRLWx').text.strip()
            job_title = card.find('h3', class_='CompactOpportunityCardsc__JobTitle-sc-dkg8my-9 hgMGcy').text.strip()
            job_location = card.find('div', class_="CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc").text.strip()
            salary_info_element = card.find('span', class_='CompactOpportunityCardsc__SalaryWrapper-sc-dkg8my-29 gfPeyg')
            salary_info = salary_info_element.text if salary_info_element else "Tidak ditampilkan"

            job_response_text = await fetch_data(session, job_link, headers)
            job_soup = BeautifulSoup(job_response_text, 'lxml')
            job_details = {}
            
            job_details['id'] = f"gl{job_id_counter}" # Assign the generated job ID
            job_id_counter += 1
            
            job_details['Job_title'] = job_title
            job_details['Company'] = company_name

            detail_card = card.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
            job_details['Category'] = detail_card[3].text
            job_details['Location'] = job_location
            job_details['Work_type'] = detail_card[0].text
            job_details['Working_type'] = "Tidak ditampilkan"
            job_details['Salary'] = salary_info
            job_details['Experience'] = detail_card[1].text
            
            skills_div = job_soup.find('div', class_='Skillssc__TagContainer-sc-1h7ic4i-5 jqLfdz')
            skills = []

            if skills_div:
                skill_tags = skills_div.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
                skills = [skill.text.strip() for skill in skill_tags]
                skills_text = ', '.join(skills)
            else:
                skills_text = "Tidak ditampilkan"

            job_details['Skills'] = skills_text
            job_details['Study_requirement'] = detail_card[2].text.replace('Minimal ', '')

            job_desc_div = job_soup.find('ul', class_="public-DraftStyleDefault-ul")
            if job_desc_div:
                job_details['Desc'] = ', '.join([li.text.strip() for li in job_desc_div.find_all('li')])
            else:
                job_details['Desc'] = ''

            job_details['Link'] = job_link

            job_data.append(job_details)

async def main():
    base_url = "https://glints.com/id/opportunities/jobs/explore?country=ID&locationName=All+Cities%2FProvinces&sortBy=LATEST"
    page_number = 1
    job_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://glints.com/",
    }
    
    while page_number < 2:
        url = f"{base_url}&page={page_number}"
        await scrape_page(url, headers, job_data, page_number)
        page_number += 1

    if job_data:
        with open('glints-data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to glints-data.csv")
    else:
        print("No job data found to save.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
