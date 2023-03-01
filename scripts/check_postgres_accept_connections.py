import sys
import time
import logging

import psycopg2

from users_db.config import get_postgres_uri

logger = logging.getLogger("dbinit")


def postgres_check():
    while True:
        try:
            conn = psycopg2.connect(get_postgres_uri())
            logger.info(f"Connecting {conn} successfully established")
            return
        except Exception as e:
            logger.error(f"Exception({type(e)}): {e}")
            time.sleep(1)


if __name__ == "__main__":
    sys.exit(postgres_check())
