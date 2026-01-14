import logging, time, random

from dataclasses import dataclass, field

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import funday_bundle.steam_scraping as steam

@dataclass(slots=True)
class FundayBundle:
    driver: webdriver.Chrome = field(init=False)

    def __post_init__(self):
        options = Options()
        options.add_argument("--headless") 
        self.driver = webdriver.Chrome(options=options)

    # run as app() instead of app.run()
    def __call__(self) -> None:
        urls_to_scrape = [
            "https://store.steampowered.com/bundlelist/1721110/Abyssus",
            "https://store.steampowered.com/bundlelist/1625450/Muck"
        ]

        for url in urls_to_scrape:
            steam.scrape_site(self.driver, url)
            time.sleep(random.uniform(2, 5))

    
    def close_driver(self):
        if self.driver:
            self.driver.quit()