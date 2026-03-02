import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote # Essential for fixing space-related search bugs
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def search_movies(query):
    # 'quote' ensures spaces and special characters don't break the URL
    safe_query = quote(query)
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={safe_query}"
    response = requests.get(url).json()
    return response.get('results', [])

def get_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    recs = requests.get(url).json().get('results', [])
    if not recs: return None
    
    df = pd.DataFrame(recs)
    # Your custom Gem Score logic
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False).head(5)

# --- STREAMLIT UI ---
st.title("🎬 Movie Gem Recommender")

# Session state to handle button clicks for "Did you mean?"
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ""

# Input triggers automatically when user hits 'Enter'
user_input = st.text_input("Enter a movie you loved:", placeholder="e.g. Maze Runner")

# Use a specific variable to track what we are actually searching for
search_term = st.session_state.selected_movie if st.session_state.selected_movie else user_input

if search_term:
    results = search_movies(search_term)
    
    if results:
        top_match = results[0]
        
        # 1. Logic for "Did you mean?" suggestions
        if top_match['title'].lower() != search_term.lower():
            st.write("✨ **Did you mean one of these?**")
            cols = st.columns(min(len(results), 3))
            for i, match in enumerate(results[:3]):
                if cols[i].button(match['title'], key=f"suggest_{match['id']}"):
                    st.session_state.selected_movie = match['title']
                    st.rerun()

        # 2. Display the Results
        st.divider()
        st.write(f"### Hidden Gems similar to **{top_match['title']}**:")
        recommendations = get_recommendations(top_match['id'])
        
        if recommendations is not None:
            # Displaying movie titles and ratings in a clean table
            st.table(recommendations[['title', 'vote_average', 'release_date']])
        else:
            st.info("Found the movie, but no specific 'gems' were found for it yet!")
            
    else:
        st.error(f"Sorry, I couldn't find '{search_term}'. Try checking the spelling!")

# Reset session state if the user types something new manually
if user_input != st.session_state.selected_movie:
    st.session_state.selected_movie = ""