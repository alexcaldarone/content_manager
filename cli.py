import click
from typing import Optional

from api import Link, Publisher, Entry, create_link, create_publisher, create_entry, get_hashes_from_db, update_publisher_hash
from utils.link_data import get_link_data # importing function to get title
from utils.email_scraper import read_email_inbox
from utils.rss_scraper import get_rss_hash, get_rss_entries

@click.help_option(
        """
        This script currently inserts links into your personal content
        manager database.
        It can interact with multiple tables in the databe. At the moment
        it can:
        1 - Save a link with attributes in the LINKS table
        2 - Add links to the LINKS table by reading my email inbox
        3 - Add a publisher to the PUBLISHERS table
        4 - Retrieve the content published by the publishers and add it to the ENTRY table
        
        If you are trying to save a link while also passing the type and 
        category options, remember that the options should go before the
        argument. An example of a correct call to the 'addlink' command is:
        
        python cli.py addlink -t type_name -c category_name link

        Otherwise if you are not passing any options but just want to save a link
        the correct call is:

        python cli.py addlink link

        """
)

@click.group
def mycommands():
    pass

@click.command()
@click.argument("link", type=str, required=1)
@click.option("-t", "--cont_type",
              help="Insert the type of content (youtube, blog post, article...)")
@click.option("-c", "--category",
              help="Insert the category of content (startups, programming, art ...)")
def addLink(link: str, cont_type: Optional[str], category: Optional[str]):
    """
    This function adds a link to the LINKS table by calling the corresponding method
    of the database's api

    Parameters
    --------------
        link: str
            Link we want to save in database
        cont_type: Optional[str]
            The type of content the link falls into 
        category: Optional[str]
            The category of content the link falls into
    """
    date, title = get_link_data(link)
    schema = Link(link=link,
                  title=title,
                  date=date,
                  type=cont_type,
                  category=category)
    create_link(schema)
    click.echo("Link inserted successfully!")

@click.command()
def add_link_from_email():
    """
    This function adds links by reading the email inbox. It inserts the links sent 
    in the day the function is invoked.
    """
    links = read_email_inbox()
    if len(links) == 0:
        click.echo("There are no links to add to the database")
        return None
    for link in links:
    # here i could do without getting the date and recycle date.today()
        date, title = get_link_data(link)
        schema = Link(link=link,
                      title=title,
                      date=date,
                      type=None,
                      category=None)
        create_link(schema)
    click.echo("Links inserted successfully!")

@click.command()
@click.argument("name", type=str, required=1)
@click.argument("website", type=str, required=1)
@click.argument("rss", type=str, required=1)
@click.option("-t", "--pub-type", 
              help="What tye of publisher is it? (podcast, blog...)")
@click.option("-c", "--category", 
              help="Insert the category of content (startups, programming, art ...)")
def add_publisher(name: str, website: str, rss: str, category: Optional[str],
                  pub_type: Optional[str]):
    """
    This function adds a publisher to the PUBLISHERS table by calling the
    corresponding method of the database's api

    Parameters
    --------------
        name: str
            The name of the publisher we want to add
        website: str
            The website of the publisher we want to add
        rss: str
            The link to the publisher's RSS feed
        category: Optional[str]
            The category of content published by the publisher
        type: Optional[str]
            THe type of content published by the publisher
    """
    hash = get_rss_hash(rss)
    schema = Publisher(name=name,
                       website=website,
                       rss=rss,
                       category=category,
                       type=pub_type,
                       hash=hash)
    create_publisher(schema)
    click.echo("Publisher added successfully!")

@click.command()
@click.option("-v", "--verbose", help="Prints added information")
def weekly_entry_update(verbose: bool):
    """
    This function is meant to be run weekly (this can be scheduled by the user).
    It will read the hashes form the PUBLISHERS table and compare them with the ones
    calculated at the moment the function is invoked. If they are different that means
    content has been published, so it is scraped from the rss feed and inserted in the
    ENTRY table. Finally the hash stored in the database is updated

    Parameters
    --------------
        verbose: bool
            If True prints additional information while the function is being executed.
    """
    db_hashes = get_hashes_from_db()
    for item in db_hashes:
        current_hash = get_rss_hash(item["rss"])
        if current_hash != item["hash"]:
            if verbose:
                print(item["name"], "has published something this week")
            
            weekly_entries = get_rss_entries(item["rss"], item["id"])

            for entry in weekly_entries:
                schema = Entry(title=entry[0], 
                               link=entry[1], 
                               publisher=entry[2], 
                               date=entry[3])
                create_entry(schema)
            
            update_publisher_hash(item["id"], current_hash)
        if verbose:
            print(item["name"], "has not published anything this week")
    click.echo("Weekly entries updated successfully")

mycommands.add_command(addLink)
mycommands.add_command(add_link_from_email)
mycommands.add_command(add_publisher)
mycommands.add_command(weekly_entry_update)

if __name__ == "__main__":
    mycommands()