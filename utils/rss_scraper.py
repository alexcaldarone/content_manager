import hashlib
import feedparser
from datetime import date, timedelta
from typing import List, Tuple


def get_rss_hash(rss: str) -> str:
    # sto calcolando la hash della lista che contiene le entries del rss feed
    # teoricamente quando viene aggiunta una nuova dovrebbe cambiare
    feed = feedparser.parse(rss)
    return hashlib.sha256(str(feed.entries).encode()).hexdigest()

def get_rss_entries(rss: str, publisher_id: int) -> List[Tuple]:
    # this function gets the entries of the rss feed from the last week
    today = date.today()
    last_week = today - timedelta(7)
    feed = feedparser.parse(rss)
    articles = [] # temporary measure

    for entry in feed.entries:
        if entry.updated_parsed > last_week.timetuple():
            parsed_date = f"{entry.updated_parsed.tm_year}-{entry.updated_parsed.tm_mon}-{entry.updated_parsed.tm_mday}"
            schema_tuple = (entry.title, entry.link, publisher_id, parsed_date)
            articles.append(schema_tuple)
        else:
            break
    return articles