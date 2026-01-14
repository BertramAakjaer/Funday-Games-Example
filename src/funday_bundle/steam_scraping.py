from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://store.steampowered.com/bundlelist/1721110/Abyssus"

options = Options()
options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

# Giver bedre navne senere
BUNDLE_SECTION_SELECTOR = "[class*='T_3MrEHN9bFK4I4FQqDC8']"
BUNDLE_ELEMENTS_SELECTOR = "[class*='_1NM531LjOd5QmDktUetCOm']"
FOCUSABLE_SELECTOR = "[class*='Focusable']"

try:
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, BUNDLE_SECTION_SELECTOR)))

    first_section = driver.find_element(By.CSS_SELECTOR, BUNDLE_SECTION_SELECTOR)
    bundle_containers = first_section.find_elements(By.CSS_SELECTOR, BUNDLE_ELEMENTS_SELECTOR)

    for i, bundle in enumerate(bundle_containers, 1):
        print(f"SCRAPING BUNDLE NR. {i}")
        
        all_games_in_bundle = bundle.find_elements(By.CSS_SELECTOR, FOCUSABLE_SELECTOR)
        
        for game in all_games_in_bundle:
            link = game.get_attribute('href')
            if link:
                print(link)

finally:
    driver.quit()