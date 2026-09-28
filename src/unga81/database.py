from pathlib import Path

import pandas as pd
import sqlite3
from loguru import logger

from unga81.config import DATABASE_PATH


def get_db_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    return conn


def create_database(db_path: Path = DATABASE_PATH):
    """Create database.

    Args:
        db_path (Path, optional): Path to the sqlite3 database. Defaults to
            DATABASE_PATH.
    """
    query = """CREATE TABLE IF NOT EXISTS country (
                country TEXT,
                iso_3 TEXT,
                url TEXT,
                full_speech TEXT,
                wordcount INTEGER
                );

                CREATE TABLE IF NOT EXISTS analysis (
                country TEXT,
                iso_3 TEXT,
                summary TEXT,
                countries_mentioned TEXT,
                risks TEXT,
                haiku TEXT,
                single_word TEXT,
                hashtags TEXT,
                headlines TEXT
                yoda TEXT
                );                
                """
    with sqlite3.connect(db_path) as conn:
        conn.executescript(query)
        conn.commit()
        logger.info(f"database created in '{db_path}'")


def insert_into_country(
    conn: sqlite3.Connection, row: pd.Series, speech: str | None, wordcount: int | None
):
    """_summary_

    Args:
        conn (sqlite3.Connection): _description_
        row (pd.Series): _description_
        speech (str | None): _description_
        wordcount (int | None): _description_
    """
    query_delete = """delete from country where country = ?;"""
    query_insert = """INSERT INTO country
            (
                country,
                iso_3,
                url,
                full_speech,
                wordcount
            )
            VALUES(?, ?, ?, ?, ?);"""
    with conn:
        cursor = conn.cursor()
        cursor.execute(query_delete, (row["country"],))
        conn.commit()
        cursor.execute(
            query_insert,
            (row["country"], row["iso_3"], row["url"], speech, wordcount),
        )
        conn.commit()


def get_all_countries(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return all the countries.

    Args:
        conn (sqlite3.Connection): Database connection.

    Returns:
        pd.DataFrame: Data with countries.
    """
    query = """select country, iso_3, url, full_speech, wordcount from country;"""
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [x[0] for x in cursor.description]
        cursor.close()

    df = pd.DataFrame(rows, columns=column_names)
    return df
