import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def get_recommendations(movie_title):
    # 1. Search for the movie ID using the title
    search_url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(search_url).json()
    
    if not response.get('results'):
        return "Movie not found! Please check your spelling."
    
    movie_id = response['results'][0]['id']

    # 2. Get 'Similar' movies from the TMDB database
    recs_url = f"{BASE_URL}/movie/{movie_id}/similar?api_key={API_KEY}"
    recs_data = requests.get(recs_url).json().get('results', [])
    
    if not recs_data:
        return "No similar movies found."

    # 3. Create a DataFrame for our custom 'Gem' algorithm
    df = pd.DataFrame(recs_data)

    # --- CUSTOM ALGORITHM ---
    # We prioritize movies with high ratings but lower popularity (Hidden Gems)
    df['gem_score'] = (df['vote_average'] * 5) - (df['popularity'] * 0.1)
    
    # Sort and return the top 5
    recommendations = df.sort_values(by='gem_score', ascending=False).head(5)
    return recommendations[['title', 'vote_average', 'release_date']]

if __name__ == "__main__":
    print("--- Movie Gem Recommender ---")
    movie = input("Enter a movie you enjoyed: ")
    print(f"\nFinding gems similar to '{movie}'...\n")
    print(get_recommendations(movie))