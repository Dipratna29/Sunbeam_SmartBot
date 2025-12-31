import time
import re
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SunbeamCoursesScraper:
    """
    Scrapes Sunbeam Modular Courses and stores data in TXT format
    """

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    # ------------------ UTILITIES ------------------
    def _clean_text(self, text):
        text = re.sub(r'CLICK TO REGISTER', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _is_basic_info_line(self, text):
        keys = [
            "batch schedule",
            "schedule :",
            "duration :",
            "timings :",
            "fees :",
            "course name :"
        ]
        t = text.lower()
        return any(k in t for k in keys)

    # ------------------ SCRAPE CORE ------------------
    def scrape(self):
        self.driver.get("https://sunbeaminfo.in/modular-courses-home")

        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "c_cat_box"))
        )

        courses = []
        for card in self.driver.find_elements(By.CLASS_NAME, "c_cat_box"):
            title = card.find_element(By.CSS_SELECTOR, ".c_info h4").text.strip()
            link = card.find_element(By.CSS_SELECTOR, "a.c_cat_more_btn").get_attribute("href")
            courses.append((title, link))

        all_courses = []

        SECTION_MAP = {
            "target audience": "Target Audience",
            "course introduction": "Target Audience",
            "syllabus": "Syllabus",
            "prerequisites": "Prerequisites",
            "pre-requisites": "Prerequisites",
            "software setup": "Tools & Setup",
            "tools & setup": "Tools & Setup",
            "outcome": "Outcome",
            "outcomes": "Outcome",
            "important notes": "Important Notes",
            "recorded videos": "Video Availability",
            "video availability till date": "Video Availability",
            "batch schedule": "Batch Schedule"
        }

        SECTION_ORDER = [
            "Target Audience",
            "Syllabus",
            "Prerequisites",
            "Tools & Setup",
            "Outcome",
            "Important Notes",
            "Video Availability",
            "Batch Schedule"
        ]

        for course_title, course_url in courses:
            self.driver.get(course_url)
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "course_info"))
            )

            basic_info = {}
            sections = {}
            seen_text = set()

            info_box = self.driver.find_element(By.CLASS_NAME, "course_info")

            # -------- Basic Info --------
            for p in info_box.find_elements(By.TAG_NAME, "p"):
                txt = p.text.strip()
                if ":" in txt:
                    k, v = txt.split(":", 1)
                    basic_info[k.strip()] = v.strip()

            # -------- Accordion Panels --------
            panels = self.driver.find_elements(By.CSS_SELECTOR, ".panel.panel-default")
            for panel in panels:
                try:
                    head = panel.find_element(By.CSS_SELECTOR, ".panel-title a")
                    raw_title = head.text.strip().lower().replace(":", "")

                    self.driver.execute_script("arguments[0].click();", head)

                    body = panel.find_element(By.CLASS_NAME, "panel-body")
                    content = self._clean_text(body.text)

                    if content and content not in seen_text:
                        seen_text.add(content)
                        mapped = SECTION_MAP.get(raw_title, raw_title.title())
                        sections.setdefault(mapped, []).append(content)

                    time.sleep(0.2)
                except:
                    continue

            # -------- Extra Content --------
            for el in info_box.find_elements(By.XPATH, ".//h4 | .//p | .//li"):
                txt = self._clean_text(el.text)
                if not txt:
                    continue
                if self._is_basic_info_line(txt):
                    continue
                if txt in seen_text:
                    continue

                seen_text.add(txt)
                sections.setdefault("Additional Information", []).append(txt)

            all_courses.append({
                "course_title": course_title,
                "basic_info": basic_info,
                "sections": sections,
                "section_order": SECTION_ORDER
            })

        return all_courses

    # ------------------ SAVE TO TXT ------------------
    def scrape_to_txt(self, output_path="text_data/sunbeam_courses.txt"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        courses = self.scrape()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("SUNBEAM MODULAR COURSES\n")
            f.write("=" * 100 + "\n\n")

            for course in courses:
                f.write(course["course_title"].upper() + "\n\n")

                for k, v in course["basic_info"].items():
                    f.write(f"{k}: {v}\n")
                f.write("\n")

                idx = 1
                for sec in course["section_order"] + ["Additional Information"]:
                    if sec in course["sections"]:
                        f.write(f"{idx}. {sec}\n")
                        for txt in course["sections"][sec]:
                            f.write(txt + "\n\n")
                        idx += 1

                f.write("-" * 100 + "\n\n")

        print(f"Courses data saved to {output_path}")
