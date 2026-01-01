def run_modular_courses_scraper():
    import time
    import re
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager


    def clean_text(text):
        text = re.sub(r'CLICK TO REGISTER', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 30)

    driver.get("https://sunbeaminfo.in/modular-courses-home")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "c_cat_box")))

    courses = []
    for card in driver.find_elements(By.CLASS_NAME, "c_cat_box"):
        title = card.find_element(By.CSS_SELECTOR, ".c_info h4").text.strip()
        link = card.find_element(By.CSS_SELECTOR, "a.c_cat_more_btn").get_attribute("href")
        courses.append((title, link))


    def is_basic_info_line(text):
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
        "recorded videos": "Video Availability Till Date",
        "video availability till date": "Video Availability Till Date",
        "batch schedule": "Batch Schedule"
    }

    SECTION_ORDER = [
        "Target Audience",
        "Syllabus",
        "Prerequisites",
        "Tools & Setup",
        "Outcome",
        "Important Notes",
        "Video Availability Till Date",
        "Batch Schedule"
    ]


    for course_title, course_url in courses:
        driver.get(course_url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "course_info")))

        basic_info = {}
        sections = {}
        seen_text = set()

        info_box = driver.find_element(By.CLASS_NAME, "course_info")

        try:
            h3 = info_box.find_element(By.TAG_NAME, "h3").text
            if ":" in h3:
                k, v = h3.split(":", 1)
                basic_info[k.strip()] = v.strip()
        except:
            pass

        for p in info_box.find_elements(By.TAG_NAME, "p"):
            txt = p.text.strip()
            if ":" in txt:
                k, v = txt.split(":", 1)
                basic_info[k.strip()] = v.strip()

        panels = driver.find_elements(By.CSS_SELECTOR, ".panel.panel-default")
        for panel in panels:
            try:
                head = panel.find_element(By.CSS_SELECTOR, ".panel-title a")
                raw = head.text.strip().lower().replace(":", "")
                driver.execute_script("arguments[0].click();", head)

                body = WebDriverWait(panel, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "panel-body"))
                )

                content = clean_text(body.text)
                if content and content not in seen_text:
                    seen_text.add(content)
                    mapped = SECTION_MAP.get(raw, raw.title())
                    sections.setdefault(mapped, []).append(content)

                time.sleep(0.2)
            except:
                pass

        for el in info_box.find_elements(By.XPATH, ".//h4 | .//p | .//li"):
            txt = clean_text(el.text)
            if not txt:
                continue
            if is_basic_info_line(txt):
                continue
            if txt in seen_text:
                continue

            seen_text.add(txt)
            sections.setdefault("Additional Information", []).append(txt)


        print("\n" + "=" * 100)
        print(course_title)
        print()

        BASIC_ORDER = ["Course Name", "Batch Schedule", "Schedule", "Duration", "Timings", "Fees"]
        for key in BASIC_ORDER:
            if key in basic_info:
                print(f"{key} : {basic_info[key]}\n")

        idx = 1
        for sec in SECTION_ORDER + ["Additional Information"]:
            if sec in sections:
                print(f"{idx}. {sec}")
                print("\n".join(sections[sec]))
                print()
                idx += 1


    driver.quit()
