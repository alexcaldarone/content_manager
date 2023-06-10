from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from datetime import date
from typing import Tuple 


def get_link_data(link: str) -> Tuple[str, str]:
    hdr = {'User-Agent': 'Mozilla/5.0'}
    r = Request(link, headers=hdr)
    page = urlopen(r)
    b = BeautifulSoup(page, features="html.parser")
    today = str(date.today())
    return today, b.title.string