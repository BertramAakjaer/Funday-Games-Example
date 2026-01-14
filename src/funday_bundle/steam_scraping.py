import logging

import funday_bundle.constants as const

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_site(driver, url: str):
    logging.info(f"Starting scrape for: {url}")
    driver.get(url)
    
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, const.BUNDLE_SECTION_SELECTOR)))

        first_section = driver.find_element(By.CSS_SELECTOR, const.BUNDLE_SECTION_SELECTOR)
        bundle_containers = first_section.find_elements(By.CSS_SELECTOR, const.BUNDLE_ELEMENTS_SELECTOR)

        for i, bundle in enumerate(bundle_containers, 1):
            logging.info(f"Found bundle nr. {i}")

            print(f"SCRAPING BUNDLE NR. {i}")
    
            all_games_in_bundle = bundle.find_elements(By.CSS_SELECTOR, const.FOCUSABLE_SELECTOR)
            
            for game in all_games_in_bundle:
                link = game.get_attribute('href')
                if link:
                    print(link)
            
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")