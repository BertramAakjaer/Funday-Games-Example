from funday_bundle.funday_bundle import FundayBundle
import logging


def main():
    app: FundayBundle = FundayBundle()
    
    try:
        app()
        
    except Exception as e:
        logging.error("Attempted to divide by zero!")
        logging.exception("Detailed stack trace:")
        print("Script failed. Check log file for details.")
        
    finally:
        logging.info("Closing driver...")
        app.end_program()
        

if __name__ == "__main__":
    main()