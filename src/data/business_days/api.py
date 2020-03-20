from typing import Set, List, Union
import logging
import os
import requests

from cachetools import cached
from dotenv import load_dotenv

from pandas import to_datetime, datetime, Series

try:
    from ... import constants
except ImportError:
    from src import constants

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s: %(message)s")

CACHE = {}


@cached(CACHE)
def fetch_data() -> Union[Series, List, datetime]:
    """
    Fetches list of business days from firebase.
    :return:
    """
    url = os.environ.get('FIREBASE_DATABASE_URL')
    url = f'{url}/businessDays/data.json'
    logging.info(f'Fetching business days from {url}')
    resp = requests.get(url).json()
    logging.info(f'Successfully business days fetched {url}')
    resp = resp[-constants.WINDOW:]
    resp = to_datetime(resp, format='%Y%m%d')
    return resp


def clear_cache():
    CACHE.clear()
    logging.debug(f'Cleared business days cache')


if __name__ == '__main__':
    load_dotenv()

    data = fetch_data()
    data = fetch_data()  # logs should only appear once
    print(data)
