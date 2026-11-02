import os
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

    def __init__(self, output_dir="text_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # On Linux servers Chromium is often installed as "chromium";
        # CHROME_BINARY / CHROMEDRIVER_PATH override auto-detection.
        # On Windows/macOS, Selenium Manager finds Chrome automatically.
        binary = os.getenv("CHROME_BINARY") or shutil.which("chromium") \
            or shutil.which("chromium-browser")
        if binary:
            chrome_options.binary_location = binary

        driver_path = os.getenv("CHROMEDRIVER_PATH") or shutil.which("chromedriver")
        service = Service(driver_path) if driver_path else Service()

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _path(self, name):
        return os.path.join(self.output_dir, name)

    
    # SCRAPE EVERYTHING → TXT FILES
    def scrape_all_to_txt(self):
        print("🚀 Starting Sunbeam scraping...\n")

        # ABOUT 
        SunbeamAboutScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_about.txt"))

        #INTERNSHIP 
        SunbeamInternshipScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_internship.txt"))

        #COURSES (each course scraper APPENDS, so start from an empty file)
        open(self._path("sunbeam_courses.txt"), "w", encoding="utf-8").close()

        SunbeamCoreJavaCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamPythonCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamDevOpsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamMERNCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamMachineLearningCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamDSAJavaCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamGenerativeAICourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamAptitudeCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamMCQsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamSparkCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamMLOpsCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        SunbeamDreamLLMCourseScraper(
            self.driver, self.wait
        ).scrape_to_txt(self._path("sunbeam_courses.txt"))

        print("\n✅ ALL SUNBEAM DATA SCRAPED SUCCESSFULLY")
        print(f"📁 Files written to: {self.output_dir}")

    
    # CLEANUP
    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass
        print("🧹 Selenium driver closed")
