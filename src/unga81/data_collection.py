import json
import time
from pathlib import Path

import pandas as pd
import pendulum
import requests
from loguru import logger
from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi

from unga81.config import RAW_DATA_DIR, URL_SPEECHES, DELAY_IN_SECONDS, SPEECH_DIR
from unga81.utils import wordcount


def get_video_url_list(
    url: str = URL_SPEECHES,
    save: bool = True,
    path: Path = RAW_DATA_DIR / "UN Speeches.csv",
) -> pd.DataFrame:
    """Return a dataframe with columns ['url', 'country', 'start', 'end'].

    The function download the spreadsheet, store it locally and then returns
    the stored copy of the spreadsheet.

    Args:
        url (str): URL of the google spreadsheet with the data.
        save (bool, optional): _description_. Defaults to True.
        path (Path, optional): _description_.
            Defaults to DATA_DIR/"UN Speeches.csv".

    Returns:
        pd.DataFrame: Dataframe with data of the speeches.
    """

    def save_spreadsheet(path: Path) -> None:
        with open(path, "wb") as f:
            f.write(response.content)

    logger.info(f"downloading '{url}' and saving it to '{path}'")

    response = requests.get(url)

    if save:
        save_spreadsheet(path)

    df_speech_url = pd.read_csv(path)

    logger.info(f"{df_speech_url.shape[0]:,} speeches found")

    return df_speech_url


def get_transcript(video_id: str) -> FetchedTranscript | None:
    """Collect the transcript from YouTube.

    Args:
        video_id (str): `id` of the YouTube video.

    Returns:
        dict: The video's transcript.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return transcript
    except Exception as e:
        print(e)
        return None


def download_all_transcripts(
    df: pd.DataFrame, overwrite: bool = False, path: Path = SPEECH_DIR
) -> None:
    """Downloads the transcript of all the urls in the dataframe.

    Args:
        df (pd.DataFrame): Dataframe with urls to speeches.
            overwrite (bool, optional): Download again if the file already
            exists. Defaults to False.
        path (Path, optional): Path to save the json files. Defaults to
            DATA_DIR/"2025".
    """
    start = pendulum.now()
    path.mkdir(parents=True, exist_ok=True)
    for i, r in df.iterrows():

        if (path / f"{r['country']}.json").exists() and not overwrite:
            # logger.info(f"{i+1}/{df.shape[0]} {r['country']} transcript exists")  # type: ignore
            continue

        logger.info(f"{i + 1}/{df.shape[0]} {r['country']} downloading transcript")  # type: ignore
        transcript = get_transcript(
            r["url"].split("/")[-1].split("?")[0]
            if "youtu.be" in r["url"]
            else r["url"].split("?v=")[-1]
        )
        time.sleep(DELAY_IN_SECONDS)
        if transcript:
            logger.info(f"{i + 1}/{df.shape[0]} {r["country"]} saving transcript")  # type: ignore
            save_json(transcript.to_raw_data(), r["country"])

    end = pendulum.now()
    logger.info(
        f"Successful download of {df.shape[0]:,} speeches in {(end - start).in_words()}"
    )


def save_json(data: list, country: str, output_path: Path = SPEECH_DIR):
    """Save the transcript as JSON file.

    Args:
        data (dict): `dict` with the transcript.
        country (str): Country of the speech.
        output_path (Path, optional): . Defaults to DATA_DIR/"2025".
    """
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / f"{country}.json", "w") as outfile:
        json.dump(data, outfile)


def get_corpus_from_file(
    country: str, start: int = 0, end: int = 3600, path: Path = SPEECH_DIR
) -> str | None:
    """Returns a string with the transcript of a video.

    Args:
        country (str): Country of origin.
        start (int, optional): Second when the speaker starts speaking.
            Defaults to 0.
        end (int, optional): Second when the speaking finish speaking.
            Defaults to 3600.
        path (Path, optional): Path where the transcripts are stored. Defaults
            to DATA_DIR/"2025".

    Returns:
        str: A string with the transcript of a video.
    """
    if not (path / f"{country}.json").exists():
        logger.warning(f"{country} transcript not found")
        return None

    with open(path / f"{country}.json") as f:
        json_data = json.load(f)
    corpus = [x["text"] for x in json_data if x["start"] > start and x["start"] < end]
    large_corpus = " ".join([x for x in corpus])
    # logger.info(f"{country} transcript found")
    return large_corpus


def get_seconds_from_str(start: str, end: str) -> tuple[int, int]:
    """Return the number of seconds given a 'hh:mm:ss' time.

    Args:
        start (str): Starting time in format "hh:mm:ss".
        end (str): Ending time in format "hh:mm:ss".

    Returns:
        tuple[int, int]: Seconds.
    """
    if isinstance(start, str):
        hours, minutes, seconds = start.split(":")
        start_seconds = int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
    else:
        start_seconds = 0
    if isinstance(end, str):
        hours, minutes, seconds = end.split(":")
        end_seconds = int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
    else:
        end_seconds = 3600
    return start_seconds, end_seconds
