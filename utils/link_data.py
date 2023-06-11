from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from datetime import date
from typing import Tuple 

def get_link_data(link: str) -> Tuple[str, str]:
    """
    This function retrieves the title of the webpage where the 
    link passed as argument points to

    Parameters
    --------------
        link: str
            The link of the webpage whose title we want to retrieve
    
    Returns
    --------------
        today: str
            A string containing today's date
        b.title.string: str
            The webpage's title
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}
    r = Request(link, headers=hdr)
    page = urlopen(r)
    b = BeautifulSoup(page, features="html.parser")
    today = str(date.today())
    return today, b.title.string