import hashlib, logging, re

from datetime import datetime
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
        #url_type: (str | None) = match.group(1)
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
            return ""
    
    return f"{url_for_page}?l=english"


def _parse_price(price_str: str) -> float:
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0
    
    
def _parse_ratings(raw_rating: str) -> tuple[int, float] | None:
    pattern = r'(\d+)%\s+(?:of the|af de)\s+([\d,.]+)\s+(?:user reviews|brugeranmeldelser)'
    match = re.search(pattern, raw_rating)
    
    if match:
        percent_str = match.group(1)
        count_str = match.group(2)
        
        percentage = float(percent_str) / 100.0
        count = int(count_str.replace(',', '').replace('.', ''))
        
        return count, percentage
    return None

def _get_time_from_str(date_str: str) -> datetime | None:
    try:
        clean_date_string = date_str.split('\n')[-1]
        date_object = datetime.strptime(clean_date_string, "%d %b, %Y")
        
        return date_object
    except Exception as e:
        logging.error(f"Error getting date from {str}: {e}")
        return None


def _get_hash_from_url(url: str, hash_lenght=16) -> str:
    hash_object = hashlib.sha256(url.encode('utf-8'))    
    return hash_object.hexdigest()[:hash_lenght]


def _print_scraping_error(url: (str | int)) -> None:
    logging.error(f"Error scraping {url}")
    print(f"Failed to scrape {url}")
    return None
    


# Class code
class SteamScraper:
    def __init__(self, driver: WebDriver, cache_collection: CachedCollection):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 3)
        self.cache_collection = cache_collection
        
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
        price_div = self._get_div_content(const.PRICE_WRAPPER_SELECTOR, element=element)
        
        if isinstance(price_div, list):
            return None
        
        try:
            try:
                price_span = self._get_div_content(const.NORMAL_GAME_PRICE, element=price_div)
            except:
                price_span = self._get_div_content(const.DISCOUNT_ORIGINAL_PRICE, element=price_div)
        except:
            return None
            
        if not isinstance(price_span, list):
            str_price: str = price_span.text.strip().lower()
            str_price = str_price
            
            if not str_price:
                return None
            
            return _parse_price(str_price)
    
    def _get_ratings(self) -> tuple[int, float] | None:
        rating_upper_div = self._get_div_content(const.REVIEW_1_SELECTOR)
        
        if isinstance(rating_upper_div, list):
            return None
        
        rating_div = self._get_div_content(const.REVIEW_2_SELECTOR, element=rating_upper_div)
        
        if not isinstance(rating_div, list):
            content = rating_div.get_attribute("data-tooltip-html")
            if content:
                temp_rating = content.strip().lower()
                return _parse_ratings(temp_rating)
            
            
            
            
    
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
            
    
    
    
    
    
    def scrape_game_page(self, steam_id: (str | int)) -> GameCache | None:
        logging.info(f"Starting Scraping: {steam_id}")
        url = _get_url_by_id(steam_id, UrlType.Game_Page)
        
        if not url:
            return _print_scraping_error(steam_id)
        
        hash = _get_hash_from_url(url)
        logging.info(f"Calculated Hash: {hash}")
        
        game_obj = self.cache_collection.does_game_exists(hash)
        
        if game_obj:
            logging.info(f"Game is already scraped at {game_obj.last_time_scraped}")
            return game_obj
        
        
        try:
            self.driver.get(url)
            
            # Variables to fill
            
            steam_link_hash: str
            _steam_id: int
            game_title: str
            game_price: float
            _overall_rating: float
            _overall_count: int
            game_tags: list[str]
            _release_date: datetime
            
            
            #** Data scraping section **
            
            # Hash calculation
            steam_link_hash = hash
            logging.info(f"Calculated Hash: {steam_link_hash}")
            
            
            # ID saving
            temp_id = _extract_steam_id(steam_id)
            if not temp_id:
                return _print_scraping_error(steam_id)
            
            _steam_id = int(temp_id)
            logging.info(f"Exctracetd ID: {_steam_id}")
            
                        
            # Game Title Extraction
            title_div = self._get_div_content(const.TITLE_SELECTOR)
            
            if not isinstance(title_div, list):
                temp_title: str = title_div.text
                game_title = temp_title.strip().lower()
            
            logging.info(f"Scraped Game Title: {game_title}")
            
                            
            # Game Price
            temp_price = self._get_price()
            if not temp_price:
                return _print_scraping_error(steam_id)
            
            game_price = temp_price
            logging.info(f"Scraped Game Price: {game_price}")
            
            
            # Reviews
            temp_rating = self._get_ratings()
                        
            if not temp_rating:
                return _print_scraping_error(steam_id)
            
            _overall_count, _overall_rating = temp_rating
            
            logging.info(f"Scraped Review Score: {_overall_rating * 100}%")
            logging.info(f"Scraped Review Count: {_overall_count}")
            
            
            # Tags
            button_tags = self._get_div_content(const.BUTTON_TAGS)
            if not isinstance(button_tags, list):
                button_tags.click()
            
            tags_div = self._get_div_content(const.TAGS_SELECTOR)
            if not isinstance(tags_div, list):
                tags_str = tags_div.text
                tags_list = tags_str.split("\n")
                strip_list = [tag.strip().lower() for tag in tags_list]
                game_tags = strip_list
            
            logging.info(f"Scraped game user tags: {game_tags}")
            
            
            
            # Release Date
            release_date_div = self._get_div_content(const.RELEASE_DATE_SELECTOR)
            
            if not isinstance(release_date_div, list):
                release_date_str = release_date_div.text
                date_obj = _get_time_from_str(release_date_str)
                if not date_obj:
                    return _print_scraping_error(steam_id)
                _release_date = date_obj
            
            logging.info(f"Scraped Release Date: {_release_date}")
            
            
            
            
            logging.info(f"Success Fully Scraping Game: {steam_id}")
            game_scraped = GameCache(
                hash=steam_link_hash,
                steam_id=_steam_id,
                title=game_title,
                price=game_price,
                overall_rating=_overall_rating,
                overall_count=_overall_count,
                tags=game_tags,
                release_date=_release_date,
                last_time_scraped=datetime.now()
            )
            
            self.cache_collection.add_game(game_scraped)
            return game_scraped
            
        except Exception as e:
            logging.error(f"Error scraping {steam_id}")
            print(f"Failed to scrape {steam_id}:")
            print(e)
            return None