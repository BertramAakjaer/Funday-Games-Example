# Game Bundle Page Selectors
BUNDLE_SECTION_SELECTOR = "[class*='T_3MrEHN9bFK4I4FQqDC8']"
BUNDLE_ELEMENTS_SELECTOR = "[class*='_1NM531LjOd5QmDktUetCOm']"
FOCUSABLE_SELECTOR = "[class*='Focusable']"



# Game Page Selectors
TITLE_SELECTOR = "[class*='apphub_AppName']"
PRICE_WRAPPER_SELECTOR = "[class*='game_area_purchase_game_wrapper']"
DISCOUNT_ORIGINAL_PRICE = "[class*='discount_original_price']"
NORMAL_GAME_PRICE = "[class*='game_purchase_price']"
REVIEW_1_SELECTOR = "[class*='outlier_totals global review_box_background_secondary']"
REVIEW_2_SELECTOR = "[class*='game_review_summary positive']"
TAGS_SELECTOR = "[class*='app_tags popular_tags']" # User given tags
BUTTON_TAGS = "[class*='app_tag add_button']" # Button to tags
RELEASE_DATE_SELECTOR = "[class*='release_date']"


###############################
def to_days(days: int) -> int:
    return days * 60 * 60 * 24

MAX_AGE: int = to_days(30)
###############################