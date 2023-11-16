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

async def fetch_job_data(url, session):
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        job_cards = soup.find_all('div', class_="z1s6m00 _1hbhsw69y _1hbhsw68u _1hbhsw67e _1hbhsw67q")

        for card in job_cards:
            job_link = "https://www.jobstreet.co.id" + card.find('a').get("href")
            async with session.get(job_link, headers=headers) as job_response:
                job_html = await job_response.text()
                job_soup = BeautifulSoup(job_html, 'html.parser')
                job_details = {}

                company_name_element = job_soup.find('span', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7i2 y44q7i21 _1d0g9qk4 y44q7ia')
                company_name = company_name_element.text if company_name_element else ""

                job_title_element = job_soup.find('h1', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7il _1d0g9qk4 y44q7is y44q7i21')
                job_title = job_title_element.text if job_title_element else ""

                job_details['Company'] = company_name
                job_details['Job_title'] = job_title

                # Extract salary information
                salary_elements = job_soup.find_all('span', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7i1 y44q7i21 y44q7ii')
                salaries = [element.get_text(separator=' ').strip() for element in salary_elements if 'IDR' in element.get_text()]

                # Extract location information
                location_element = job_soup.select_one('.z1s6m00._1hbhsw65a._1hbhsw65e._1hbhsw6ga.kt8mbq0 span.z1s6m00._1hbhsw64y.y44q7i0.y44q7i1.y44q7i21.y44q7ii')
                location = location_element.text if location_element else ""

                #Extract Job Type information
                job_type_elements = job_soup.find_all('span', class_= 'z1s6m00 _1hbhsw64y y44q7i0 y44q7i1 y44q7i21 _1d0g9qk4 y44q7ia')
                # Initialize an empty list to store job types
                job_types = []

                # List of keywords to check for in lowercase
                keywords_to_check = ['penuh', 'paruh', 'kontrak', 'magang', 'temporer']

                for element in job_type_elements:
                    text = element.text.lower()  # Convert to lowercase for case-insensitive comparison
                    for keyword in keywords_to_check:
                        if keyword in text:
                            job_types.append(element.text)

                # Join the identified job types with a comma or any desired separator
                job_type = ", ".join(job_types) if job_types else " "
    
                #Extract Job Description
                # Find the div element with data-automation="jobDescription"
                job_description_div = job_soup.find('div', {'data-automation': 'jobDescription'})

                # Initialize a variable to store the scraped text
                scraped_text = ""

                # Check if job_description_div is found before extracting text
                if job_description_div:
                    # Extract text from p and strong elements within job_description_div
                    for element in job_description_div.find_all(['p', 'strong', 'ul', 'li', 'ol']):
                        text = element.get_text(strip=True)
                        scraped_text += text + ', '  # Append text with a newline

                job_details['Location'] = location
                job_details['Salary'] = salaries[0] if salaries else ""
                job_details['Work Type'] = job_type
                job_details['Descriptions'] = scraped_text
                job_details['Links'] = job_link
                job_data.append(job_details)

async def main():
    page_number = 1
    async with aiohttp.ClientSession() as session:
        tasks = []
        while page_number < 2:
            url = f"{base_url}?pg={page_number}"
            tasks.append(fetch_job_data(url, session))
            page_number += 1
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

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
