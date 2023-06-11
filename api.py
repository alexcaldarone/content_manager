import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from typing import Optional

app = FastAPI()

load_dotenv()

db = mysql.connector.connect(
    host="localhost",
    user=os.environ.get("dbUserName"),
    password=os.environ.get("dbPassword"),
    database="content_manager"
)

class Link(BaseModel):
    link: str = Field(description="The link pointing to the resource")
    title: str = Field(description="The title associated to the resource")
    date: str = Field(description="The date on which the resource was added to the database")
    type: Optional[str] = Field(default=None, description="Indicated the type of resource (article, video, podcast ...)")
    category: Optional[str] = Field(default=None, description="The category of content (math, technology, programming, art, ...)")

class Publisher(BaseModel):
    id: Optional[int] = Field(description="The unique ID that identifies the publisher")
    name: str = Field(description="The name of the publisher")
    website: str = Field(description="Thw publisher's website")
    rss: str = Field(description="The RSS feed where the publisher's content is uploaded")
    category: Optional[str] = Field(description="The category of content published (math, technology, programming, art, ...)")
    type: Optional[str] = Field(default=None, description="Indicated the type of content published (article, video, podcast ...)")
    hash: Optional[str] = Field(description="The hexadecimal digest of the publisher's RSS feed")

class Entry(BaseModel):
    title: str = Field(description="The title of the resouce published by the publisher")
    link: str = Field(description="The title of the resource published by the publisher")
    publisher: int = Field(description="The unique ID of the publisher that published this entry")
    date: Optional[str] = Field(description="The date on which the entry was published")

# Interact with the LINKS table
@app.get("/links")
def get_links():
    """
        ## Get links in table
        This function retrieves all the tuples in the LINKS table

        Returns
        --------------
            items: list[dict]
                List of dictionaries, where each dictionary represents a row of the table
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM links")
    items = [{'link': row[0], 'title': row[1], 'date': row[2], "type":row[3], "category":row[4]} 
             for row in cursor.fetchall()]
    return items

@app.post("/links", status_code=201)
def create_link(item: Link):
    """
        ## Create link 
        This function creates a new row in the LINKS tables

        Paramateres
        --------------
            item: Link
                Link object containing the information we want to add to the table
    """
    cursor = db.cursor()
    cursor.execute("INSERT INTO links VALUES (%s, %s, %s, %s, %s)", 
                   (item.link, item.title, item.date, item.type, item.category))
    db.commit()
    return {"message": "Item inserted successfully"}

@app.get("/links/{link_title}")
def get_links_by_title(link_title: str):
    """
        ## Get link by title
        This function retrieves a row from the LINKS table where the title matches the 
        one passed as argument

        Parameters
        --------------
            link_title: str
                Title of the link we want to retrieve
        
        Returns
        --------------
            (dict) A dictionary containing the fetched row
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM links WHERE title = %s",
                   (link_title,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"link": row[0], 
            "title": row[1],
            "date": row[2],
            "type": row[3],
            "category": row[4]}

