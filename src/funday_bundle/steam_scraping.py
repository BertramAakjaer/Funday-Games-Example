import hashlib, logging, re

from re import Match
from typing import Any
from enum import Enum

import funday_bundle.constants as const
from funday_bundle.data_structures import CachedCollection, GameCache, BundleCache

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC



# Enum
class UrlType(Enum):
    Game_Page = 1
    Bundle_Page = 2
    Game_Bundels_Page = 3


# Helper functions
def _extract_steam_id(url: (str | int)) -> str | None:
    # Finds app_id because the whole link is not needed
    match: (Match[str] | None) = re.search(r'/(app|bundle|bundlelist)/(\d+)', str(url))
    
    if match:
        url_type: (str | None) = match.group(1)
        steam_id: (str | None) = match.group(2)
        return steam_id
    return ""


def _get_url_by_id(steam_id: (str | int), url_type: UrlType) -> str | None:
    cleaned_id = _extract_steam_id(steam_id)
    
    if not cleaned_id:
        cleaned_id = str(steam_id)
    
    match url_type:
        case UrlType.Game_Page:
            url_for_page = f"https://store.steampowered.com/app/{cleaned_id}/"
            
        case UrlType.Bundle_Page:
            url_for_page = f"https://store.steampowered.com/bundle/{cleaned_id}"
            
        case UrlType.Game_Bundels_Page:
            url_for_page = f"https://store.steampowered.com/bundlelist/{cleaned_id}/"
            
        case _:
            url_for_page = ""
    
    return url_for_page

def parse_price(price_str: str) -> float:
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0
    
def parse_ratings(raw_rating: str) -> tuple[int, float] | None:
    match = re.search(r'(\d+)% of the ([\d,]+) user reviews', raw_rating)
    
    if match:
        percent_str = match.group(1)
        count_str = match.group(2)
        
        percentage = float(percent_str) / 100.0
        count = int(count_str.replace(',', '').replace('.', ''))
        
        return count, percentage
    return None


def get_hash_from_url(url: str, hash_lenght=16) -> str:
    hash_object = hashlib.sha256(url.encode('utf-8'))    
    return hash_object.hexdigest()[:hash_lenght]


def print_scraping_error(url: (str | int)) -> None:
    logging.error(f"Error scraping {url}")
    print(f"Failed to scrape {url}")
    return None
    


# Class code
class SteamScraper:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 3)
        
    def _get_div_content(self, selector: str, find_multiple=False, element: (WebElement | None)=None) -> (WebElement | list[WebElement]):
        if element: # Using Element
            if find_multiple:
                return element.find_elements(By.CSS_SELECTOR, selector)
            
            return (element.find_element(By.CSS_SELECTOR, selector))
        
        else: # Using driver
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            if find_multiple:
                return (self.driver.find_elements(By.CSS_SELECTOR, selector))
            
            return (self.driver.find_element(By.CSS_SELECTOR, selector))
    
    def _get_price(self, element: (WebElement | None)=None) -> float | None:
        price_div = self._get_div_content(const.DISCOUNT_ORIGINAL, element=element)
            
        if not isinstance(price_div, list):
            str_price: str = price_div.text.strip().lower()
            str_price = str_price
            
            if not str_price:
                return None
            
            return parse_price(str_price)
    
    def _get_ratings(self) -> tuple[int, float] | None:
        rating_div = self._get_div_content(const.REVIEW_SELECTOR)
        
        if not isinstance(rating_div, list):
            temp_rating = rating_div.text.strip().lower()
            return parse_ratings(temp_rating)
            
            
            
    def scrape_bundle_page(self, url: str) -> None:
        try:
            self.driver.get(url)
            
            first_section = self._get_div_content(const.BUNDLE_SECTION_SELECTOR)
            
            if not isinstance(first_section, list):
                bundle_containers = self._get_div_content(const.BUNDLE_ELEMENTS_SELECTOR, True, first_section)
            
            if isinstance(bundle_containers, list):
                for i, bundle in enumerate(bundle_containers, 1):
                    logging.info(f"Found bundle nr. {i}")

                    print(f"SCRAPING BUNDLE NR. {i}")
            
                    all_games_in_bundle = bundle.find_elements(By.CSS_SELECTOR, const.FOCUSABLE_SELECTOR)
                    
                    for game in all_games_in_bundle:
                        link = game.get_attribute('href')
                        if link:
                            print(link)
        except Exception as e:
            logging.error(f"Error scraping {url}")
            print(f"no bundles on {url}")
            
    
    
    
    def scrape_game_page(self, steam_id: (str | int)) -> None:
        try:
            url = _get_url_by_id(steam_id, UrlType.Game_Page)
            
            if not url:
                return print_scraping_error(steam_id)
            
            
            self.driver.get(url)
            
            # Variables to fill
            
            steam_link_hash: str
            _steam_id: int
            game_title: str
            game_price: float
            _overall_rating: float
            _overall_count: int
            game_tags: list[str]
            game_genres: list[str]
            _release_date: int
            
            
            #** Data scraping section **
            
            # Hash calculation
            steam_link_hash = get_hash_from_url(url)
            print(f"Hash: {steam_link_hash}")
            
            # ID saving
            temp_id = _extract_steam_id(steam_id)
            if not temp_id:
                return print_scraping_error(steam_id)
            
            _steam_id = int(temp_id) 
            print(f"Steam ID: {_steam_id}")
            
            # Game Title Extraction
            title_div = self._get_div_content(const.TITLE_SELECTOR)
            
            if not isinstance(title_div, list):
                temp_title: str = title_div.text
                game_title = temp_title.strip().lower()
                print(f"Game Title: {game_title}")
                
            # Game Price
            temp_price = self._get_price()
            if not temp_price:
                return print_scraping_error(steam_id)
            
            game_price = temp_price
            print(f"Game Price: {game_price}")
            
            # Reviews
            temp_rating = self._get_ratings()
            
            if temp_rating is None:
                return print_scraping_error(steam_id)
            
            _overall_count, _overall_rating = temp_rating
            
            print(f"Review Score: {_overall_rating}")
            print(f"Review Count: {_overall_count}")
            
            
            # Tags            
                
            return
        
            a = GameCache(
                hash=steam_link_hash,
                steam_id=_steam_id,
                title=game_title,
                price=game_price,
                overall_rating=_overall_rating,
                overall_count=_overall_count,
                tags=game_tags,
                genres=game_genres,
                release_date=_release_date
            )
            

        except Exception as e:
            logging.error(f"Error scraping {steam_id}")
            print(f"Failed to scrape {steam_id}: {e}")
            return None