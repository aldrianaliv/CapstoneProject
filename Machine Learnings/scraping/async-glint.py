# Control the page number to determine how much data is retrieved
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
import re

# Use regular expression to extract the image ID
pattern_imgLink = re.compile(r'(.*company-logo.)(.*)')

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
            imgLink = card.find('img').get('src')
            
            detail_card = card.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
            dc_list = []
            for dc_element in detail_card:
                text_content = dc_element.text
                dc_list.append(text_content)

            match = pattern_imgLink.search(imgLink)
            if match:
                imgLink = match.group(2)

            job_response_text = await fetch_data(session, job_link, headers)
            job_soup = BeautifulSoup(job_response_text, 'lxml')
            job_details = {}

            exp = "Tidak ditampilkan"
            work_type = "Tidak ditampilkan"
            study_req = "Tidak ditampilkan"

            for element in detail_card:
                text = element.text
                if any(keyword in text.lower() for keyword in ["setahun", "tahun"]):  # Assuming this text is for "experience"
                    exp = text
                elif any(keyword in text.lower() for keyword in ["harian",'magang','penuh waktu','paruh waktu','kontrak']):
                    work_type = text
                elif any(keyword in text.lower() for keyword in ["sma/smk",'diploma','sarjana','magister','sd', 'smp', '(s3)']):
                    study_req = text.replace('Minimal ', '')

            job_details['id'] = f"gl{job_id_counter}" # Assign the generated job ID
            job_id_counter += 1

            job_details['Job_title'] = job_title
            job_details['Company'] = company_name
            job_details['Category'] = dc_list[3] if len(dc_list) > 3 else "Tidak Ditampilkan"
            job_details['Location'] = job_location
            job_details['Work_type'] = work_type 
            job_details['Working_type'] = "Tidak ditampilkan"
            job_details['Salary'] = salary_info
            job_details['Experience'] = exp if exp else "Tidak ditampilkan"

            skills_box = job_soup.find_all('div', class_="TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk")
            skills_box2 = job_soup.find_all('label', class_="TagStyle__TagContent-sc-66xi2f-0 iFeugN tag-content")
            if skills_box:
                skills_text = ', '.join([box.text for box in skills_box if box is not None])
            elif skills_box2:
                skills_text = ', '.join([box.text for box in skills_box2 if box is not None])
            else:
                skills_text = "Tidak ditampilkan"

            job_details['Skills'] = skills_text
            job_details['Study_requirement'] = study_req

            job_desc_div = job_soup.find('ul', class_="public-DraftStyleDefault-ul")
            if job_desc_div:
                job_details['Desc'] = ', '.join([li.text.strip() for li in job_desc_div.find_all('li')])
            else:
                job_details['Desc'] = ''

            job_details['Link'] = job_link
            job_details['Link_img'] = "https://images.glints.com/unsafe/glints-dashboard.s3.amazonaws.com/company-logo/" + imgLink + ';'

            job_data.append(job_details)

async def main():
    base_url = "https://glints.com/id/opportunities/jobs/explore?country=ID&locationName=All+Cities%2FProvinces&sortBy=LATEST"
    page_number = 1
    job_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://glints.com/",
    }

    while page_number < 30:
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
