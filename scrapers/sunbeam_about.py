from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class SunbeamAboutScraper:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape_to_txt(self, output_path="text_data/sunbeam_about.txt"):
        os.makedirs("text_data", exist_ok=True)

        url = "https://www.sunbeaminfo.in/about-us"
        self.driver.get(url)

        lines = []
        lines.append("PAGE: ABOUT SUNBEAM\n\n")

        # Page heading
        heading = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h3.inner_page_head")
            )
        ).text
        lines.append(f"{heading}\n\n")

        # Main paragraphs
        for p in self.driver.find_elements(By.CSS_SELECTOR, "div.main_info p"):
            text = p.text.strip()
            if text:
                lines.append(text + "\n\n")

        # Scroll for accordion
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Accordion sections
        for link in self.driver.find_elements(By.CSS_SELECTOR, "a[data-toggle='collapse']"):
            title = link.text.strip()
            panel_id = link.get_attribute("href").split("#")[-1]

            self.driver.execute_script("arguments[0].click();", link)
            time.sleep(1)

            panel_body = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"#{panel_id} .panel-body")
                )
            )

            lines.append(f"\nSECTION: {title}\n")

            for p in panel_body.find_elements(By.TAG_NAME, "p"):
                txt = p.text.strip()
                if txt:
                    lines.append(txt + "\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ About data saved to {output_path}")
