import logging, os
from datetime import datetime

from funday_bundle.funday_bundle import FundayBundle

def init_project():
    # Making folders for data storage
    if not os.path.exists("scraped_data"):
        os.makedirs("scraped_data")
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(
        filename=os.path.join("logs", f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a"
    )


def main():
    init_project()

    app: FundayBundle = FundayBundle()
    
    try:
        logging.info("Starting Program...")
        app()
        
    except Exception as e:
        logging.error("Program Crashed Unexcpectedly")
        logging.exception(f"Details: {e}")
        print("Script failed. Check log file for details.")
        
    finally:
        logging.info("Closing driver...")
        app.end_program()

if __name__ == "__main__":
    main()