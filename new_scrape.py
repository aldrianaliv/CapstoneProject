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

while page_number < 2 :
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
        job_location = card.find('div', class_="CompactOpportunityCardsc__OpportunityInfo-sc-dkg8my-16 krJQkc").text.strip()

        job_response = requests.get(job_link, headers=headers)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')

        job_details = {}
        company_element = job_soup.find('div', class_="TopFoldsc__JobOverViewCompanyInfo-sc-1fbktg5-4 cTKYTc")
        if company_element:
            company_name = company_element.find('a').text.strip()
            job_details['Company'] = company_name
        else:
            job_details['Company'] = ''
        
        job_title_element = job_soup.find('div', class_="TopFoldsc__JobOverviewHeader-sc-1fbktg5-24 cuvDWG")
        if job_title_element:
            job_title = job_title_element.find('h1', class_="TopFoldsc__JobOverViewTitle-sc-1fbktg5-3 fwLnaN").text.strip()
            job_details['Job_title'] = job_title
        else:
            job_details['Job_title'] = ''
        
        salary_element = job_soup.find('div', class_="TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 TopFoldsc__SalaryJobOverview-sc-1fbktg5-29 iqoKuL cmcyYP")
        if salary_element:
            salary_info = salary_element.find('span', class_="TopFoldsc__BasicSalary-sc-1fbktg5-15 bsAnW").text.strip()
            job_details['Salary'] = salary_info
        else:
            job_details['Salary'] = ''

        info_divs = job_soup.find_all('div', class_="TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL")
        if len(info_divs) >= 4:
            job_details['Department'] = info_divs[0].text.strip()
            job_details['Type'] = info_divs[1].text.strip()
            job_details['Study_Req'] = info_divs[2].text.strip()
            job_details['Experience'] = info_divs[3].text.strip()
        else:
            job_details['Department'] = ""
            job_details['Type'] = ""
            job_details['Study_Req'] = ""
            job_details['Experience'] = ""

        skills_div = job_soup.find('div', class_="Opportunitysc__SkillsContainer-sc-gb4ubh-9 klZVgS")
        if skills_div:
            job_details['Skill'] = ', '.join([skill.text.strip() for skill in skills_div.find_all('div')])
        else:
            job_details['Skill'] = ''

        job_desc_div = job_soup.find('div', class_="JobDescriptionsc__DescriptionContainer-sc-22zrgx-2 jCwTA-d")
        if job_desc_div:
            job_details['Job_Desc'] = ', '.join([li.text.strip() for li in job_desc_div.find_all('li')])
        else:
            job_details['Job_Desc'] = ''

        job_data.append(job_details)

    page_number += 1

if job_data:
    with open('job.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = job_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for job in job_data:
            writer.writerow(job)
    print("Data has been scraped and saved to job_listings.csv")
else:
    print("No job data found to save.")
