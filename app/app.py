import sqlite3
from pathlib import Path
from random import randrange

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from unga81 import database
from unga81.config import EXTERNAL_DATA_DIR
from unga81.utils import get_paragraphs

st.set_page_config(
    page_title="#UNGA81",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_data(db: Path):
    """Returns a pd.DataFrame with the following columns:
    - country
    - url
    - full_speech
    - summary
    - countries_mentioned
    - risks
    - haiku
    - word
    """
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        rows = cursor.execute("""SELECT
                                    c.country,
                                    c.iso_3,
                                    c.url,
                                    c.full_speech,
                                    c.wordcount,
                                    a.summary,
                                    a.countries_mentioned,
                                    a.risks,
                                    a.haiku,
                                    a.single_word,
                                    a.hashtags,
                                    a.headlines
                                FROM
                                    country as c left join analysis as a
                                    on c.country = a.country ;""").fetchall()
        column_names = [x[0] for x in cursor.description]
        cursor.close()

    df = pd.DataFrame(rows, columns=column_names)
    return df


@st.cache_data
def get_geodata(file_path: Path = EXTERNAL_DATA_DIR / "ne_110m_admin_0_countries.zip"):
    geo_data = gpd.read_file(file_path)
    geo_data["POPULATION (EST)"] = geo_data["POP_EST"].apply(lambda x: f"{int(x):,}")
    geo_data["GDP (MD)"] = geo_data["GDP_MD"].apply(lambda x: f"${int(x):,}")
    return geo_data


df = get_data(Path(__file__).absolute().parent / "countries.db")
geo_data = get_geodata(EXTERNAL_DATA_DIR / "ne_110m_admin_0_countries.zip")
# geo_data = gpd.read_file(EXTERNAL_DATA_DIR / "ne_110m_admin_0_countries.zip")
# geo_data["POPULATION (EST)"] = geo_data["POP_EST"].apply(lambda x: f"{int(x):,}")
# geo_data["GDP (MD)"] = geo_data["GDP_MD"].apply(lambda x: f"${int(x):,}")

if "random_initial_country" not in st.session_state:
    st.session_state.random_initial_country = randrange(len(df))
    st.session_state.disabled = False

with st.sidebar:
    st.caption(f"{df.shape[0]} speeches")

    country_selection = st.selectbox(
        "Country",
        df["country"].sort_values().to_list(),
        index=st.session_state.random_initial_country,
    )  # type: ignore
    iso_3_selection = df[df["country"] == country_selection].iso_3.values[0]
    st.caption(iso_3_selection)
    st.divider()

st.title(f"{country_selection}")

col1, col2 = st.columns(2)

with col1:
    if iso_3_selection in geo_data["ADM0_A3"].to_list():
        country = geo_data[geo_data["ADM0_A3"] == iso_3_selection]
        m = country.explore(
            popup=[  # type: ignore
                "ADM0_A3",
                "NAME",
                "FORMAL_EN",
                "POPULATION (EST)",
                "POP_YEAR",
                "GDP (MD)",
                "GDP_YEAR",
                "ECONOMY",
                "CONTINENT",
                "REGION_UN",
            ],
            tooltip=[  # type: ignore
                "ADM0_A3",
                "NAME",
                "FORMAL_EN",
                "POPULATION (EST)",
                "POP_YEAR",
                "GDP (MD)",
                "GDP_YEAR",
                "ECONOMY",
                "CONTINENT",
                "REGION_UN",
            ],
        )
        st_folium(m)

    st.subheader(f"{df[df["country"] == country_selection].hashtags.values[0]}")

    if df[df["country"] == country_selection]["summary"].values[0]:
        st.header("Summary")
        st.markdown(df[df["country"] == country_selection]["summary"].values[0])

    with st.expander(
        f"Transcript - {df[df["country"] == country_selection].wordcount.values[0]:,} words"
    ):
        st.text(
            f"{get_paragraphs(str(df[df["country"] == country_selection].full_speech.values[0]))}"
        )

with col2:
    st.video(df[df["country"] == country_selection]["url"].values[0])  # type: ignore

    col3, col4 = st.columns(2)

    with col3:
        if df[df["country"] == country_selection]["haiku"].values[0]:
            st.header("Haiku")
            st.text(df[df["country"] == country_selection]["haiku"].values[0])

    with col4:
        if df[df["country"] == country_selection]["single_word"].values[0]:
            st.header("In One Word")
            st.title(
                f'{df[df["country"] == country_selection]["single_word"].values[0]}'
            )
