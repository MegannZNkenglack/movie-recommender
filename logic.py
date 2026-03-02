import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
API_KEY = st.secrets["TMDB_API_KEY"] if "TMDB_API_KEY" in st.secrets else os.getenv("TMDB_API_KEY")

# --- DATA FETCHING FUNCTIONS ---
def get_movie_details(movie_id):
    """Fetches Credits (Director, Cast) and Release Dates (Content Rating)"""
    # 1. Get Credits
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    credits = requests.get(credits_url).json()
    
    # 2. Get Release Dates (for US parental rating like PG-13, R)
    release_url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={API_KEY}"
    releases = requests.get(release_url).json().get('results', [])
    
    rating = "N/A"
    for r in releases:
        if r['iso_3166_1'] == "US":
            rating = r['release_dates'][0].get('certification', 'N/A')
            break

    director = next((m['name'] for m in credits.get('crew', []) if m['job'] == 'Director'), "Unknown")
    writers = [m['name'] for m in credits.get('crew', []) if m['job'] in ['Writer', 'Screenplay']][:2]
    stars = [m['name'] for m in credits.get('cast', [])][:3]
    
    return {"director": director, "writers": ", ".join(writers), "stars": ", ".join(stars), "rating": rating}

def get_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    if not res: return []
    
    df = pd.DataFrame(res)
    # Custom Gem Score logic
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Movie Gem Recommender", layout="wide")
st.title("🎬 Movie Gem Recommender")

# Session state for shuffling/refreshing
if 'random_seed' not in st.session_state:
    st.session_state.random_seed = 0

user_input = st.text_input("Enter a movie you loved:", placeholder="e.g. Interstellar")

if user_input:
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(user_input)}"
    search_results = requests.get(search_url).json().get('results', [])
    
    if search_results:
        top_movie = search_results[0]
        st.divider()
        
        # Action Buttons
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("🔄 Refresh List"):
                st.session_state.random_seed += 5
        
        # Get all recommendations and slice based on "Refresh"
        all_recs = get_recommendations(top_movie['id'])
        start_idx = st.session_state.random_seed % max(1, len(all_recs))
        display_recs = all_recs.iloc[start_idx : start_idx + 5]

        if not display_recs.empty:
            for _, movie in display_recs.iterrows():
                details = get_movie_details(movie['id'])
                
                # Create a "Card" for each movie
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        poster_path = movie.get('poster_path')
                        img_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/200x300"
                        st.image(img_url)
                    with col2:
                        st.header(movie['title'])
                        st.write(f"**Rating:** {details['rating']} | **Popularity:** {int(movie['popularity'])} | **Score:** ⭐ {movie['vote_average']}")
                        st.write(f"**Director:** {details['director']}")
                        st.write(f"**Writers:** {details['writers']}")
                        st.write(f"**Stars:** {details['stars']}")
                        st.write(f"**Summary:** {movie['overview']}")
        else:
            st.info("No more recommendations found. Try a different movie!")
    else:
        st.error("Movie not found!")