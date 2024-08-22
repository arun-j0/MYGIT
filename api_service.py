import json
import requests
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging as log
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

def get_course_syllabus_beginner(course_name):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are a highly knowledgeable assistant tasked with generating detailed syllabuses for various beginner-level courses. "#level need to be modified
        "For the provided course title, create a syllabus that includes modules and sub-modules in key-value pairs. "
        "Each module should have at least 5 sub-modules. The syllabus should be formatted as follows:\n\n"
        "{\n"
        "    \"Module 1: Module Name\": [\n"
        "        \"Sub-module 1.1: Sub-module Name\",\n"
        "        \"Sub-module 1.2: Sub-module Name\",\n"
        "        \"Sub-module 1.3: Sub-module Name\",\n"
        "        \"Sub-module 1.4: Sub-module Name\",\n"
        "        \"Sub-module 1.5: Sub-module Name\"\n"
        "    ],\n"
        "    \"Module 2: Module Name\": [\n"
        "        \"Sub-module 2.1: Sub-module Name\",\n"
        "        \"Sub-module 2.2: Sub-module Name\",\n"
        "        \"Sub-module 2.3: Sub-module Name\",\n"
        "        \"Sub-module 2.4: Sub-module Name\",\n"
        "        \"Sub-module 2.5: Sub-module Name\"\n"
        "    ],\n"
        "    // Continue with additional modules\n"
        "}\n\n"
        "Ensure that the syllabus is comprehensive and suitable for beginners."
    )
    
    user_message = f"{course_name}"
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            chat_completion = response.json()
            syllabus_text = chat_completion["choices"][0]["message"]["content"]
            
            # Log raw syllabus text for debugging
            log.debug(f"Raw syllabus text: {syllabus_text}")
            
            # Parse the syllabus text into a dictionary
            modules = parse_syllabus_to_dict(syllabus_text)
            
            if modules:
                log.info(f"Syllabus generated and parsed for the course '{course_name}'")
                return modules
            else:
                log.error(f"Failed to parse syllabus format for course '{course_name}'")
                return {"Error": "Failed to parse syllabus format"}
        else:
            log.error(f"Error: {response.status_code} - {response.json()}")
            return {"Error": f"API request failed with status {response.status_code}"}
    
    except requests.RequestException as e:
        log.error(f"Request failed: {e}")
        return {"Error": f"Request failed: {e}"}

def parse_syllabus_to_dict(syllabus_text):
    # Regex to capture module titles and sub-modules
    module_pattern = re.compile(r'"Module \d+: [^"]+"')
    sub_module_pattern = re.compile(r'"Sub-module \d+\.\d+: [^"]+"')

    modules = {}
    current_module = None

    # Log the raw syllabus text
    log.debug(f"Raw syllabus text: {syllabus_text}")

    for line in syllabus_text.splitlines():
        line = line.strip()
        # Check if the line is a module
        module_match = module_pattern.match(line)
        if module_match:
            current_module = module_match.group().strip().strip('"')
            modules[current_module] = []
            log.debug(f"Detected module: {current_module}")
        elif current_module:
            # Check if the line is a sub-module
            sub_module_match = sub_module_pattern.match(line)
            if sub_module_match:
                modules[current_module].append(sub_module_match.group().strip().strip('"'))
                log.debug(f"Detected sub-module: {sub_module_match.group().strip().strip('\"')}")

    return modules
    



def get_chat_completion(message):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Provide detailed explanations with clear headings or subtitles. Focus solely on delivering relevant content. Avoid introductory terms, conclusions, and self-explanatory language. Ensure the response is structured and informative."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        chat_completion = response.json()
        return chat_completion["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.json()}"




def get_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def search_videos(youtube, topic, max_results=10, language='en'):
    try:
        request = youtube.search().list(
            part='snippet',
            q=topic,
            type='video',
            order='relevance',
            maxResults=max_results,
            relevanceLanguage=language
        )
        response = request.execute()

        video_details = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            
            if not is_english(video_title) or not is_english(video_description):
                continue


            video_url = f"https://www.youtube.com/watch?v={video_id}"
            channel_title = item['snippet']['channelTitle']
            published_at = item['snippet']['publishedAt']
            video_details.append({
                'video_id': video_id,
                'title': video_title,
                'url': video_url,
                'channel_title': channel_title,
                'published_at': published_at
            })

        return video_details

    except HttpError as error:
        return f"An HTTP error occurred: {error}"

def is_english(text):
    # Check if the text is primarily in English
    non_english_patterns = [r'\b(?:Hindi|Chinese|French|German|Spanish|Japanese|Korean|Russian)\b',  # Add more languages as needed
                            r'[^\x00-\x7F]+']  # Matches non-ASCII characters
    return not any(re.search(pattern, text, re.IGNORECASE) for pattern in non_english_patterns)

def has_english_captions(youtube, video_id):
    try:
        request = youtube.captions().list(
            part='snippet',
            videoId=video_id
        )
        response = request.execute()

        for item in response.get('items', []):
            if item['snippet']['language'] == 'en':
                return True
        return False

    except HttpError as error:
        return False

def get_video_details(youtube, video_id):
    request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    response = request.execute()
    stats = response['items'][0]['statistics']
    return {
        'views': int(stats['viewCount']),
        'likes': int(stats.get('likeCount', 0)),
        'comments': int(stats.get('commentCount', 0))
    }
