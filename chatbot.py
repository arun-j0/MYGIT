import streamlit as st
from api_service import get_chat_completion, get_youtube_service, search_videos, get_video_details
from utils import calculate_rating, calculate_title_relevance_score
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

def find_top_rated_videos(api_key, topics):
    youtube = get_youtube_service(api_key)
    all_results = {}

    for topic in topics:
        videos = search_videos(youtube, topic)
        if isinstance(videos, str):
            return videos  # Return the error message if an error occurred
        
        results = []
        for video in videos:
            video_id = video.get('video_id')
            if not video_id:
                continue

            video_details = get_video_details(youtube, video_id)
            if isinstance(video_details, str):
                return video_details  # Return the error message if an error occurred
            
            title_relevance_score = calculate_title_relevance_score(video.get('title', ''), topic)
            
            if video_details.get('comments', 0) >= 20:
                rating = calculate_rating(video_details, title_relevance_score)
                
                results.append({
                    'title': video.get('title', 'No Title'),
                    'channel_name': video.get('channel_title', 'No Channel Name'),
                    'date_uploaded': video.get('published_at', 'Unknown Date'),
                    'rating': rating,
                    'url': video.get('url', '#'),
                    'video_id': video_id
                })
        
        results.sort(key=lambda x: x['rating'], reverse=True)
        all_results[topic] = results[:1]  # Get top 1 video for each topic
    
    return all_results

def chatbot(selected_course, selected_module, selected_sub_module, keyword=None, keywords=None):
    # Clean up sub_module name
    index = selected_sub_module.find(":")
    if index != -1:
        selected_sub_module = selected_sub_module[index + 1:].strip()
    
    st.subheader(f"Clear Your Doubts on {selected_sub_module} in {selected_course}")

    # Initialize the session state if it doesn't exist
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = keyword

    # Create dynamic placeholder text
    placeholder_text = f"{st.session_state.selected_keyword} (in {selected_course})" if st.session_state.selected_keyword else ""
    
    # Update the text input box value based on the session state
    user_input = st.text_input("Your Question:", value=placeholder_text, help=placeholder_text)
    
    # Button to send user input to the bot
    if st.button("Send"):
        if user_input:
            # Include keyword in the prompt if provided
            prompt = f"{user_input} {st.session_state.selected_keyword} in {selected_course}"
            bot_response = get_chat_completion(prompt)
            st.write("**Bot Response:**")
            st.write(bot_response)
        else:
            st.write("Please enter a question.")

    # Button to find and display top-rated videos
    if st.button("Facing difficulties? Watch a tutorial"):
        # Construct the topic based on submodule and course
        topic = f"{selected_sub_module} in {selected_course}"
        top_videos = find_top_rated_videos(youtube_api_key, [topic])
        
        if isinstance(top_videos, str):
            st.error(top_videos)
        else:
            for concept, videos in top_videos.items():
                st.write(f"**Tutorials for '{concept}':**")
                for video in videos:
                    st.write(f"**{video['title']}**")
                    st.write(f"Channel: {video['channel_name']}")
                    st.write(f"Uploaded on: {video['date_uploaded']}")
                    st.write(f"[Watch Video]({video['url']})")
                    st.video(video['url'])

    # Render keywords inside the expander
    if keywords:
        st.subheader("Keywords")
        long_keywords = [k for k in keywords if len(k) > 20]
        short_keywords = [k for k in keywords if len(k) <= 20]

        if long_keywords:
            for keyword in long_keywords:
                cleaned_keyword = keyword.replace(":", "")
                if st.button(f"{cleaned_keyword}", key=f"long_keyword_{cleaned_keyword}", help="Click to select"):
                    st.session_state.selected_keyword = cleaned_keyword
                    # No need to rerun; the input box value is directly updated

        if short_keywords:
            buttons_per_row = 2
            num_rows = (len(short_keywords) + buttons_per_row - 1) // buttons_per_row

            for row in range(num_rows):
                cols = st.columns(buttons_per_row)
                for col in range(buttons_per_row):
                    index = row * buttons_per_row + col
                    if index < len(short_keywords):
                        keyword = short_keywords[index]
                        cleaned_keyword = keyword.replace(":", "")
                        with cols[col]:
                            if st.button(f"{cleaned_keyword}", key=f"short_keyword_{cleaned_keyword}_{index}", help="Click to select"):
                                st.session_state.selected_keyword = cleaned_keyword
                                # No need to rerun; the input box value is directly updated

# Ensure this script is run directly
if __name__ == "__main__":
    st.title("Chatbot and Tutorial Finder")
