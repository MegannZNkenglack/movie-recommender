import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def get_recommendations(movie_title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(search_url).json()
    if not response.get('results'):
        return None
    
    movie_id = response['results'][0]['id']
    recs_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    recs_data = requests.get(recs_url).json().get('results', [])
    
    if not recs_data:
        return None

    df = pd.DataFrame(recs_data)
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False).head(5)

# --- STREAMLIT UI ---
st.title("🎬 Movie Gem Recommender")

user_movie = st.text_input("Enter a movie you loved:", placeholder="e.g. Inception")

if st.button("Find Gems"):
    if user_movie:
        results = get_recommendations(user_movie)
        if results is not None:
            st.write(f"### Results for '{user_movie}':")
            st.table(results[['title', 'vote_average', 'release_date']])
        else:
            st.error("Movie not found. Try another one!")
    else:
        st.warning("Please enter a movie title first.")