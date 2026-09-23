from pathlib import Path

UNGA_VERSION = "UNGA81"
URL_SPEECHES = "https://docs.google.com/spreadsheets/d/1qtqfnRSW24j-XLN7SRKywDCuFatARCH8pUg1Rr6I2vI/export?format=csv&gid=1802282131"
DELAY_IN_SECONDS = 5.0

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

SPEECH_DIR = RAW_DATA_DIR / UNGA_VERSION
APP_DIR = ROOT_DIR / "app"
DATABASE_PATH = APP_DIR / "countries.db"

APP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
SPEECH_DIR.mkdir(parents=True, exist_ok=True)
