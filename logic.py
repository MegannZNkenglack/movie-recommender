import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote
from dotenv import load_dotenv

# 1. SETUP & KEYS
load_dotenv()
API_KEY = st.secrets["TMDB_API_KEY"] if "TMDB_API_KEY" in st.secrets else os.getenv("TMDB_API_KEY")

# 2. DATA FETCHING FUNCTIONS
def get_max_popularity():
    """Fetches the popularity of the #1 trending movie as a baseline."""
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    return res[0]['popularity'] if res else 1000

def get_movie_details(movie_id):
    """Fetches Credits (Director, Stars) and US Parental Rating."""
    # Get Credits
    cred_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    credits = requests.get(cred_url).json()
    
    # Get Parental Rating (Certification)
    rel_url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={API_KEY}"
    releases = requests.get(rel_url).json().get('results', [])
    
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
    """Gets similar movies and applies the custom Gem Score logic."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    if not res: return pd.DataFrame()
    
    df = pd.DataFrame(res)
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False)

# 3. STREAMLIT UI SETUP
st.set_page_config(page_title="Movie Gem Recommender", layout="wide")
st.title("🎬 Movie Gem Recommender")

if 'random_seed' not in st.session_state:
    st.session_state.random_seed = 0

max_pop = get_max_popularity()
user_input = st.text_input("Enter a movie you loved:", placeholder="e.g. Interstellar")

# 4. MAIN APP LOGIC
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
        
        all_recs = get_recommendations(top_movie['id'])
        
        if not all_recs.empty:
            start_idx = st.session_state.random_seed % len(all_recs)
            display_recs = all_recs.iloc[start_idx : start_idx + 5]

            for _, movie in display_recs.iterrows():
                details = get_movie_details(movie['id'])
                pop_percent = min(100, int((movie['popularity'] / max_pop) * 100))
                
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        p_path = movie.get('poster_path')
                        img = f"https://image.tmdb.org/t/p/w500{p_path}" if p_path else "https://via.placeholder.com/200x300"
                        st.image(img)
                    with c2:
                        st.header(movie['title'])
                        st.write(f"**Rating:** {details['rating']} | **Score:** ⭐ {movie['vote_average']}")
                        st.write(f"**Trending Score:** {pop_percent}%")
                        st.progress(pop_percent / 100)
                        
                        st.write(f"**Director:** {details['director']} | **Stars:** {details['stars']}")
                        st.write(f"**Summary:** {movie['overview']}")
        else:
            st.info("No recommendations found for this movie.")
    else:
        st.error("Movie not found!")