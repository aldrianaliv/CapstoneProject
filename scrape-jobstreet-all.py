import requests
from bs4 import BeautifulSoup
import csv

# Initialize base URL and page number
base_url = "https://www.jobstreet.co.id/id/jobs"
page_number = 1

job_data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://www.jobstreet.co.id/",
}
while page_number < 5:
    # Create the URL with the current page number
    url = f"{base_url}?pg={page_number}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all job card containers
    job_cards = soup.find_all('div', class_="z1s6m00 _1hbhsw69y _1hbhsw68u _1hbhsw67e _1hbhsw67q")
    if not job_cards:
        print(f"No job listings found on page {page_number}. Exiting.")
        continue  # No more pages to scrape

    for card in job_cards:
        job_link = "https://www.jobstreet.co.id" + card.find('a').get("href")
        job_response = requests.get(job_link, headers=headers)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')
        job_details = {}

        company_name_element = job_soup.find('span', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7i2 y44q7i21 _1d0g9qk4 y44q7ia')
        company_name = company_name_element.text if company_name_element else "Company name not found"
                  
        job_title_element = job_soup.find('h1', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7il _1d0g9qk4 y44q7is y44q7i21')
        job_title = job_title_element.text if job_title_element else "Job Title not found"
        
        job_details['Company'] = company_name
        job_details['Job_title'] = job_title

        # Assuming 'job_soup' contains the parsed HTML

        # Extract salary information
        salary_elements = job_soup.find_all('span', class_='z1s6m00 _1hbhsw64y y44q7i0 y44q7i1 y44q7i21 y44q7ii')
        salaries = [element.get_text(separator=' ').strip() for element in salary_elements if 'IDR' in element.get_text()]

        job_details['Salary'] = salaries[0] if salaries else "No salary information found"

        # Assuming 'job_soup' contains the parsed HTML
        location_element = job_soup.select_one('.z1s6m00._1hbhsw65a._1hbhsw65e._1hbhsw6ga.kt8mbq0 span.z1s6m00._1hbhsw64y.y44q7i0.y44q7i1.y44q7i21.y44q7ii')
        if location_element:
            location = location_element.text

        job_details['Location'] = location 
        job_details['Links'] = job_link
        job_data.append(job_details)

    page_number += 1

if job_data:
    with open('job-list-jobstreet.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = job_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for job in job_data:
            writer.writerow(job)
    print("Data has been scraped and saved to job-list-jobstreet.csv")
else:
    print("No job data found to save.")