import requests
import csv
from bs4 import BeautifulSoup

all_job_listings = []

base_url = "https://glints.com/id/lowongan-kerja"
page_number = 1
url = f"{base_url}?page={page_number}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://glints.com/",
}

while page_number < 20:
    # Send an HTTP GET request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        page_source = response.text  # Get the page content as text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        job_listings = []

        job_titles = soup.find_all('h3', class_='CompactOpportunityCardsc__JobTitle-sc-dkg8my-9 hgMGcy')
        company = soup.find_all('a', class_='CompactOpportunityCardsc__CompanyLink-sc-dkg8my-10 iTRLWx')
        location = soup.find_all('span', class_='CardJobLocation__StyledTruncatedLocation-sc-1by41tq-1 kEinQH')
        work_type = soup.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
        salary = soup.find_all('span', class_='CompactOpportunityCardsc__SalaryWrapper-sc-dkg8my-29 gfPeyg')
        links = soup.find_all('a', class_='CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link')

        for i in range(len(job_titles)):
            job_listing = {
                "Job Title": job_titles[i].text if i < len(job_titles) else "N/A",
                "Company": company[i].text if i < len(company) else "N/A",
                "Location": location[i].text if i < len(location) else "N/A",
                "Work Type": work_type[i].text if i < len(work_type) else "N/A",
                "Salary": salary[i].text if i < len(salary) else "N/A",
                "Link": "https://glints.com" + links[i]["href"] if i < len(links) else "N/A"
            }
            if job_listing not in job_listings:
                job_listings.append(job_listing)
        
        # Append the job listings for this page to the master list
        all_job_listings.extend(job_listings)

        page_number += 1
        url = f"{base_url}?page={page_number}"
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)

# Save job listings to a CSV file
with open('job_listings.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Job Title", "Company", "Location", "Work Type", "Salary", "Link"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()
    
    # Write the data rows
    for job_listing in all_job_listings:
        writer.writerow(job_listing)

print("Job listings have been saved to job_listings.csv")
