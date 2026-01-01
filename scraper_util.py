from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.sunbeam_about import SunbeamAboutScraper
from scrapers.sunbeam_internship import SunbeamInternshipScraper


class ScraperManager:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def scrape_all_to_txt(self):
        SunbeamAboutScraper(self.driver, self.wait).scrape_to_txt()
        SunbeamInternshipScraper(self.driver, self.wait).scrape_to_txt()

    def close(self):
        self.driver.quit()
