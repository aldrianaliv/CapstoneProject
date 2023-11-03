import requests
from bs4 import BeautifulSoup
import csv

# Initialize base URL and page number
base_url = "https://glints.com/id/lowongan-kerja"
page_number = 1

job_data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Referer": "https://glints.com/",
}

while page_number < 5:
    # Create the URL with the current page number
    url = f"{base_url}?page={page_number}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all job card containers
    job_cards = soup.find_all('div', class_="JobCardsc__JobcardContainer-sc-hmqj50-0 iirqVR CompactOpportunityCardsc__CompactJobCardWrapper-sc-dkg8my-2 bMyejJ compact_job_card")
    if not job_cards:
        print(f"No job listings found on page {page_number}. Exiting.")
        break  # No more pages to scrape

    for card in job_cards:
        job_link = "https://glints.com" + card.find('a').get("href")
        company_name = card.find('a', class_='CompactOpportunityCardsc__CompanyLink-sc-dkg8my-10 iTRLWx').text.strip()
        job_title = card.find('h3', class_='CompactOpportunityCardsc__JobTitle-sc-dkg8my-9 hgMGcy').text.strip()
        job_location = card.find('div', class_="CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc").text.strip()
        salary_info_element = card.find('span', class_='CompactOpportunityCardsc__SalaryWrapper-sc-dkg8my-29 gfPeyg')
        salary_info = salary_info_element.text.strip() if salary_info_element else "Perusahaan tidak menampilkan gaji"

        job_response = requests.get(job_link, headers=headers)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')
        job_details = {}
        
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

        # Find the parent div element containing the skills
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
        else:
            skills_text = ""
        # Add the skills information to the job_details dictionary
        job_details['Skill'] = skills_text


        job_desc_div = job_soup.find('ul', class_="public-DraftStyleDefault-ul")
        if job_desc_div:
            job_details['Job_Desc'] = ', '.join([li.text.strip() for li in job_desc_div.find_all('li')])
        else:
            job_details['Job_Desc'] = ''

        job_details['Links'] = job_link

        job_data.append(job_details)

    page_number += 1

if job_data:
    with open('newjobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = job_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for job in job_data:
            writer.writerow(job)
    print("Data has been scraped and saved to job.csv")
else:
    print("No job data found to save.")
