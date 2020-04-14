from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
import os
import csv
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()

s = text("INSERT INTO book(isbn, title, author, year) VALUES(:a, :b, :c, :d)")

with open("book.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    line_count = 0
    for row in csv_reader:

        # skip the headers
        if line_count == 0:
            line_count += 1

    # add each entry to the books table in the database
        else:
            conn.execute(s, a=row[0], b=row[1], c=row[2], d=row[3])
            line_count += 1
