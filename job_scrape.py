import requests
from bs4 import BeautifulSoup
import csv

url = "https://glints.com/id/lowongan-kerja"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')


job_cards = soup.find_all("a", class_="CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link")

job_listings = []

for card in job_cards:
    location = card.find("div", class_="CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc").text.strip()
    
    job_response = requests.get("https://glints.com" + card["href"])
    job_soup = BeautifulSoup(job_response.text, 'html.parser')
    
    company = job_soup.find("div", class_="TopFoldsc__JobOverViewCompanyInfo-sc-1fbktg5-4 cTKYTc").text.strip()
    job_title = job_soup.find("div", class_="TopFoldsc__JobOverviewHeader-sc-1fbktg5-24 cuvDWG").text.strip()

    # Add the job details to the list, including the location from the job card
    job_listings.append({'Company': company, 'Job Title': job_title, 'Location': location})



# Save job listings to a CSV file
with open('job_list.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Job Title", "Company", "Location"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()
    
    # Write the data rows
    for job_listing in job_listings:
        writer.writerow(job_listing)

print("Job listings have been saved to job_listings.csv")
