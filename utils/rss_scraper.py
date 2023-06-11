import hashlib
import feedparser
from datetime import date, timedelta
from typing import List, Tuple


def get_rss_hash(rss: str) -> str:
    """
    This function returns a hexadecimal digest associated with a RSS feed

    Parameters
    --------------
        rss: str
            Link pointing to the RSS feed whose digest we want to calculate
    """
    feed = feedparser.parse(rss)
    return hashlib.sha256(str(feed.entries).encode()).hexdigest()

def get_rss_entries(rss: str, publisher_id: int) -> List[Tuple]:
    """
    This function returns the entries in an RSS feed that were published
    in the last week.

    Parameters
    --------------
        rss: str
            The link pointing to the RSS feed we want to parse
        publisher_id: int
            The unique ID that is used to identify a publisher inside the PUBLISHERS
            table in the content_manager database
    
    Returns
    --------------
        articles: list[tuple]
            List of tuple containing the entries published in the last week
    """
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