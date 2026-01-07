from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

#ABOUT & INTERNSHIP
from scrapers.sunbeam_about import SunbeamAboutScraper
from scrapers.sunbeam_internship import SunbeamInternshipScraper

#COURSES (1–12)
from scrapers.courses1 import SunbeamCoreJavaCourseScraper
from scrapers.courses2 import SunbeamPythonCourseScraper
from scrapers.courses3 import SunbeamDevOpsCourseScraper
from scrapers.courses4 import SunbeamMERNCourseScraper
from scrapers.courses5 import SunbeamMachineLearningCourseScraper
from scrapers.courses6 import SunbeamDSAJavaCourseScraper
from scrapers.courses7 import SunbeamGenerativeAICourseScraper
from scrapers.courses8 import SunbeamAptitudeCourseScraper
from scrapers.courses9 import SunbeamMCQsCourseScraper
from scrapers.courses10 import SunbeamSparkCourseScraper
from scrapers.courses11 import SunbeamMLOpsCourseScraper
from scrapers.courses12 import SunbeamDreamLLMCourseScraper


class ScraperManager:
    """
    Central manager that controls Selenium driver
    and runs all Sunbeam scrapers.
    """

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    
    # SCRAPE EVERYTHING → TXT FILES
    def scrape_all_to_txt(self):
        print("🚀 Starting Sunbeam scraping...\n")

        # ABOUT 
        SunbeamAboutScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        #INTERNSHIP 
        SunbeamInternshipScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        #COURSES
        SunbeamCoreJavaCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamPythonCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamDevOpsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamMERNCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamMachineLearningCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamDSAJavaCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamGenerativeAICourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamAptitudeCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamMCQsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamSparkCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamMLOpsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        SunbeamDreamLLMCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt()

        print("\n✅ ALL SUNBEAM DATA SCRAPED SUCCESSFULLY")
        print("📁 Files generated:")
        print("   - text_data/sunbeam_about.txt")
        print("   - text_data/sunbeam_internship.txt")
        print("   - text_data/sunbeam_courses.txt")

    
    # CLEANUP
    def close(self):
        self.driver.quit()
        print("🧹 Selenium driver closed")
