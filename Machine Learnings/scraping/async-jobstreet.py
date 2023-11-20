import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv

base_url = "https://www.jobstreet.co.id/id/jobs"

job_data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://www.jobstreet.co.id/",
}
job_id_counter = 0
async def fetch_job_data(url, session):
    global job_id_counter
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        job_cards = soup.find_all('div', class_="_1wkzzau0 a1msqi4y a1msqi4w")

        for card in job_cards:
            job_link = "https://www.jobstreet.co.id" + card.find('a').get("href")
            async with session.get(job_link, headers=headers) as job_response:
                job_html = await job_response.text()
                job_soup = BeautifulSoup(job_html, 'html.parser')
                job_details = {}
                # Check if job ID already exists before adding to job_data
                job_id = f"jt{job_id_counter}" # Assign the generated job ID
                if job_id not in job_id_set:
                    job_details['id'] = job_id
                    job_data.append(job_details)
                    job_id_set.add(job_id)
                job_id_counter += 1
                
                
                # Job Title    
                job_title_element = job_soup.find('h1', class_='_1wkzzau0 a1msqi4y lnocuo0 lnocuol _1d0g9qk4 lnocuop lnocuo21')
                job_title = job_title_element.text if job_title_element else ""
                job_details['Job_title'] = job_title

                # Company Name
                company_name_element = job_soup.find('span', class_='_1wkzzau0 a1msqi4y lnocuo0 lnocuo1 lnocuo21 _1d0g9qk4 lnocuod')
                company_name = company_name_element.text if company_name_element else ""
                job_details['Company'] = company_name

                # Extract Working Type
                job_details['Working_type'] = "Tidak ditampilkan"

                # Extract salary information
                salary_elements = job_soup.find_all('span', class_='_1wkzzau0 a1msqi4y a1msqir')
                salaries = [element.get_text(separator=' ').strip() for element in salary_elements if 'Rp' in element.get_text()]
                job_details['Salary'] = salaries[0] if salaries else "Tidak ditampilkan"
                
                # Extract Experience
                job_details['Experience'] = "Tidak ditampilkan"


                # Extract Skill
                job_details['Skills'] = "Tidak ditampilkan"

                # Extract Study Requirement
                job_details['Study_requirement'] = "Tidak ditampilkan"
               
    
                # Extract Job Description
                # Find the div element with data-automation="jobDescription"
                job_description_div = job_soup.find('div', {'data-automation': 'jobAdDetails'})

                # Initialize a variable to store the scraped text
                scraped_text = ""

                # Check if job_description_div is found before extracting text
                if job_description_div:
                    # Extract text from p and strong elements within job_description_div
                    for element in job_description_div.find_all(['p', 'strong', 'ul', 'li', 'ol']):
                        text = element.get_text(strip=True)
                        scraped_text += text + ', '  # Append text with a newline
                job_details['Descriptions'] = scraped_text
                
                
                # Extract Link
                job_details['Link'] = job_link

                # Company Image
                img_tag = job_soup.find('img', class_='_14i2qkq0')
                job_details['Link_img'] = img_tag


async def main():
    page_number = 1
    async with aiohttp.ClientSession() as session:
        tasks = []
        while page_number < 10:
            url = f"{base_url}?page={page_number}"
            tasks.append(fetch_job_data(url, session))
            page_number += 1
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    job_id_set = set()
    loop.run_until_complete(main())

    if job_data:
        with open('jobstreet-data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to jobstreet-data.csv")
    else:
        print("No job data found to save.")
