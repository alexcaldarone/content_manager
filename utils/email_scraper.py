import email
from dotenv import load_dotenv
import os
import imaplib
import re
from datetime import date

MONTH_REFERENCES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

def read_email_inbox():
    link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    today = date.today()
    today_str_query = f"{today.day}-{MONTH_REFERENCES[today.month]}-{today.year}"
    links = []

    load_dotenv()
    username = os.environ.get("gmailUserEmail")
    password = os.environ.get("gmailAppPassword")
    
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(username, password)
    server.select("Links")
    response, items = server.search(None, f'(SINCE "{today_str_query}")')
    items = items[0].split()
    if response != "OK":
        return None
    for item in items:
        response2, data = server.fetch(item, "(UID BODY[TEXT])")
        
        for element in data:
            if isinstance(element, tuple):
                message = email.message_from_bytes(element[1])
                matches = re.findall(link_pattern, message.as_string())
                break
        if len(matches) > 1:
            for match in matches: 
                # check that it's not already in list
                if match not in links and "</a>" not in match and "</div>" not in match: 
                    links.append(match)
        else: links = [matches[0]]
    
    return links