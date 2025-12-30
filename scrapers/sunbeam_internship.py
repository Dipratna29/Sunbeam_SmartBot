from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class SunbeamInternshipScraper:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape(self) -> dict:
        url = "https://www.sunbeaminfo.in/internship"
        self.driver.get(url)

        page_heading = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h3.inner_page_head")
            )
        ).text

        intro_paragraphs = [
            p.text.strip()
            for p in self.driver.find_elements(By.CSS_SELECTOR, "div.main_info p")
            if p.text.strip()
        ]

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(2)

        accordion_sections = []
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

            paragraphs = [
                p.text.strip()
                for p in panel_body.find_elements(By.TAG_NAME, "p")
                if p.text.strip()
            ]

            bullets = [
                li.text.strip()
                for li in panel_body.find_elements(By.TAG_NAME, "li")
                if li.text.strip()
            ]

            accordion_sections.append({
                "title": title,
                "paragraphs": paragraphs,
                "bullets": bullets
            })

        # ---------------- Internship Batch Schedule Table ----------------
        tables = []

        schedule_heading = self.driver.find_element(
            By.XPATH, "//h4[contains(text(),'Internship Batches Schedule')]"
        ).text

        schedule_table = self.driver.find_element(
            By.CSS_SELECTOR, "div.table-responsive table"
        )

        headers = [th.text.strip() for th in schedule_table.find_elements(By.TAG_NAME, "th")]

        rows = []
        for tr in schedule_table.find_elements(By.TAG_NAME, "tr")[1:]:
            cells = tr.find_elements(By.TAG_NAME, "td")
            if len(cells) == len(headers):
                rows.append({
                    headers[i]: cells[i].text.strip()
                    for i in range(len(headers))
                })

        tables.append({
            "title": schedule_heading,
            "headers": headers,
            "rows": rows
        })

        return {
            "page_heading": page_heading,
            "intro_paragraphs": intro_paragraphs,
            "accordion_sections": accordion_sections,
            "tables": tables
        }

    # ✅ ADD THIS METHOD
    def scrape_to_txt(self, output_path="text_data/sunbeam_internship.txt"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data = self.scrape()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"PAGE: {data['page_heading']}\n\n")

            for para in data["intro_paragraphs"]:
                f.write(para + "\n\n")

            for section in data["accordion_sections"]:
                f.write(f"\nSECTION: {section['title']}\n")
                for p in section["paragraphs"]:
                    f.write(p + "\n")
                for b in section["bullets"]:
                    f.write(f"- {b}\n")

            for table in data["tables"]:
                f.write(f"\nTABLE: {table['title']}\n")
                for row in table["rows"]:
                    row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
                    f.write(row_text + "\n")

        print(f"✅ Internship data saved to {output_path}")
