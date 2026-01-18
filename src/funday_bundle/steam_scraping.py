import logging, time, random

from datetime import datetime

import funday_bundle.constants as const
import funday_bundle.utils as util
from funday_bundle.utils import ReturnInfo, UrlType
from funday_bundle.data_structures import CachedCollection, GameCache, BundleCache

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC


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
    



    def _get_game_price(self, element: (WebElement | None)=None) -> float | None:
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
            
            return util.parse_price(str_price)
    
    def _get_game_ratings(self) -> tuple[int, float] | None:
        rating_upper_div = self._get_div_content(const.REVIEW_1_SELECTOR)
        
        if isinstance(rating_upper_div, list):
            return None
        
        rating_div = self._get_div_content(const.REVIEW_2_SELECTOR, element=rating_upper_div)
        
        if not isinstance(rating_div, list):
            content = rating_div.get_attribute("data-tooltip-html")
            if content:
                temp_rating = content.strip().lower()
                return util.parse_ratings(temp_rating)
    
    
    def _scrape_single_game_page(self, steam_id: (str | int)) -> tuple[GameCache | None, ReturnInfo]:
        url = util.get_url_by_id(steam_id, UrlType.GAME_PAGE)
        
        if not url:
            return util.print_scraping_error(steam_id)
        
        hash = util.get_hash_from_url(url)
        logging.info(f"Calculated Hash: {hash}")
        
        game_obj = self.cache_collection.does_game_exists(hash)
        
        if game_obj:
            logging.info(f"Game is already scraped at {game_obj.last_time_scraped}")
            return (game_obj, ReturnInfo.GAME_FOUND_IN_CACHE)
        
        
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
            
            # ID saving
            temp_id = util.extract_steam_id(steam_id)
            if not temp_id:
                return util.print_scraping_error(steam_id)
            
            _steam_id = int(temp_id)
            logging.info(f"Exctracetd ID: {_steam_id}")
            
                        
            # Game Title Extraction
            title_div = self._get_div_content(const.TITLE_SELECTOR)
            
            if not isinstance(title_div, list):
                temp_title: str = title_div.text
                game_title = temp_title.strip().lower()
            
            logging.info(f"Scraped Game Title: {game_title}")
            
                            
            # Game Price
            temp_price = self._get_game_price()
            if not temp_price:
                return util.print_scraping_error(steam_id)
            
            game_price = temp_price
            logging.info(f"Scraped Game Price: {game_price}")
            
            
            # Reviews
            temp_rating = self._get_game_ratings()
                        
            if not temp_rating:
                return util.print_scraping_error(steam_id)
            
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
                date_obj = util.get_time_from_str(release_date_str)
                if not date_obj:
                    return util.print_scraping_error(steam_id)
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
            return (game_scraped, ReturnInfo.GAME_SCRAPED_SCUCCESFULLY)
            
        except Exception as e:
            logging.error(f"Error scraping {steam_id}: e")
            return (None, ReturnInfo.FAILED)
        

    def scrape_game_pages(self, steam_ids: list[str] | list[int]) -> None:
        logging.info(f"Beginning scrpaing of {len(steam_ids)} games")
        for index, steam_id in enumerate(steam_ids):
            logging.info(f"Scraping game nr. {index + 1}: {steam_id}")
            _, return_info = self._scrape_single_game_page(steam_id)

            if (return_info == ReturnInfo.GAME_FOUND_IN_CACHE):
                wait_time: float = 0
            else:
                wait_time: float = random.uniform(2, 5)

            time.sleep(wait_time)