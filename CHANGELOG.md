# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep A Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v1.0.0.html).

## Unreleased

- Prompt with the main idea for a telegram
- Prompt to generate an entry for the book The Hichhiker's Guide to the Galaxy
- Transcript download button

## [1.0.0]

### Added

- Public streamlit app in https://unga81.streamlit.app
- Database with transcripts of 196 speeches at UNGA81
- Tasks for LLMs using Ollama:
  - Summary generation
  - Risk extraction and identification
  - Country and entity spotting
  - Newspaper headline generation
  - Hashtag generation
  - Yoda speech conversion
  - Single word extraction

### Data Sources

- 196 United Nations General Assembly #81 transcripts obtained from YouTube
- GDP and population of countries from https://www.worldometers.info/
- SDG ranking and link from [Sustainable Development Report database](https://dashboards.sdgindex.org/)
- Country code from [Wikipedia's List_of_ISO_3166_country_codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
- Flag images from [amckenna41/iso3166-flags](https://github.com/amckenna41/iso3166-flags)
- Vector data of countries from [Natural Earth](https://www.naturalearthdata.com)