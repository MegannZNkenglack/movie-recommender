import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def search_movies(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
    return requests.get(url).json().get('results', [])

def get_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    recs = requests.get(url).json().get('results', [])
    if not recs: return None
    
    df = pd.DataFrame(recs)
    # Your proprietary Gem Score logic
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df.sort_values(by='gem_score', ascending=False).head(5)

# --- STREAMLIT UI ---
st.title("🎬 Movie Gem Recommender")

# Session state to handle clickable suggestions
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# text_input automatically handles the 'Enter' key
user_input = st.text_input("Enter a movie you loved:", value=st.session_state.search_query, placeholder="e.g. Thor")

if user_input:
    results = search_movies(user_input)
    
    if results:
        # Check if the first result is an exact match or very close
        top_match = results[0]
        
        # UI for "Did you mean?" if there are multiple results
        if len(results) > 1 and top_match['title'].lower() != user_input.lower():
            st.write("✨ **Did you mean one of these?**")
            cols = st.columns(min(len(results), 3))
            for i, match in enumerate(results[:3]):
                if cols[i].button(match['title'], key=f"btn_{match['id']}"):
                    st.session_state.search_query = match['title']
                    st.rerun()

        # Display recommendations for the top match
        st.divider()
        st.write(f"### Hidden Gems similar to **{top_match['title']}**:")
        recommendations = get_recommendations(top_match['id'])
        
        if recommendations is not None:
            st.table(recommendations[['title', 'vote_average', 'release_date']])
        else:
            st.info("We found the movie, but couldn't find any 'hidden gems' for it yet!")
            
    else:
        st.error(f"Sorry, I didn't find any movies matching '{user_input}'. Check your spelling and try again!")