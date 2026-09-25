# UN General Assermbly 81 - Speeches

The app analyses the speech of each country at the #UNGA81 on 22 - 28 September, 2026.

Features:

- Summary of the speech.
- Summary in one word.
- Hashtags from the speech.
- Countries mentioned in the speech with positive and negative sentiment.
- Key stakeholders identified (Corporations, NGOs, individuals mentioned)
- Risks mentioned in the speech.
- Haiku generated with the speech.
- Information about the country.
- Mention of the 17SDGs
- Speech length
- Compare wealth levels with issue priority

The process is the following:

```mermaid
flowchart LR
    data_collection(Download URLs) --> transcripts(Get transcripts)
    transcripts --> summary(LLM summary)
    transcripts --> word(LLM one word)
    transcripts --> haiku(LLM haiku)
    transcripts --> risks(LLM risks)
    transcripts --> other_countries(LLM countries mentioned)

    summary --> streamlit(Streamlit App)
    word --> streamlit(Streamlit App)
    haiku --> streamlit(Streamlit App)
    risks --> streamlit(Streamlit App)
    other_countries --> streamlit(Streamlit App)
    rest(REST Countries API) --> streamlit(Streamlit App)

```

![](images/screenshot.png)

## LLM application

* [x] Summary of the speech
* [x] Summary in one word
* [x] Risks mentioned in the speech
* [ ] List of countries mentioned and sentiment
* [ ] Emotion detection: speech, such as happiness, sadness, anger, or excitement
* [ ] **Inference Generation**: Use LLMs to generate inferences based on the speech content, such as predicting potential consequences of policy decisions oranticipating international reactions.
* [ ] Audio generation in Yoda's style

## Usage locally

### Prerequisites

This repository requires [`uv`](https://docs.astral.sh/uv/getting-started/installation/) and [Ollama](https://ollama.com) installed.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
ollama pull artifish/llama3.2-uncensored
```

### UNGA81 repository

```bash
# Clone this repository
git clone https://github.com/darenasc/unga81.git

# Change directory to repository
cd unga81

# Install dependencies
uv sync

# Run the streamlit app
uv run streamlit run app/app.py

# Download video URLs, transcripts and country information
uv run unga81
```

## Tools used

- Ollama
- sqlite3
- `artifish/llama3.2-uncensored` model
- [plotly](https://docs.plotly.com)
- [REST Countries API](https://restcountries.com)

## Data
- [#UNGA81 - United Nations General Assembly - YouTube playlist](https://www.youtube.com/playlist?list=PLB69IJorxm_g)
- [UNGA81 Speech urls](https://docs.google.com/spreadsheets/d/1qtqfnRSW24j-XLN7SRKywDCuFatARCH8pUg1Rr6I2vI/export?format=csv&gid=1802282131)
- [Admin 0 – Countries](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip)

## Previous years

- [UNGA80](https://unga80.streamlit.app/)
- [UNGA79](https://unga79.streamlit.app/)
- [UNGA78](https://unga-speeches-2023.streamlit.app/)

## **Disclaimer**

This repository contains a project designed to analyze and process speeches from the United Nations using Large
Language Models (LLMs). The purpose of this project is for entertainment and educational purposes only.

**No Endorsement or Guarantee**

The analysis provided by this project should not be considered as an endorsement or guarantee of the accuracy,
completeness, or reliability of the information contained within. This project is intended to provide a general
overview of speech patterns and trends, but it may not capture the full complexity and nuance of the original
speeches.

**Limitations and Caveats**

* The analysis is based on pre-existing data and models, which may be biased towards certain perspectives or
interpretations.
* The LLMs used in this project are trained on vast amounts of text data, including texts that may contain errors,
inaccuracies, or outdated information.
* This project should not be used for decision-making or policy purposes, as the analysis may not provide a
comprehensive understanding of the complex issues involved.

**No Liability**

The repository author and maintainer make no warranties, express or implied, regarding the accuracy,
completeness, or reliability of the information contained within. By using this project, you acknowledge that you
are using it for personal, non-commercial purposes only.

**Attribution**

By using this project, you agree to hold harmless the repository author and maintainer from any claims or
liabilities arising from the use of this project.