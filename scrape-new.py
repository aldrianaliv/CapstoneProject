import requests
import csv
from bs4 import BeautifulSoup

def scrape_skill_information(job_url, headers, skill_list):
    if job_url != "N/A":
        # Send an HTTP GET request to the job link
        response = requests.get(job_url, headers=headers)

        if response.status_code == 200:
            job_page_source = response.text
            job_soup = BeautifulSoup(job_page_source, 'html.parser')

            # Locate and scrape the skill section from the job page
            # Replace the following line with your own logic to locate the skill section
            skill_section = job_soup.find('label', class_='TagStyle__TagContent-sc-66xi2f-0 iFeugN tag-content')

            if skill_section:
                skill_info = skill_section.text.strip()
                if skill_info not in skill_list:
                    skill_list.append(skill_info)
    return skill_list

def extract_job_description_and_requirements(job_url, headers):
    job_description = "N/A"
    job_requirements = "N/A"

    if job_url != "N/A":
        # Send an HTTP GET request to the job link
        response = requests.get(job_url, headers=headers)

        if response.status_code == 200:
            job_page_source = response.text
            job_soup = BeautifulSoup(job_page_source, 'html.parser')

            # Locate and scrape the job description and requirements
            divs = job_soup.find_all('ul', class_='public-DraftStyleDefault-ul')

            for div in divs:
                text = div.text.strip()
                if "job description" in text.lower():
                    job_description = text
                else:
                    job_requirements = text

    return job_description, job_requirements

all_job_listings = []
skill_list = []  # Initialize an empty list for skill information

base_url = "https://glints.com/id/lowongan-kerja"
page_number = 1
url = f"{base_url}?page={page_number}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://glints.com/",
}

while page_number < 2:
    # Send an HTTP GET request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        page_source = response.text  # Get the page content as text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        job_listings = []

        # Your existing code to extract job listings here
        job_titles = soup.find_all('h3', class_='CompactOpportunityCardsc__JobTitle-sc-dkg8my-9 hgMGcy')
        company = soup.find_all('a', class_='CompactOpportunityCardsc__CompanyLink-sc-dkg8my-10 iTRLWx')
        location = soup.find_all('span', class_='CardJobLocation__StyledTruncatedLocation-sc-1by41tq-1 kEinQH')
        
        # Extract work type and experience values
        study_req_elements = soup.find_all('div', class_='TagStyle-sc-r1wv7a-4 bJWZOt CompactOpportunityCardTags__Tag-sc-610p59-1 hncMah')
        
        study_req_list = []
        experience_list = []
        work_type_list=[]
        skill_list=[]

        for element in study_req_elements:
            text = element.text
            if any(keyword in text.lower() for keyword in ["setahun", "tahun"]):  # Assuming this text is for "experience"
                experience_list.append(text)
            elif "Minimal" in text:  # Assuming this text is for "min study"
                study_req_list.append(text)
            elif any(keyword in text.lower() for keyword in ["harian",'magang','penuh waktu','paruh waktu','kontrak']):
                work_type_list.append(text)
            elif not any(keyword in text.lower() for keyword in ['+']):
                skill_list.append(text)
                
        

        salary = soup.find_all('span', class_='CompactOpportunityCardsc__SalaryWrapper-sc-dkg8my-29 gfPeyg')
        links = soup.find_all('a', class_='CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link')

        for i in range(len(job_titles)):
            job_listing = {
                "Job Title": job_titles[i].text if i < len(job_titles) else "N/A",
                "Company": company[i].text if i < len(company) else "N/A",
                "Location": location[i].text if i < len(location) else "N/A",
                "Work Type": work_type_list[i] if i < len(work_type_list) else "N/A",
                "Study Requirement": study_req_list[i] if i < len(study_req_list) else "N/A",
                "Experience": experience_list[i] if i < len(experience_list) else "N/A",
                "Skill" : skill_list[i] if i < len(skill_list) else "N/A",
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

# Now, let's add code to scrape the skill information, job description, and requirements from each job link
for job_listing in all_job_listings:
    job_url = job_listing["Link"]
    skill_list = scrape_skill_information(job_url, headers, skill_list)
    job_description, job_requirements = extract_job_description_and_requirements(job_url, headers)
    job_listing["Job Description"] = job_description
    job_listing["Job Requirements"] = job_requirements

# Save job listings to a CSV file
with open('job_listings.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Job Title", "Company", "Location", "Work Type", "Study Requirement", "Experience", "Skill", "Salary", "Job Description", "Job Requirements", "Link"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    # Write the data rows
    for i, job_listing in enumerate(all_job_listings):
        job_listing["Skill"] = ", ".join(skill_list)  # Update "Skill" field with all skill information
        writer.writerow(job_listing)

print("Job listings have been saved to job_listings.csv")
