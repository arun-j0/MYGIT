# utils.py
import re

def is_english(text):
    non_english_patterns = [
    r'\b(?:Hindi|हिंदी|Chinese|中文|French|Français|German|Deutsch|Spanish|Español|Japanese|日本語|Korean|한국어|Russian|Русский|दोस्तों|आप|देखना|लाइक|सब्सक्राइब|कमेंट|शेयर|वीडियो|चैनल|नए)\b',
    r'[^\x00-\x7F]+'
]
    return not any(re.search(pattern, text, re.IGNORECASE) for pattern in non_english_patterns)

def calculate_title_relevance_score(title, topic):
    return 1.0 if topic.lower() in title.lower() else 0.0

def calculate_rating(video_details, title_relevance_score):
    views = video_details['views']
    likes = video_details['likes']
    comments = video_details['comments']

    normalized_views = views / 1_000_000
    normalized_comments = comments / 1_000

    rating = (0.6 * title_relevance_score) + (0.2 * (likes / (views + 1))) + (0.1 * normalized_views) + (0.2 * normalized_comments)
    return round(min(rating * 10, 10), 1)

def parse_query(query):
    concepts = [concept.strip() for concept in re.split(r'\s*,\s*|\s+and\s+|\s+or\s+', query)]
    final_concepts = [concept + " in Python" if len(concept.split()) == 1 else concept for concept in concepts]
    return final_concepts
