# Game Bundle Page Selectors
BUNDLE_SECTION_SELECTOR = "[class*='T_3MrEHN9bFK4I4FQqDC8']"
BUNDLE_ELEMENTS_SELECTOR = "[class*='_1NM531LjOd5QmDktUetCOm']"
FOCUSABLE_SELECTOR = "[class*='Focusable']"

# Game Page Selectors
TITLE_SELECTOR = "[class*='apphub_AppName']"
DISCOUNT_ORIGINAL = "[class*='discount_original_price']"
REVIEW_SELECTOR = "[class*='nonresponsive_hidden responsive_reviewdesc']"





###############################
def to_days(days: int) -> int:
    return days * 60 * 60 * 24

MAX_AGE: int = to_days(30)
###############################