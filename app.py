import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# Helper function to get the full poster URL from TMDB
def get_poster_url(path):
    if not path: 
        return "https://via.placeholder.com/500x750?text=No+Poster"
    return f"https://image.tmdb.org/t/p/w500{path}"

# Recommendation logic with genre filtering
def get_recs(movie_title, selected_genre_id=None):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    res = requests.get(search_url).json().get('results')
    if not res: return None
    
    movie_id = res[0]['id']
    recs_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    recs = requests.get(recs_url).json().get('results', [])
    
    # Filter by genre if one is selected
    if selected_genre_id:
        recs = [m for m in recs if selected_genre_id in m.get('genre_ids', [])]
        
    # Return top 5 using your custom Gem Score logic
    for m in recs:
        m['gem_score'] = (m.get('vote_average', 0) * 5) - (m.get('popularity', 0) * 0.1)
    
    recs.sort(key=lambda x: x['gem_score'], reverse=True)
    return recs[:5]

# --- STREAMLIT UI LAYOUT ---
st.set_page_config(page_title="Movie Gem Recommender", layout="wide")
st.title("🎬 Movie Gem Recommender")
st.markdown("Enter a movie you love and discover high-quality 'Hidden Gems' similar to it.")

# Fetch genres for the dropdown
genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
genres = {g['name']: g['id'] for g in requests.get(genre_url).json().get('genres', [])}

# Search Area: Putting search bar and button together
col1, col2 = st.columns([3, 1])
with col1:
    user_movie = st.text_input("Search Movie:", placeholder="e.g. Inception")
with col2:
    genre_name = st.selectbox("Filter Genre:", ["All"] + list(genres.keys()))

# The Button - now directly under the search bar
if st.button("✨ Find My Next Movie", use_container_width=True):
    if user_movie:
        genre_id = genres.get(genre_name) if genre_name != "All" else None
        results = get_recs(user_movie, genre_id)
        
        if results:
            st.divider()
            cols = st.columns(5)
            for i, movie in enumerate(results):
                with cols[i]:
                    st.image(get_poster_url(movie.get('poster_path')))
                    st.subheader(movie['title'])
                    st.caption(f"📅 {movie.get('release_date', 'N/A')}")
                    st.write(f"⭐ {movie['vote_average']}")
        else:
            st.warning("No hidden gems found for that combination. Try a different genre!")
    else:
        st.error("Please enter a movie name first.")