from mongo_connect import client
from postgres_connect import connection
from datetime import datetime

db = client["hw-8"]


def get_quotes_from_mongo():
    quotes = db.quote.find()
    return quotes


def get_authors_from_mongo():
    authors = db.author.find()
    return authors


def fill_authors_to_postgres(authors, cursor):
    fill_authors = [(author["fullname"], author["born_date"], author["born_location"], author["description"]) for author in authors]
    
    sql = "insert into authors_author(fullname, born_date, born_location, description) values(%s, %s, %s, %s)"
    cursor.executemany(sql, fill_authors)


def fill_quotes_to_postgres(quotes, cursor):
    for quote in quotes:
        author = db.author.find_one({"_id": quote["author"]})

        author_id_sql = "select id from authors_author where fullname = %s"
        cursor.execute(author_id_sql, (author["fullname"],))
        author_id = cursor.fetchone()

        sql = """insert into quotes_quote(tags, quote, author_id) values(%s, %s, %s)"""
        cursor.execute(sql, (quote["tags"], quote["quote"], author_id[0]))

if __name__ == "__main__":
    quotes = get_quotes_from_mongo()
    authors = get_authors_from_mongo()

    with connection() as conn:
        cur = conn.cursor()
        fill_authors_to_postgres(authors, cur)
        fill_quotes_to_postgres(quotes, cur)

