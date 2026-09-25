import os

import typer
from dotenv import load_dotenv
from loguru import logger

from unga81.config import EXTERNAL_DATA_DIR
from unga81.restcountries import download_country_data

from unga81.data_collection import (
    get_video_url_list,
    download_all_transcripts,
    get_corpus_from_file,
    get_seconds_from_str,
)
from unga81.database import (
    create_database,
    insert_into_country,
    get_db_connection,
    get_all_countries,
)
from unga81.utils import wordcount

load_dotenv()

API_KEY = os.getenv("API_KEY_RESTCOUNTRIES")
app = typer.Typer()


@app.command()
def update():
    # Transcripts
    df_urls = get_video_url_list()

    # Download the transcripts using the speeches urls
    download_all_transcripts(df_urls, overwrite=False)

    create_database()

    conn = get_db_connection()
    for i, r in df_urls.iterrows():
        start, end = get_seconds_from_str(r["start"], r["end"])
        text = get_corpus_from_file(country=r["country"], start=start, end=end)
        insert_into_country(
            conn=conn,
            row=r,
            speech=text,
            wordcount=wordcount(text=text) if text else None,
        )

    conn.close()

    # Maps
    conn = get_db_connection()
    df = get_all_countries(conn=conn)
    logger.info(f"{df.shape[0]} speeches in the database")

    country_information_path = EXTERNAL_DATA_DIR / "restcountriesapi"
    country_information_path.mkdir(parents=True, exist_ok=True)

    for i, r in df.iterrows():
        if isinstance(r["iso_3"], str):
            download_country_data(
                alpha_3=r["iso_3"], output_path=country_information_path
            )


if __name__ == "__main__":

    app()
