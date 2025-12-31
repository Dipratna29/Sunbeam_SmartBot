from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from driver import get_headless_driver


def scrape_dream_llm_course():
    driver = get_headless_driver()
    driver.get(
        "https://www.sunbeaminfo.in/modular-courses/dreamllm-training-institute-pune"
    )

    wait = WebDriverWait(driver, 20)

    # Course Info
    course_info = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
    )
    print("\n\nDream LLM Info")
    print("-" * 40)
    print(course_info.text)

    # SYLLABUS
    syllabus_collapse_id = "collapse320"
    driver.execute_script(f"""
    var el = document.getElementById('{syllabus_collapse_id}');
    el.classList.add('in');
    el.style.height = 'auto';
    el.style.display = 'block';
    """)

    syllabus_div = wait.until(
        EC.presence_of_element_located((By.ID, syllabus_collapse_id))
    )
    print("\nSYLLABUS")
    print("-" * 40)

    panel_body = syllabus_div.find_element(By.CLASS_NAME, "panel-body")
    li_items = panel_body.find_elements(By.TAG_NAME, "li")

    if li_items:
        for li in li_items:
            if li.text.strip():
                print(li.text.strip())
    else:
        text = panel_body.text.strip()
        print(text if text else "No syllabus available")

    # PRE-REQUISITES
    pre_collapse_id = "collapse319"
    driver.execute_script(f"""
    var el = document.getElementById('{pre_collapse_id}');
    el.classList.add('in');
    el.style.height = 'auto';
    el.style.display = 'block';
    """)

    pre_div = wait.until(
        EC.presence_of_element_located((By.ID, pre_collapse_id))
    )
    print("\nPRE-REQUISITES")
    print("-" * 40)

    content = pre_div.find_element(By.CLASS_NAME, "panel-body").text.strip()
    print(content if content else "No pre-requisites mentioned")

    # BATCH SCHEDULE
    collapse_id = "collapseFive"
    driver.execute_script(
        f"document.getElementById('{collapse_id}').classList.add('in')"
    )
    time.sleep(1)

    rows = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, f"//div[@id='{collapse_id}']//table//tbody//tr")
    ))

    print("\nBATCH SCHEDULE\n")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 5:
            print(f"Sr No     : {cols[0].text}")
            print(f"Batch Code: {cols[1].text}")
            print(f"Start Date: {cols[2].text}")
            print(f"End Date  : {cols[3].text}")
            print(f"Time      : {cols[4].text}")
            print("-" * 40)

    driver.quit()
