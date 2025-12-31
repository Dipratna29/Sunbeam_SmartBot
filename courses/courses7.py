from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from driver import get_headless_driver


def scrape_genai_course():
    driver = get_headless_driver()
    driver.get("https://www.sunbeaminfo.in/modular-courses/mastering-generative-ai")

    wait = WebDriverWait(driver, 20)

    course_info = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.course_info"))
    )
    print("\n\nMastering Generative AI Info")
    print("-" * 40)
    print(course_info.text)

    syllabus_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='#collapse300']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", syllabus_btn)
    syllabus_btn.click()

    syllabus_div = wait.until(
        EC.presence_of_element_located((By.ID, "collapse300"))
    )
    print("\nSYLLABUS")
    print("-" * 40)
    for li in syllabus_div.find_elements(By.CSS_SELECTOR, ".list_style ul li"):
        if li.text.strip():
            print(li.text.strip())

    pre_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='#collapse306']"))
    )
    if pre_btn.get_attribute("aria-expanded") == "false":
        driver.execute_script("arguments[0].scrollIntoView(true);", pre_btn)
        pre_btn.click()

    items = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".panel-collapse.collapse.in"))
    )
    print("\nPRE-REQUISITES")
    print("-" * 40)
    print(items.find_element(By.TAG_NAME, "li").text.strip())

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
