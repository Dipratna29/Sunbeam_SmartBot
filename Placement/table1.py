from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

def scrape_placement_info(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 30)
    placements = []

    try:
        # Wait until at least one row is present
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tr")))

        rows = driver.find_elements(By.XPATH, "//table//tr")

        if len(rows) <= 1:
            print("Table found but no data rows.")
            return []

        for row in rows[1:]:  # skip header
            cols = row.find_elements(By.TAG_NAME, "td")

            if len(cols) >= 5:
                placements.append({
                    "Batch": cols[0].text,
                    "Karad DAC (%)": cols[1].text,
                    "DAC (%)": cols[2].text,
                    "Wimc/DMC (%)": cols[3].text,
                    "Divesd/DESD (%)": cols[4].text,
                    "DBDA (%)": cols[5].text
                })

    except Exception as e:
        print("Error:", e)

    driver.quit()
    return placements


if __name__ == "__main__":
    url = "https://www.sunbeaminfo.in/placements"
    data = scrape_placement_info(url)

    if not data:
        print("No data found!")
    else:
        for d in data:
            print(d)
