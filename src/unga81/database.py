from pathlib import Path
from typing import Literal

import pandas as pd
import sqlite3
from loguru import logger

from unga81.config import DATABASE_PATH
from unga81.prompts import run_model_prompt


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


def insert_into_analysis(conn: sqlite3.Connection, data: dict):
    query_delete = """delete from analysis where country = ?;"""
    query_insert = """INSERT INTO analysis
                    (country,
                     iso_3,
                     summary,
                     countries_mentioned,
                     risks,
                     haiku,
                     single_word,
                     hashtags,
                     headlines,
                     yoda)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    with conn:
        cursor = conn.cursor()
        cursor.execute(query_delete, (data["country"],))
        conn.commit()

        cursor.execute(
            query_insert,
            (
                data["country"],
                data["iso_3"],
                data["summary"],
                data["countries_mentioned"],
                data["risks"],
                data["haiku"],
                data["single_word"],
                data["hashtags"],
                data["headlines"],
                data["yoda"],
            ),
        )
        conn.commit()


PromptType = Literal[
    "summary",
    "countries_mentioned",
    "risks",
    "haiku",
    "single_word",
    "hashtags",
    "headlines",
    "yoda",
]


def update_analysis_column(
    conn: sqlite3.Connection,
    country: str,
    iso_3: str,
    column_name: PromptType,
    text: str,
):
    """Update a specific column in the `analysis` table.

    Posible values in `column_name` are the ones in `PromptType`:
    - summary
    - countries_mentioned
    - risks
    - haiku
    - single_word
    - hashtags
    - headlines
    - yoda

    Args:
        conn (sqlite3.Connection): Database connection.
        country (str): Country to be updated in full name.
        iso_3 (str): Code ISO 3 of the country to be updated.
        column_name (PromptType): Column name in the analysis table.
        text (str): Value of the column to be inserted.
    """
    query_check = """select * from analysis where country = ?;"""
    query_update = f"""update analysis set {column_name} = ? where country = ?;"""
    with conn:
        cursor = conn.cursor()
        cursor.execute(query_check, (country,))
        rows = cursor.fetchone()
        if rows is None:
            # insert
            logger.info(f"Inserting data into 'analysis.{column_name}' for {country}")
            cursor.execute(
                f"insert into analysis (country, iso_3, {column_name}) values (?, ?, ?);",
                (
                    country,
                    iso_3,
                    text,
                ),
            )
            conn.commit()

        else:
            # update
            logger.info(f"Updating data into 'analysis.{column_name}' for {country}")
            cursor.execute(
                query_update,
                (
                    text,
                    country,
                ),
            )
            conn.commit()


def check_analysis_column(
    conn: sqlite3.Connection, country: str, column_name: PromptType
) -> bool:
    """Check if a record about the `country` exists in the database to decide
    whether to insert a new record or to update the existing one.

    Args:
        conn (sqlite3.Connection): Database connection.
        country (str): Country to check in the analysis table.
        column_name (PromptType): _description_

    Returns:
        bool: _description_
    """
    query = f"""select {column_name} from analysis where country = ?;"""
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, (country,))
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return False
        else:
            if row[0] is None:
                return False
            else:
                return True


def update_prompt_result(
    conn: sqlite3.Connection,
    prompt_name: PromptType,
    prompt: str,
    model: str,
    country: str,
    iso_3: str,
    text: str,
    overwrite: bool = False,
):
    """Update the database with the results of a given prompt for a given country.

    Args:
        conn (sqlite3.Connection): Database connection.
        prompt_name (PromptType): Prompt to be used.
        prompt (str): Prompt to be used.
        model (str): LLM model that must exists in the local Ollama server.
        country (str): Country to be updated.
        iso_3 (str): Country code.
        text (str): Speech.
        overwrite (bool, optional): Whether or not to overwrite an existing
            record. Defaults to False.
    """
    if (
        check_analysis_column(conn=conn, country=country, column_name=prompt_name)
        and not overwrite
    ):
        return

    logger.info(f"Running '{prompt_name}' prompt with model '{model}' for {country}")
    result = run_model_prompt(model=model, prompt=prompt, text=text)
    logger.info(f"Updating '{prompt_name}' with '{model}' for {country}")
    update_analysis_column(
        conn=conn,
        country=country,
        iso_3=iso_3,
        column_name=prompt_name,
        text=str(result["response"]),
    )
