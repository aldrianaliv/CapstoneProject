import csv
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

async def scrape_kalibrr_jobs():
    # Set the path to your chromedriver executable
    chromedriver_path = 'drivers\chromedriver.exe'

    # Create a Chrome service with headless option
    service = ChromeService(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser window)

    # Initialize the Chrome WebDriver with the service and options
    driver = webdriver.Chrome(service=service, options=options)

    # URL of the webpage containing job listings
    base_url = "https://www.kalibrr.com/id-ID/home/all-jobs"
    job_data = []

    # Define the number of pages to scrape (you can adjust this)
    num_pages_to_scrape = 5

    async def fetch_data(url):
        driver.get(url)
        await asyncio.sleep(5)  # Wait for the page to load completely (you can adjust the sleep duration)

    async def scrape_page(page_number):
        url = f"{base_url}?page={page_number}"
        await fetch_data(url)

        job_cards = driver.find_elements(By.CLASS_NAME, "k-font-dm-sans.k-rounded-lg.k-bg-white.k-border-solid.k-border")

        if not job_cards:
            print(f"No job listings found on page {page_number}. Exiting.")
            return

        for card in job_cards:
            job_details = {}

            job_link_element = card.find_element(By.CLASS_NAME, "k-text-black")
            job_link = job_link_element.get_attribute("href")

            company_name_element = card.find_element(By.CLASS_NAME, "k-text-subdued.k-font-bold")
            company_name = company_name_element.text.strip()

            job_title_element = card.find_element(By.CLASS_NAME, "k-text-2xl")
            job_title = job_title_element.text.strip()

            location_element = card.find_element(By.XPATH, "//span[contains(text(), 'South Jakarta, Indonesia')]")
            location = location_element.text.strip() if location_element else "Location Not Specified"

            salary_element = card.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div/div[1]/div[2]/div[1]/span[2]/p')
            salary = salary_element.text.strip() if salary_element else "Salary Undisclosed"

            work_type_element = card.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div/div[1]/div[2]/div[1]/span[3]/span[1]')
            work_type = work_type_element.text.strip() if work_type_element else "Job Type Not Specified"

            
            job_details['Job_title'] = job_title
            job_details['Company'] = company_name
            job_details['Location'] = location
            job_details['Salary'] = salary
            job_details['Work Type'] = work_type
            job_details['Link'] = job_link

            # Extract other details as needed
            # ...

            job_data.append(job_details)

    # Use asyncio to scrape multiple pages concurrently
    tasks = [scrape_page(page_number) for page_number in range(1, num_pages_to_scrape + 1)]
    await asyncio.gather(*tasks)

    # Close the browser
    driver.quit()

    # Save job data to a CSV file
    csv_file_name = "kalibrr-data.csv"
    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = job_data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for job_details in job_data:
            writer.writerow(job_details)

    print(f"Job details saved to '{csv_file_name}'")

if __name__ == '__main__':
    asyncio.run(scrape_kalibrr_jobs())
