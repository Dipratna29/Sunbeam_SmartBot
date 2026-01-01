from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class SunbeamMCQsCourseScraper:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape_to_txt(self, output_path="text_data/sunbeam_courses.txt"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        url = "https://www.sunbeaminfo.in/modular-courses.php?mdid=57"
        self.driver.get(url)

        lines = []

        # ================= COURSE HEADER =================
        lines.append("\n" + "=" * 90 + "\n")
        lines.append("COURSE: MASTERING MCQs\n")
        lines.append("=" * 90 + "\n\n")

        # ================= COURSE INFO =================
        course_info = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
        )
        lines.append(course_info.text + "\n\n")

        # ================= COURSE CONTENT =================
        content_collapse_id = "collapse302"

        self.driver.execute_script(f"""
            var el = document.getElementById('{content_collapse_id}');
            if (el) {{
                el.classList.add('in');
                el.style.height = 'auto';
                el.style.display = 'block';
            }}
        """)
        time.sleep(1)

        items = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, f"#{content_collapse_id} .list_style ul li")
            )
        )

        lines.append("COURSE CONTENT\n")
        for item in items:
            if item.text.strip():
                lines.append(f"- {item.text.strip()}\n")
        lines.append("\n")

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

        print("✅ Mastering MCQs course saved to text_data/sunbeam_courses.txt")
