import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
import re
import time
import csv

# Define the base URL for job listings
base_url = 'https://glints.com/id/lowongan-kerja'
page_number = 1  # Start with the first page

job_urls = []  # Initialize a list to store job URLs
job_data = []

# Save the scraped job URLs to a CSV file
while True:
    # Construct the URL with the current page number
    url = f"{base_url}&page={page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Check if there are job postings on the current page
    job_listings = soup.find_all('div', class_='JobCardsc__JobcardContainer-sc-hmqj50-0 iirqVR CompactOpportunityCardsc__CompactJobCardWrapper-sc-dkg8my-2 bMyejJ compact_job_card')
    
    if not job_listings:
        # No more job listings on the page, exit the loop
        break

    # Iterate through job listings on the current page
    for job_listing in job_listings:
        # Extract the URL of the current job listing
        job_url = 'https://www.glints.com' + job_listing.find('a', class_='CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link')['href']
        job_urls.append(job_url)

    # Increment the page number for the next page
    page_number += 1

# Append the scraped job URLs to a CSV file
with open('ScrapedJobURLs.csv', 'a', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for url in job_urls:
        csv_writer.writerow([url])

# Iterate through job URLs and extract details
for job_url in job_urls:
    response = requests.get(job_url)
    job_soup = BeautifulSoup(response.content, 'html.parser')
    
    job_details = {}
    
    # Extract job details from the current job URL
    job_details['Name'] = job_soup.find('h1', class_='TopFoldsc__JobOverViewTitle-sc-1fbktg5-3 fwLnaN').text
    job_details['Company'] = job_soup.find('a', class_='TopFoldsc__JobOverViewCompanyName-sc-1fbktg5-5 gvAbxa').text
    job_details['Location'] = soup.find('div', class_='CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc').text
    job_details['Salary'] = job_soup.find('div', class_='TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 TopFoldsc__SalaryJobOverview-sc-1fbktg5-29 iqoKuL cmcyYP').text
    job_details['Experience'] = job_soup.find('div', class_='TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL').text
    job_details['Type'] = job_soup.find('div', class_='TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL').text
    job_details['Field'] = job_soup.find('div', class_='TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL').text
    job_details['Posted'] = job_soup.find('span', class_='TopFoldsc__PostedAt-sc-1fbktg5-13 jCcQeG').text
    job_details['Updated'] = job_soup.find('span', class_='TopFoldsc__UpdatedAt-sc-1fbktg5-14 donikX').text
    j# Find the parent div element containing the skills
    skills_div = job_soup.find('div', class_='Skillssc__TagContainer-sc-1h7ic4i-5 jqLfdz')
     # Initialize a list to store the extracted skills
    skills = []
        # Check if the skills_div is found
    if skills_div:
        # Find all the skill tags within the skills_div
        skill_tags = skills_div.find_all('div', class_='TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk')
        # Extract the text from each skill tag and append it to the skills list
        skills = [skill.text.strip() for skill in skill_tags]
    # Combine the extracted skills into a comma-separated string
    skills_text = ', '.join(skills)
    # Add the skills information to the job_details dictionary
    job_details['Skill Required'] = skills_text
    job_details['Link'] = job_url
    
    job_data.append(job_details)

    # Append the extracted job details to a CSV file
with open('ScrapedData.csv', 'a', newline='') as csv_file:
    fieldnames = ['Name', 'Company', 'Location', 'Salary', 'Experience', 'Type', 'Field', 'Posted', 'Updated', 'Skill Required', 'Link']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Write the header if the file is empty
    if csv_file.tell() == 0:
        csv_writer.writeheader()
    
    for job in job_data:
        csv_writer.writerow(job)



