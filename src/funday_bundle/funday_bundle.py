import logging

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class FundayBundle:

    # run as app() instead of app.run()
    def __call__(self) -> None:
        # Optain Page to scrape

        # Scrape HTML


        # Find Bundle Candidates and parse into class


        # Validate for bundle based on demands


        # Put 
        pass
        
