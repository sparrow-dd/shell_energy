import logging
from datetime import datetime

# get current date time
now = datetime.now()

now_str = now.strftime("%Y%m%d")
# create and config logger

format = "%(asctime)s - %(name)s [%(levelname)s] - %(message)s"
filename = f"logs\log_file_{now_str}.log"

logging.basicConfig(filename = filename,
                    filemode = "a",
                    format = format, 
                    level = logging.INFO)

logger = logging.getLogger()

reportname = f"reports\inspect_report_{now_str}.txt"
report = open(reportname,"a")