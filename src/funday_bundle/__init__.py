import logging, os
from datetime import datetime

# Making folders for data storage
if not os.path.exists("scraped_data"):
    os.makedirs("scraped_data")
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename= os.path.join("logs", f"{datetime.now().strftime("%Y-%m-%d")}.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a"
)