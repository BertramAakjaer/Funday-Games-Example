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