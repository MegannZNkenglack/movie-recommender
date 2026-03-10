import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote
from dotenv import load_dotenv

# 1. SETUP & KEYS
load_dotenv()
API_KEY = st.secrets["TMDB_API_KEY"] if "TMDB_API_KEY" in st.secrets else os.getenv("TMDB_API_KEY")

# --- 2. SESSION STATE HELPERS ---
# Initialize keys if they don't exist yet to prevent the "StreamlitAPIException"
for i in range(1, 6):
    if f"m{i}" not in st.session_state:
        st.session_state[f"m{i}"] = ""

def reset_form():
    """Clears all movie input fields in the session state."""
    # This now works because the keys were initialized above
    st.session_state["m1"] = ""
    st.session_state["m2"] = ""
    st.session_state["m3"] = ""
    st.session_state["m4"] = ""
    st.session_state["m5"] = ""

# 3. DATA FETCHING FUNCTIONS
def get_max_popularity():
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    return res[0]['popularity'] if res else 1000

def get_movie_details(movie_id):
    cred_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    credits = requests.get(cred_url).json()
    rel_url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={API_KEY}"
    releases = requests.get(rel_url).json().get('results', [])
    
    rating = "N/A"
    for r in releases:
        if r['iso_3166_1'] == "US":
            rating = r['release_dates'][0].get('certification', 'N/A')
            break

    director = next((m['name'] for m in credits.get('crew', []) if m['job'] == 'Director'), "Unknown")
    stars = [m['name'] for m in credits.get('cast', [])][:3]
    return {"director": director, "stars": ", ".join(stars), "rating": rating}

def get_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    if not res: return pd.DataFrame()
    df = pd.DataFrame(res)
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    return df

def get_movie_trailer(movie_id):
    """Fetches the YouTube trailer link for a movie."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    res = requests.get(url).json().get('results', [])
    for video in res:
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

# 4. STREAMLIT UI SETUP
st.set_page_config(page_title="Movie Gem Recommender", layout="wide")
st.title("🎬 Movie Gem Recommender")
st.markdown("### Step 1: Tell us your favorites")
st.caption("Enter 3 to 5 movies to get a more accurate feel for your taste.")

max_pop = get_max_popularity()

# 5. THE INPUT FORM (Consolidated)
with st.form("movie_form"):
    col1, col2 = st.columns(2)
    with col1:
        # We MUST use 'key' here so the reset function can find them
        m1 = st.text_input("Movie 1", placeholder="e.g. Inception", key="m1")
        m2 = st.text_input("Movie 2", placeholder="e.g. The Dark Knight", key="m2")
        m3 = st.text_input("Movie 3", placeholder="e.g. Interstellar", key="m3")
    with col2:
        m4 = st.text_input("Movie 4 (Optional)", key="m4")
        m5 = st.text_input("Movie 5 (Optional)", key="m5")
    
    submit_button = st.form_submit_button("✨ Generate Recommendations")

# Reset button placed neatly below the form
if st.button("🗑️ Clear All Inputs"):
    reset_form()
    st.rerun()

# 6. PROCESSING LOGIC
if submit_button:
    user_list = [m for m in [m1, m2, m3, m4, m5] if m.strip()]
    
    if len(user_list) < 3:
        st.warning("Please enter at least 3 movies for a better 'feel' of your taste!")
    else:
        all_recs_list = []
        with st.status("Analyzing your taste...", expanded=True) as status:
            for movie_name in user_list:
                st.write(f"Searching for {movie_name}...")
                search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(movie_name)}"
                search_results = requests.get(search_url).json().get('results', [])
                if search_results:
                    recs = get_recommendations(search_results[0]['id'])
                    if not recs.empty:
                        all_recs_list.append(recs)
            status.update(label="Analysis complete!", state="complete", expanded=False)

        if all_recs_list:
            combined_df = pd.concat(all_recs_list).drop_duplicates(subset='id')
            combined_df = combined_df.sort_values(by='popularity', ascending=False)

            st.divider()
            st.write(f"### ✨ Your Custom Movie Feed")
            
            for _, movie in combined_df.head(15).iterrows():
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
                        st.write(f"**Popularity:** {pop_percent}%")
                        st.progress(pop_percent / 100)
                        st.write(f"**Director:** {details['director']} | **Stars:** {details['stars']}")
                        st.write(f"**Summary:** {movie['overview']}")
        else:
            st.error("Could not find any recommendations. Try different titles!")

# Inside your loop, right under st.write(f"**Summary:** {movie['overview']}")
trailer_url = get_movie_trailer(movie['id'])
if trailer_url:
    st.link_button("🎥 Watch Trailer", trailer_url)