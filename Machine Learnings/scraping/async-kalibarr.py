import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv

async def fetch_data(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_page(url, headers, job_data, page_number):
    async with aiohttp.ClientSession() as session:
        response_text = await fetch_data(session, url, headers)
        soup = BeautifulSoup(response_text, 'html.parser')

        job_cards = soup.find_all('div', class_="k-font-dm-sans k-rounded-lg k-bg-white k-border-solid k-border hover:k-border-2 hover:k-border-primary-color k-border k-group k-flex k-flex-col k-justify-between css-1otdiuc")
        if not job_cards:
            print(f"No job listings found on page {page_number}. Exiting.")
            return

        for card in job_cards:
            job_link = "https://kalibrr.com" + card.find('a').get("href")
            
            job_response_text = await fetch_data(session, job_link, headers)
            job_soup = BeautifulSoup(job_response_text, 'html.parser')
            job_details = {}


            company_name = job_soup.find('h2', class_='k-inline-block').text.strip()
            job_title = job_soup.find('h1', class_='k-text-title k-inline-flex k-items-center md:k-text-primary-head md:k-flex lg:k-mt-16').text.strip()
            job_location = card.find('div', class_="CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc").text.strip()
            salary_info_element = card.find('span', class_='CompactOpportunityCardsc__SalaryWrapper-sc-dkg8my-29 gfPeyg')
            salary_info = salary_info_element.text.strip() if salary_info_element else "Perusahaan tidak menampilkan gaji"

            job_details['Company'] = company_name
            job_details['Job_title'] = job_title
            job_details['Location'] = job_location
            job_details['Salary'] = salary_info

            elements = card.find('div', class_='TagStyle-sc-r1wv7a-4 bJWZOt CompactOpportunityCardTags__Tag-sc-610p59-1 hncMah')
            for element in elements:
                text = element.text
                if any(keyword in text.lower() for keyword in ["setahun", "tahun"]):  # Assuming this text is for "experience"
                    job_details['Experience'] = text
                elif any(keyword in text.lower() for keyword in ["harian",'magang','penuh waktu','paruh waktu','kontrak']):
                    job_details['Work Type'] = text

            skills_div = job_soup.find('div', class_='Skillssc__TagContainer-sc-1h7ic4i-5 jqLfdz')
            skills = []

            if skills_div:
                skill_tags = skills_div.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
                skills = [skill.text.strip() for skill in skill_tags]
                skills_text = ', '.join(skills)
            else:
                skills_text = ""

            job_details['Skills'] = skills_text

            job_desc_div = job_soup.find('ul', class_="public-DraftStyleDefault-ul")
            if job_desc_div:
                job_details['Descriptions'] = ', '.join([li.text.strip() for li in job_desc_div.find_all('li')])
            else:
                job_details['Descriptions'] = ''

            job_details['Links'] = job_link

            job_data.append(job_details)

async def main():
    base_url = "https://www.kalibrr.com/id-ID/home/all-jobs"
    job_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://www.kalibrr.com/",
    }
    
    while page_number < 5:
        url = f"{base_url}&page={page_number}"
        await scrape_page(url, headers, job_data, page_number)
        page_number += 1

    if job_data:
        with open('async-test.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to job-list-all.csv")
    else:
        print("No job data found to save.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
