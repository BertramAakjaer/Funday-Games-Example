from funday_bundle.funday_bundle import FundayBundle
import logging


def main():
    app: FundayBundle = FundayBundle()
    
    try:
        logging.info("Starting Program...")
        app()
        
    except Exception as e:
        logging.error("Program Crashed Unexcpectedly")
        logging.exception(f"Detailed stack trace: {e}")
        print("Script failed. Check log file for details.")
        
    finally:
        logging.info("Closing driver...")
        app.end_program()
        

if __name__ == "__main__":
    main()