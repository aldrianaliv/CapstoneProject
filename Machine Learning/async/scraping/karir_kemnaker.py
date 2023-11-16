from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv

def scrape_page(driver, url, job_data, page_number):
    driver.get(url)

    job_cards = driver.find_elements(By.XPATH, '//div[@class="col-md-6 col-lg-4"]')
    if not job_cards:
        print(f"No job listings found on page {page_number}. Exiting.")
        return

    for card in job_cards:
        job_link = card.find_element(By.XPATH, './/a[2]').get_attribute("href")
        company_name = card.find_element(By.XPATH, './/a[1]').text.strip()
        job_title = card.find_element(By.XPATH, './/a[2]/h3').text.strip()
        job_location = card.find_element(By.XPATH, './/div[@class="company-location"]/a').text.strip()
        salary = card.find_element(By.XPATH, './/div[@class="card-content"]/label').text.strip()

        # Navigate to the job link
        driver.get(job_link)
        job_details = {}

        job_details['Job_title'] = job_title
        job_details['Company'] = company_name
        job_details['Location'] = job_location
        job_details['Salary'] = salary

        skill_elements = driver.find_elements(By.XPATH, '//div[@class="vacancy-vocational-badge"]')
        skills = [skill.text.strip() for skill in skill_elements]

        detail_elements = driver.find_elements(By.XPATH, '//div[@class="vacancy-detail-data-wrapper"]')

        job_details['Skills'] = skills
        job_details['Study Requirement'] = detail_elements[6].find_element(By.XPATH, './/p').text.strip()
        job_details['Category'] = detail_elements[0].find_element(By.XPATH, './/p').text.strip()
        job_details['Link'] = job_link

        job_data.append(job_details)

def main():
    base_url = "https://karirhub.kemnaker.go.id/vacancies/industrial"
    page_number = 1
    job_data = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    while page_number < 5:
        url = f"{base_url}?page={page_number}"
        scrape_page(driver, url, job_data, page_number)
        page_number += 1

    driver.quit()

    if job_data:
        with open('selenium-test.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in job_data:
                writer.writerow(job)
        print("Data has been scraped and saved to selenium-test.csv")
    else:
        print("No job data found to save.")

if __name__ == '__main__':
    main()
