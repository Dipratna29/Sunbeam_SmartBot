from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class SunbeamMLOpsCourseScraper:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape_to_txt(self, output_path="text_data/sunbeam_courses.txt"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        url = (
            "https://www.sunbeaminfo.in/modular-courses/"
            "mlops-llmops-training-institute-pune"
        )
        self.driver.get(url)

        lines = []

        # ================= COURSE HEADER =================
        lines.append("\n" + "=" * 90 + "\n")
        lines.append("COURSE: MLOps & LLMOps\n")
        lines.append("=" * 90 + "\n\n")

        # ================= COURSE INFO =================
        course_info = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
        )
        lines.append(course_info.text + "\n\n")

        # ================= SYLLABUS =================
        syllabus_id = "collapse318"
        self.driver.execute_script(f"""
            var el = document.getElementById('{syllabus_id}');
            if (el) {{
                el.classList.add('in');
                el.style.height = 'auto';
                el.style.display = 'block';
            }}
        """)
        time.sleep(1)

        syllabus_div = self.wait.until(
            EC.presence_of_element_located((By.ID, syllabus_id))
        )

        lines.append("SYLLABUS\n")
        panel_body = syllabus_div.find_element(By.CLASS_NAME, "panel-body")
        li_items = panel_body.find_elements(By.TAG_NAME, "li")

        if li_items:
            for li in li_items:
                if li.text.strip():
                    lines.append(f"- {li.text.strip()}\n")
        else:
            text = panel_body.text.strip()
            if text:
                lines.append(text + "\n")
        lines.append("\n")

        # ================= PRE-REQUISITES =================
        prereq_id = "collapse317"
        self.driver.execute_script(f"""
            var el = document.getElementById('{prereq_id}');
            if (el) {{
                el.classList.add('in');
                el.style.height = 'auto';
                el.style.display = 'block';
            }}
        """)
        time.sleep(1)

        prereq_div = self.wait.until(
            EC.presence_of_element_located((By.ID, prereq_id))
        )

        lines.append("PRE-REQUISITES\n")
        prereq_text = prereq_div.find_element(
            By.CLASS_NAME, "panel-body"
        ).text.strip()

        if prereq_text:
            lines.append(prereq_text + "\n\n")
        else:
            lines.append("No pre-requisites mentioned\n\n")

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

        print("✅ MLOps & LLMOps course saved to text_data/sunbeam_courses.txt")
