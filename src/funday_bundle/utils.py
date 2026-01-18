import hashlib, logging, re

from datetime import datetime
from re import Match
from enum import Enum






# Enums
class UrlType(Enum):
    GAME_PAGE = 1
    BUNDLE_PAGE = 2
    GAME_BUNDLE_PAGE = 3

class ReturnInfo(Enum):
    GAME_FOUND_IN_CACHE = 1
    GAME_SCRAPED_SCUCCESFULLY = 2
    FAILED = 3


# Helper functions
def extract_steam_id(url: (str | int)) -> str | None:
    # Finds app_id because the whole link is not needed
    match: (Match[str] | None) = re.search(r'/(app|bundle|bundlelist)/(\d+)', str(url))
    
    if match:
        #url_type: (str | None) = match.group(1)
        steam_id: (str | None) = match.group(2)
        return steam_id
    return ""


def get_url_by_id(steam_id: (str | int), url_type: UrlType) -> str | None:
    cleaned_id = extract_steam_id(steam_id)
    
    if not cleaned_id:
        cleaned_id = str(steam_id)
    
    match url_type:
        case UrlType.GAME_PAGE:
            url_for_page = f"https://store.steampowered.com/app/{cleaned_id}/"
            
        case UrlType.BUNDLE_PAGE:
            url_for_page = f"https://store.steampowered.com/bundle/{cleaned_id}"
            
        case UrlType.GAME_BUNDLE_PAGE:
            url_for_page = f"https://store.steampowered.com/bundlelist/{cleaned_id}/"
            
        case _:
            return ""
    
    return f"{url_for_page}?l=english"


def parse_price(price_str: str) -> float:
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0
    
    
def parse_ratings(raw_rating: str) -> tuple[int, float] | None:
    pattern = r'(\d+)%\s+(?:of the|af de)\s+([\d,.]+)\s+(?:user reviews|brugeranmeldelser)'
    match = re.search(pattern, raw_rating)
    
    if match:
        percent_str = match.group(1)
        count_str = match.group(2)
        
        percentage = float(percent_str) / 100.0
        count = int(count_str.replace(',', '').replace('.', ''))
        
        return count, percentage
    return None

def get_time_from_str(date_str: str) -> datetime | None:
    try:
        clean_date_string = date_str.split('\n')[-1]
        date_object = datetime.strptime(clean_date_string, "%d %b, %Y")
        
        return date_object
    except Exception as e:
        logging.error(f"Error getting date from {str}: {e}")
        return None


def get_hash_from_url(url: str, hash_lenght=16) -> str:
    hash_object = hashlib.sha256(url.encode('utf-8'))    
    return hash_object.hexdigest()[:hash_lenght]


def print_scraping_error(url: (str | int)) -> tuple[None, ReturnInfo]:
    logging.error(f"Error scraping {url}")
    return (None, ReturnInfo.FAILED)
    