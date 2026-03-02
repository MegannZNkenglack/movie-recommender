import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote
from dotenv import load_dotenv

# Load local .env for VS Code testing
load_dotenv()

# Streamlit looks for secrets automatically if st.secrets exists
if "TMDB_API_KEY" in st.secrets:
    API_KEY = st.secrets["TMDB_API_KEY"]
else:
    API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"

def search_movies(query):
    if not API_KEY:
        st.error("Missing API Key! Please add it to Streamlit Secrets.")
        return []
    safe_query = quote(query)
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={safe_query}"
    response = requests.get(url).json()
    return response.get('results', [])

def get_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar?api_key={API_KEY}"
    res = requests.get(url).json()
    recs = res.get('results', [])
    if not recs: return None
    
    df = pd.DataFrame(recs)
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False).head(5)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Movie Gem Recommender", layout="centered")
st.title("🎬 Movie Gem Recommender")

user_input = st.text_input("Enter a movie you loved:", placeholder="e.g. Thor")

if user_input:
    results = search_movies(user_input)
    
    if results:
        top_match = results[0]
        
        # Did you mean logic
        if top_match['title'].lower() != user_input.lower():
            st.write("✨ **Did you mean?**")
            cols = st.columns(3)
            for i, match in enumerate(results[:3]):
                if cols[i].button(match['title'], key=match['id']):
                    # This will trigger a rerun with the correct title
                    st.info(f"Searching for {match['title']}...")
                    results = search_movies(match['title'])
                    top_match = results[0]

        st.divider()
        st.subheader(f"Hidden Gems similar to {top_match['title']}")
        
        # Display Movie Info
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            poster = top_match.get('poster_path')
            url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else "https://via.placeholder.com/150"
            st.image(url)
        with col_txt:
            st.write(top_match.get('overview', 'No description available.'))
            st.write(f"**Release Date:** {top_match.get('release_date')}")

        # Recommendations Table
        recs = get_recommendations(top_match['id'])
        if recs is not None:
            st.write("### Our Top Recommendations")
            st.dataframe(recs[['title', 'vote_average', 'release_date']], use_container_width=True)
    else:
        st.warning(f"No results found for '{user_input}'. Try checking the spelling!")