import logging
from dataclasses import dataclass, field

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from funday_bundle.data_structures import CachedCollection
from funday_bundle.steam_scraping import SteamScraper


@dataclass(slots=True)
class FundayBundle:
    driver: webdriver.Chrome = field(init=False)
    cache_collection: CachedCollection = field(default_factory=CachedCollection)

    def __post_init__(self):
        # Driver Init
        options = Options()
        options.add_argument("--headless") 
        self.driver = webdriver.Chrome(options=options)
        
        # Cache Init
        self.cache_collection.import_from_csv()
        
    def end_program(self):
        # Close driver
        if self.driver:
            self.driver.quit()
        
        try:
            # Export Cached games/bundels to csv
            self.cache_collection.export_to_csv()
        except Exception as e:
            logging.error("Data could not be saved")
            logging.exception(f"Details: {e}")
            print("To CSV failed. Check log file for details.")

    # run as app() instead of app.run()
    def __call__(self) -> None:
        scraper: SteamScraper = SteamScraper(self.driver, self.cache_collection)
        
        urls_to_scrape = [
            "https://store.steampowered.com/bundlelist/1721110/Abyssus",
            "https://store.steampowered.com/bundlelist/1625450/Muck"
        ]

        #for url in urls_to_scrape:
        #    scraper.scrape_bundle_page(url)
        #    time.sleep(random.uniform(2, 5))
        
        urls_game_scrape = [
            "https://store.steampowered.com/app/2835570/Buckshot_Roulette/",
            "https://store.steampowered.com/app/3419520/Quarantine_Zone_The_Last_Check/",
            "https://store.steampowered.com/app/2835570/Buckshot_Roulette/",
            "https://store.steampowered.com/app/3419520/Quarantine_Zone_The_Last_Check/"
        ]
        
        scraper.scrape_game_pages(urls_game_scrape)

    