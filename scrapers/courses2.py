from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class SunbeamPythonCourseScraper:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape_to_txt(self, output_path="text_data/sunbeam_courses.txt"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        url = "https://www.sunbeaminfo.in/modular-courses/python-classes-in-pune"
        self.driver.get(url)

        lines = []

        # ================= COURSE HEADER
        lines.append("\n" + "=" * 90 + "\n")
        lines.append("COURSE: PYTHON DEVELOPMENT\n")
        lines.append("=" * 90 + "\n\n")

        # ================= COURSE INFO =================
        course_info = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
        )
        lines.append(course_info.text + "\n\n")

        # ================= SYLLABUS =================
        syllabus_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='#collapse58']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", syllabus_btn)
        syllabus_btn.click()

        syllabus_div = self.wait.until(
            EC.presence_of_element_located((By.ID, "collapse58"))
        )

        lines.append("SYLLABUS\n")
        for li in syllabus_div.find_elements(By.CSS_SELECTOR, ".list_style ul li"):
            if li.text.strip():
                lines.append(f"- {li.text.strip()}\n")
        lines.append("\n")

        # ================= PRE-REQUISITES =================
        pre_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='#collapse56']"))
        )

        if pre_btn.get_attribute("aria-expanded") == "false":
            self.driver.execute_script("arguments[0].scrollIntoView(true);", pre_btn)
            pre_btn.click()

        prereq_div = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".panel-collapse.collapse.in")
            )
        )

        lines.append("PRE-REQUISITES\n")
        li = prereq_div.find_element(By.TAG_NAME, "li")
        lines.append(f"- {li.text.strip()}\n\n")

        # ================= BATCH SCHEDULE =================
        collapse_id = "collapseFive"
        self.driver.execute_script(
            f"document.getElementById('{collapse_id}').classList.add('in')"
        )
        time.sleep(1)

        rows = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, f"//div[@id='{collapse_id}']//table//tbody//tr")
            )
        )

        lines.append("BATCH SCHEDULE\n")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                lines.append(
                    f"Batch Code: {cols[1].text} | "
                    f"Start: {cols[2].text} | "
                    f"End: {cols[3].text} | "
                    f"Time: {cols[4].text}\n"
                )
        lines.append("\n")

        # ================= WRITE TO FILE =================
        with open(output_path, "a", encoding="utf-8") as f:
            f.writelines(lines)

        print("✅ Python Development course saved to text_data/sunbeam_courses.txt")
