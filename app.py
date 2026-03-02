import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# Helper function to get the full poster URL
def get_poster_url(path):
    if not path: return "https://via.placeholder.com/500x750?text=No+Poster"
    return f"https://image.tmdb.org/t/p/w500{path}"

# Helper to get recommendations with a genre filter
def get_recs(movie_title, selected_genre_id=None):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    res = requests.get(search_url).json().get('results')
    if not res: return None
    
    movie_id = res[0]['id']
    recs_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    recs = requests.get(recs_url).json().get('results', [])
    
    # Apply Genre Filter if selected
    if selected_genre_id:
        recs = [m for m in recs if selected_genre_id in m.get('genre_ids', [])]
        
    return recs[:5] # Return top 5

# --- STREAMLIT UI ---
st.title("🎬 Movie Gem Recommender")

# Get Genre list for the dropdown
genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
genres = {g['name']: g['id'] for g in requests.get(genre_url).json().get('genres', [])}

# Sidebar inputs
with st.sidebar:
    st.header("Settings")
    user_movie = st.text_input("Enter a movie you love:", "Inception")
    genre_name = st.selectbox("Optional: Filter by Genre", ["All"] + list(genres.keys()))

if st.button("Find Gems"):
    genre_id = genres.get(genre_name) if genre_name != "All" else None
    results = get_recs(user_movie, genre_id)
    
    if results:
        # Create columns for the posters
        cols = st.columns(5)
        for i, movie in enumerate(results):
            with cols[i]:
                st.image(get_poster_url(movie.get('poster_path')))
                st.write(f"**{movie['title']}**")
                st.caption(f"⭐ {movie['vote_average']}")
    else:
        st.error("No recommendations found with those settings!")