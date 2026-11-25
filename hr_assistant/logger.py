"""Step 0: shared logger used by every other step.

Every module in this app asks this file for a logger instead of
setting up its own. That way all the logs (from document loading
to the final answer) end up in one place, in one consistent format.

"""

import logging
import os
from datetime import datetime

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

_run_started_at = datetime.now()
date_folder = _run_started_at.strftime("%Y-%m-%d")
time_suffix = _run_started_at.strftime("%H%M%S")

date_log_dir = os.path.join(LOGS_DIR, date_folder)
os.makedirs(date_log_dir, exist_ok=True)

RUN_LOG_FILE = os.path.join(date_log_dir, f"run_{time_suffix}.log")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(RUN_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)