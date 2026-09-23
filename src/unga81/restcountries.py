import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

API_KEY = os.getenv("API_KEY_RESTCOUNTRIES")


def get_country_information(alpha_3: str) -> dict:
    """ADM0_A3 is iso_3.

    Args:
        iso_3 (str): ISO 3.

    Returns:
        dict: Data of the country.
    """
    country_rest = f"https://api.restcountries.com/countries/v5/codes.alpha_3/{alpha_3}"
    response = requests.get(
        country_rest, headers={"Authorization": f"Bearer {API_KEY}"}
    )
    if response.ok:
        logger.info(f"'{alpha_3}' downloaded")
        return response.json()
    else:
        logger.info(f"'{alpha_3}' failed {response.status_code} code")
        return {}


def save_data_country(data: dict, file_path: Path):
    """Save data to JSON file in disk.

    Args:
        data (dict): Data about a country.
        file_path (Path): Path to the JSON file to save the data.
    """
    file_path.parent.absolute().mkdir(exist_ok=True, parents=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"'{file_path.stem}' saved to '{file_path}'")


def download_country_data(alpha_3: str, output_path: Path, overwrite: bool = False):
    """Download data from restcountries.com using the alpha_3 code of a country.

    Args:
        alpha_3 (str): 3-letter country code.
        output_path (Path): Path to the folder to save the data.
        overwrite (bool, optional): Whether or not download again an existing
            file. Defaults to False.
    """
    file_path = output_path / f"{alpha_3}.json"
    if file_path.exists() and not overwrite:
        logger.info(f"'{file_path.name}' exists, skipping download")
        return

    data_pais = get_country_information(alpha_3=alpha_3)
    save_data_country(data=data_pais, file_path=file_path)
