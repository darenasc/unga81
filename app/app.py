import json
import sqlite3
from pathlib import Path
from random import randrange

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from unga81 import database
from unga81.config import EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR
from unga81.utils import get_paragraphs

st.set_page_config(
    page_title="#UNGA81",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.logo(
    "https://www.un.org/sg/themes/custom/un3/un3_base/images/logos/UN_logo_en.svg",
    link="https://www.un.org/",
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
    - yoda
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
                                    a.headlines,
                                    a.yoda
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


@st.cache_data
def get_country_data(alpha_3: str):
    file_path = EXTERNAL_DATA_DIR / "restcountriesapi" / f"{alpha_3}.json"
    if not file_path.exists():
        return {}

    with open(file_path, "r") as file:
        data = json.load(file)
    return data


df = get_data(Path(__file__).absolute().parent / "countries.db")
geo_data = get_geodata(EXTERNAL_DATA_DIR / "ne_110m_admin_0_countries.zip")
df_gdp = pd.read_csv(PROCESSED_DATA_DIR / "worldometer.csv")
df_sdg = pd.read_csv(PROCESSED_DATA_DIR / "sdg_countries.csv")


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

    # economic
    if iso_3_selection in df_gdp["iso_3"].to_list():
        gdp = df_gdp[df_gdp["iso_3"] == iso_3_selection]["gdp (us$) wb"].values[0]
        gdp_per_capita = df_gdp[df_gdp["iso_3"] == iso_3_selection][
            "gdp per capita (us$) wb"
        ].values[0]
        population = int(
            df_gdp[df_gdp["iso_3"] == iso_3_selection]["population 2026"].values[0]  # type: ignore
        )
        st.text(
            f"WB GDP (US$): {gdp}\nWB GDP per capita (US$): {gdp_per_capita}\nPopulation (2026): {population:,}"
        )

    # country data
    country_data = get_country_data(alpha_3=iso_3_selection)  # type: ignore
    if "data" in country_data:
        st.write(
            f'Capital: {
            ", ".join([x["name"] for x in country_data["data"]["objects"][0]["capitals"]])}'
        )
        st.write(
            f'Area: {country_data["data"]["objects"][0]["area"]["kilometers"]:,} km2'
        )
        st.write(
            f'Govenrment type: {country_data["data"]["objects"][0]["government_type"]}'
        )
        st.write(
            f'Languages ({len(country_data["data"]["objects"][0]["languages"])}): {
            ", ".join([x["name"] for x in country_data["data"]["objects"][0]["languages"]])}'
        )

        # flag
        st.image(country_data["data"]["objects"][0]["flag"]["url_png"])

        st.divider()

    # links
    if iso_3_selection in df_sdg["Country Code ISO3"].to_list():
        sdf_rank = f"[![](https://img.shields.io/badge/SDG_Rank_{df_sdg[df_sdg['Country Code ISO3']==iso_3_selection]['2026 SDG Index Rank'].values[0]:.0f}/169_({df_sdg[df_sdg['Country Code ISO3']==iso_3_selection]['2026 SDG Index Score'].values[0]:.2f}%)-009EDB)]({df_sdg[df_sdg['Country Code ISO3']==iso_3_selection]['sdg_profile'].values[0]})"
    else:
        sdf_rank = ""

    prominent_color = country_data["data"]["objects"][0]["flag"]["colors"][
        "prominent"
    ].replace("#", "")
    st.markdown(
        f"""[{country_data["data"]["objects"][0]["flag"]["emoji"]}]({country_data["data"]["objects"][0]["links"]["official"]}) [![](https://img.shields.io/badge/{str(country_selection).replace(' ', '_')}-{prominent_color}?logo=wikipedia)]({country_data["data"]["objects"][0]["links"]["wikipedia"]}) {sdf_rank}"""
    )


# st.title(f"{country_selection}")

col1, col2 = st.columns(2)

with col1:
    st.title(f"{country_selection}")
    if iso_3_selection in geo_data["ADM0_A3"].to_list():
        country = geo_data[geo_data["ADM0_A3"] == iso_3_selection]
        m = country.explore(
            popup=[  # type: ignore
                "NAME",
                "FORMAL_EN",
                "ECONOMY",
                "CONTINENT",
                "REGION_UN",
            ],
            tooltip=[  # type: ignore
                "NAME",
                "FORMAL_EN",
                "ECONOMY",
                "CONTINENT",
                "REGION_UN",
            ],
        )
        container_map = st.container(border=True)
        with container_map:
            st_folium(m, use_container_width=True, height=350)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Summary", "Risks", "Countries Mentioned", "Newspaper Headlines"]
    )
    with tab1:
        # Summary
        if df[df["country"] == country_selection]["summary"].values[0]:
            st.markdown(df[df["country"] == country_selection]["summary"].values[0])

    with tab2:
        # Risks
        if df[df["country"] == country_selection]["risks"].values[0]:
            st.markdown(df[df["country"] == country_selection]["risks"].values[0])

    with tab3:
        # Countries Mentioned
        if df[df["country"] == country_selection]["countries_mentioned"].values[0]:
            st.markdown(
                df[df["country"] == country_selection]["countries_mentioned"].values[0]
            )

    with tab4:
        # Headlines
        if df[df["country"] == country_selection]["headlines"].values[0]:
            st.markdown(df[df["country"] == country_selection]["headlines"].values[0])

    # with st.expander(
    #     f"Transcript - {df[df["country"] == country_selection].wordcount.values[0]:,} words"
    # ):
    #     st.text(
    #         f"{get_paragraphs(str(df[df["country"] == country_selection].full_speech.values[0]))}"
    #     )

with col2:
    (
        st.title(
            (
                f'{df[df["country"] == country_selection]["single_word"].values[0]}'
                if df[df["country"] == country_selection]["single_word"].values[0]
                else ""
            ),
            text_alignment="right",
        )
    )
    st.video(df[df["country"] == country_selection]["url"].values[0])  # type: ignore

    if df[df["country"] == country_selection].hashtags.values[0]:
        container_hashtags = st.container(border=True)
        container_hashtags.caption(
            f"{df[df["country"] == country_selection].hashtags.values[0]}",
            text_alignment="center",
        )

    col3, col4 = st.columns(2)

    with col3:
        if df[df["country"] == country_selection]["haiku"].values[0]:
            container_haiku = st.container(border=True)
            container_haiku.markdown("##### Haiku", text_alignment="center")
            # container_haiku.text(
            #     df[df["country"] == country_selection]["haiku"].values[0],
            #     text_alignment="center",
            # )
            container_haiku.markdown(
                str(df[df["country"] == country_selection]["haiku"].values[0]).replace(
                    "\n", "\n\n"
                ),
                text_alignment="center",
            )

    with col4:
        if df[df["country"] == country_selection]["yoda"].values[0]:
            container_yoda = st.container(border=True)
            container_yoda.markdown(
                "##### Master Yoda message", text_alignment="center"
            )
            container_yoda.markdown(
                f'{df[df["country"] == country_selection]["yoda"].values[0]}',
                text_alignment="center",
            )


with st.bottom:
    st.caption("© 2026 Diego Arenas · All rights reserved")
