from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from driver import get_headless_driver


def scrape_mcqs_course():
    driver = get_headless_driver()
    driver.get("https://www.sunbeaminfo.in/modular-courses.php?mdid=57")

    wait = WebDriverWait(driver, 20)

    course_info = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
    )
    print("\n\nMastering MCQs Info")
    print("-" * 40)
    print(course_info.text)

    # COURSE CONTENT
    collapse_id = "collapse302"
    driver.execute_script(f"""
    var el = document.getElementById('{collapse_id}');
    el.classList.add('in');
    el.style.height = 'auto';
    el.style.display = 'block';
    """)

    items = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, f"#{collapse_id} .list_style ul li")
        )
    )
    print("\nCourse Content")
    print("-" * 40)
    for item in items:
        if item.text.strip():
            print(item.text.strip())

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
