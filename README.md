# 🎬 Movie Gem Recommender

A Python-based recommendation engine that identifies "Hidden Gems" using a custom-weighted algorithm and The Movie Database (TMDB) API.

## 🚀 The "Gem Score" Algorithm
Unlike standard recommenders that suggest the most popular blockbusters, this project uses a custom scoring logic to surface high-quality, lesser-known films. 

**The Formula:** `Gem Score = (Rating * 5) - (Popularity * 0.1)`

This logic ensures that movies with high critical acclaim (ratings) are prioritized, while mainstream "noise" (high popularity) is penalized slightly to reveal hidden gems.

## 🛠️ Features
- **Real-time Data:** Fetches live movie metadata using the TMDB API.
- **Custom Ranking:** Implements a proprietary scoring algorithm using `pandas`.
- **Interactive CLI:** Simple command-line interface for user input and results.
- **Environment Security:** Uses `python-dotenv` to manage API credentials securely.

## 📦 Tech Stack
- **Language:** Python 3.x
- **Libraries:** Pandas, Requests, Python-Dotenv
- **API:** [The Movie Database (TMDB)](https://www.themoviedb.org/)

## ⚙️ Setup & Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/MegannZNkenglack/movie-recommender.git](https://github.com/MegannZNkenglack/movie-recommender.git)