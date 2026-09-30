import ollama

summary_prompt = """Provide a concise summary of the speech, extracting the most important ideas and concepts. 
Extract the key statistics or data mentioned in the speech. 
Summarize the speech in a specific format, such as a bullet-point list.
Avoid referencing the speaker's personal opinions.
Output ONLY the summary, nothing else.

Speech:
'''{text}'''
"""

countries_mentioned_prompt = """Extract all countries mentioned in this text in exactly what order they appear. 
Format as a comma-separated list with country names only (e.g., "France, Japan, Germany").
Ignore proper nouns that are not standalone countries (cities like Paris don't count).
Output ONLY the ordered list, nothing else.

Text:
'''{text}'''
"""

risks_prompt = """Summarize the risks and challenges discussed in the provided speech.
Identify the points that require attention. Use bullet points to present a concise list of the main risks/concerns.

For each risk, briefly state it AND its source/cause. Do not invent risks beyond what is implied or stated.
Output ONLY the the bullet points, nothing else.

Text:
'''{text}'''
"""

haiku_prompt = """Craft a 3-line haiku inspired by the key themes or messages of the speech. Reply only with the lines of the haiku.
Output ONLY the haiku, nothing else.

Speech:
'''{text}'''
"""

single_word_prompt = """Extract a single word that best represents this entire presidential speech's core message or main point. 
The word should be one the speaker themselves might use when asking "What is THIS about?"
Output ONLY the single word, nothing else.

Speech:
'''{text}'''
"""

hashtags_prompt = """Create a set of relevant hashtags representing this presidential speech's content and themes. 

Requirements:
- Include 5-7 hashtags total
- Prioritize topics that would appear on Twitter/X when discussing this speech
- Mix broad topic tags with more specific keywords 
- Use #hashtags only (no spaces)

Output ONLY the hashtag list, nothing else.

Example output:
#PresidentialSpeech #ClimatePolicy #InternationalRelations #GlobalCooperation #NewAdministration #EconomicGrowth #ForeignPolicyMatters #VotersFirst

Speech:
'''{text}'''
"""

headlines_prompt = """Generate a single impactful newspaper headline for each one of the following styles: 
[leftist, alt-right, environmental, financial, sports] from the following speech. 
Each headline should be unique and accurately reflect the content of the speech. Do not include the name of the paper.

The output should be as follows. Output ONLY the headlines. Nothing else:
- [leftist] <leftist headline>
- [alt-right] <alt-right headline>
- [environmental] <environmental headline>
- [financial] <financial headline>
- [sports] <sports headline>

Speech: 
'''{text}'''"""

yoda_prompt = """Craft a short advice in Yoda's voice, based on the content of the speech. Don't describe it, just write what Yoda would say. 
Output ONLY the Yoda advice, nothing else.

Speech:
'''{text}'''
"""

galaxy_telegram_prompt = """What it the single most relevant idea from the following speech to be send in a telegram to the interfalactic federation of planets in the galaxy?
Output ONLY the idea, nothing else.

Speech:
'''{text}'''
"""


def run_model_prompt(
    model: str, prompt: str, text: str, think: bool = False, temperature: float = 0
):
    """Run a prompt in an Ollama model.

    Args:
        model (str): LLM model that must exists in the Ollama server.
        prompt (str): Prompt to be used.
        text (str): Argument to pass in the prompt.
        think (bool, optional): To limit reasoning models. Defaults to False.

    Returns:
        _type_: Response from the LLM model.
    """
    result = ollama.generate(
        model=model,
        prompt=prompt.format(text=text),
        think=think,
        options={"temperature": temperature},
    )
    return result