@app.put("/links/{old_item_name}")
def update_link(old_item_name: str, newItem: Link):
    """
        ## Update a link
        This function updates a row in the LINKS table where the title attribute 
        matches the one passed as the first argument of this function.

        Parameters
        --------------
            old_item_name: str
                The name of the link whose attributes we want to update
            newItem: Link
                Link object containing the updated information
    """
    cursor = db.cursor()
    cursor.execute("SELECT link, title FROM links WHERE title = %s", (old_item_name, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # i cant change name if its the primary key i am using to identify a link.
    # do i have to change primary key ? (for now i only allow to change date, type, category)
    if newItem.date is not None:
        cursor.execute("UPDATE links SET date = %s WHERE title = %s", 
                       (newItem.date, old_item_name))
    if newItem.type is not None:
        cursor.execute("UPDATE links SET type = %s WHERE title = %s", 
                       (newItem.type, old_item_name))
    if newItem.category is not None:
        cursor.execute("UPDATE links SET category = %s WHERE title = %s", 
                       (newItem.category, old_item_name))
    db.commit()
    return {"message": "Item updated successfully"}

@app.delete("/links/{link_title}")
def delete_link(link_title: str):
    """
        ## Delete link
        This function deletes a row from the LINKS table where the title matches
        the one passed as the functions argument

        Parameters
        --------------
            link_title: str
                Title attribute of the row we want to delete
    """
    cursor = db.cursor()
    cursor.execute("SLEECT * FROM links WHERE title = %s", (link_title, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.execute("DELETE FROM links WHERE title = %s", (link_title, ))
    db.commit()
    return {"message": "Item deleted successfully"}

# Interact with PUBLISERS table
@app.get("/publishers")
def get_publishers():
    """
        ## Get publishers in table
        This function retrieves all the tuples in the PUBLISHERS table

        Returns
        --------------
            items: list[dict]
                List of dictionaries, where each dictionary represents a row of the table
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM publishers")
    items = [{"id": row[0], "name": row[1], "website": row[2], "rss": row[3], "type":row[4], "category":row[5], "hash":row[6]} 
             for row in cursor.fetchall()]
    return items

@app.post("/publishers", status_code=201)
def create_publisher(publisher: Publisher):
    """
        ## Create publisher 
        This function creates a new row in the PUBLISHERS tables

        Paramateres
        --------------
            publisher: Publisher
                Publisher object containing the information we want to add to the table
    """
    cursor = db.cursor()
    cursor.execute("INSERT INTO publishers(name, website, rss, type, category, hash) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (publisher.name, publisher.website, publisher.rss, 
                    publisher.type, publisher.category, publisher.hash))
    db.commit()
    return {"message": "Item inserted successfully"}

@app.put("/publishers/{publisher_name}")
def update_publisher(publisher_name: str, new_publisher: Publisher):
    """
        ## Update a publisher
        This function updates a row in the PUBLISHERS table where the name attribute 
        matches the one passed as the first argument of this function.

        Parameters
        --------------
            publisher_name: str
                The name of the publisher whose attributes we want to update
            new_publisher: Publisher
                Publisher object containing the updated information
    """
    # should I reimplement it using publisher id?
    cursor = db.cursor()
    cursor.execute("SELECT * FROM publishers WHERE name = %s", (publisher_name, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"Item not found"})
    # does it make sense to allow to modify rss?
    if new_publisher.rss is not None:
        cursor.execute("UPDATE publishers SET rss = %s WHERE name = %s",
                       (new_publisher.rss, publisher_name))
    if new_publisher.type is not None:
        cursor.execute("UPDATE publishers SET type = %s WHERE name = %s",
                       (new_publisher.type, publisher_name))
    if new_publisher.category is not None:
        cursor.execute("UPDATE publishers SET category = %s WHERE name = %s",
                       (new_publisher.category, publisher_name))
    if new_publisher.hash is not None:
        cursor.execute("UPDATE publishers SET hash = %s WHERE name = %s",
                       (new_publisher.hash, publisher_name))
    db.commit()
    return {"message": "Item updated successfully"}

@app.delete("/publishers/{publisher_name}")
def delete_publisher(publisher_name: str):
    """
        ## Delete publisher
        This function deletes a row from the PUBLISHERS table where the name matches
        the one passed as the functions argument

        Parameters
        --------------
            name: str
                Name attribute of the row we want to delete
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM publishers WHERE name = %s", (publisher_name, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.execute("DELETE FROM publishers WHERE name = %s", (publisher_name, ))
    db.commit()
    return {"message": "Item deleted successfully"}

@app.get("/publishers/hash")
def get_hashes_from_db():
    """
        ## Get the publisher hashes
        This function retrieves all the hashes associated to the publishers' rss feeds

        Returns
        --------------
            items: list[dict]
                A list of dictionaries, where each dictionary contains a publisher's id, name, 
                rss feed link and hash associated with the rss feed.
    """
    cursor = db.cursor()
    cursor.execute("SELECT id, name, rss, hash FROM publishers")
    items = [{"id": row[0], "name": row[1], "rss":row[2], "hash": row[3]}
             for row in cursor.fetchall()]
    return items

@app.put("/publishers/{publisher_name}/hash")
def update_publisher_hash(publisher_id: int, new_hash: str):
    """
        ## Update publisher hashes
        This function updates the publisher's hash with the new one passes as argument.

        Parameters
        --------------
            publisher_id: int
                The unique id that identifies the publisher
            new_hash: str
                Update hash associated with the publisher's rss feed
    """
    cursor = db.cursor()
    cursor.execute("SELECT id, hash FROM publishers WHERE id = %s", (publisher_id, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"There is no entry in the database with this name"})
    cursor.execute("UPDATE publishers SET hash = %s WHERE id = %s",
                   (new_hash, publisher_id))
    db.commit()
    return {"message": "Hash updated correctly"}

# Interacts with the Entry table
@app.get("/entries")
def get_entries():
    """
        ## Get entries in table
        This function retrieves all the tuples in the ENTRY table

        Returns
        --------------
            items: list[dict]
                List of dictionaries, where each dictionary represents a row of the table
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM entry")
    items = [{"title": row[0], "link": row[1], "publisher": row[2], "date": row[3]}
             for row in cursor.fetchall()]
    return items

@app.post("/entries", status_code=201)
def create_entry(entry: Entry):
    """
        ## Create entry
        This function creates a new row in the ENTRY tables

        Paramateres
        --------------
            entry: Entry
                Entry object containing the information we want to add to the table
    """
    cursor = db.cursor()
    cursor.execute("INSERT INTO entry VALUES (%s, %s, %s, %s)", 
                   (entry.title, entry.link, entry.publisher, entry.date))
    db.commit()
    return {"message": "Item inserted successfully"}

@app.post("/entries/{entry_link}")
def update_entry(entry_link: str, new_entry: Entry):
    pass

@app.delete("/entries/{entry_link}")
def delete_entry(entry_link: str):
    """
        ## Delete entry
        This function deletes a row from the ENTRY table where the link matches
        the one passed as the functions argument

        Parameters
        --------------
            entry_link: str
                Link attribute of the row we want to delete
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM entry WHERE link = %s", (entry_link, ))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException("There is no entry with this link in the table")
    cursor.execute("DELETE FROM entry WHERE link = %s", (entry_link))
    db.commit()
    return {"message": "Item deleted successfully"}