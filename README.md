# 🎬 Movie Gem Recommender

A high-performance movie discovery engine built with **Python** and **Streamlit** that surfaces **high-quality “hidden gem” films** using a custom ranking algorithm and metadata from **The Movie Database (TMDB) API**.

Unlike typical recommenders that surface the most popular blockbusters, this engine prioritizes **quality, relevance, and intersection of user tastes**.

🔗 Live Demo: https://your-streamlit-link-here

---

# ⚙️ How It Works

This application implements a **content-based recommendation pipeline** that transforms a small set of user favorites into a curated recommendation feed.

The system processes **3–5 input movies**, analyzes overlapping metadata, and ranks results using a **custom weighted scoring algorithm**.

---

## 1️⃣ Data Aggregation & Taste Profiling

The recommendation pipeline begins by establishing a **baseline profile of the user’s cinematic preferences**.

### Steps

**User Input Processing**

- The system accepts **3–5 favorite movies** from the user.
- Multiple inputs allow the algorithm to capture **patterns in genres, themes, and storytelling styles**.

**Fuzzy Title Matching**

- A search layer identifies the correct movie even if the title is **slightly misspelled**.

**TMDB API Integration**

- Each movie title is resolved into a **unique TMDB ID**.
- The system retrieves metadata and **similar movie recommendations** from TMDB.

This produces a **candidate pool of potential recommendations**.

---

## 2️⃣ The "Gem Score" Ranking Algorithm

To prioritize **quality over mainstream popularity**, the engine uses a custom scoring formula.
$$Gem\ Score = (Rating \times 5) - (Popularity \times 0.1)$$

### Why this works

Most recommendation systems push **high-popularity movies**, which leads to the same blockbuster suggestions.

This algorithm intentionally:

- **Rewards high ratings**
- **Slightly penalizes extreme popularity**
- Surfaces **high-quality but lesser-known films**

### Intersection Weighting (Match Bonus)

If a movie appears in the recommendation lists of **multiple input films**, it receives a **Match Bonus**.

This indicates a **strong overlap in the user’s taste profile** and increases its ranking.

Example:

| Movie | Appears In | Priority |
|------|------------|----------|
| Film A | 3 input movies | 🔥 High |
| Film B | 1 input movie | Normal |

---

## 3️⃣ Real-Time Content Enrichment

After ranking the results, the system enriches each recommendation with **live metadata** from TMDB.

### Data Added to Each Recommendation

**Cast & Crew**

- Director
- Top 3 credited actors

**Parental Guidance**

- Extracts US certifications such as **PG-13 or R**

**Trailer Integration**

- Fetches the **YouTube trailer key** using TMDB's `/videos` endpoint.

This allows users to **immediately preview films directly within the app**.

---

## 4️⃣ Performance & Data Processing

Several techniques keep the application responsive and scalable.

### Streamlit Session State

- Maintains user inputs across interactions
- Prevents redundant API calls

### Pandas DataFrames

Used for efficient:

- Data filtering
- Deduplication
- Score calculation
- Ranking operations

### Vectorized Operations

Enable fast processing across **large recommendation datasets**.

---

# 🛠️ Features

- **Multi-Movie Taste Profiling** – Accepts 3–5 favorites to build a stronger recommendation profile  
- **Weighted Intersection Logic** – Movies recommended by multiple sources receive a **🔥 Top Match bonus**  
- **Custom Gem Score Algorithm** – Prioritizes high-quality hidden films  
- **Real-time Metadata Enrichment** – Displays director, cast, and parental ratings  
- **Multimedia Integration** – Automatically fetches YouTube trailers  
- **Cloud Deployment** – Interactive web interface hosted on Streamlit Cloud  

---

# 📦 Tech Stack

### Language
- Python 3.x

### Framework
- Streamlit (UI + State Management)

### Libraries
- Pandas – Data processing and ranking
- Requests – API communication
- Python-Dotenv – Environment variable security

### API
- The Movie Database (TMDB)

### DevOps
- Git / GitHub
- Streamlit Cloud Deployment
- Secret management using `.env`

---

# ⚙️ Setup & Installation

## ⚙️ Setup & Installation
## 1. Clone the repository:
   ```bash
   git clone [https://github.com/MegannZNkenglack/movie-recommender.git](https://github.com/MegannZNkenglack/movie-recommender.git)
   ```

## 2. Install Dependencies

   ```bash
   pip install -r requirements.txt
   ```
## 3. Configure Environment Variables

Create a `.env` file in the root directory and add your TMDB API key:

   ```bash
   TMDB_API_KEY=your_api_key_here
   ```

## 4. Run the Application

   ```bash
   streamlit run logic.py
   ```
## 🏅 About the Developer

I am a **Computer Science student** and **Varsity Wrestler**. I apply the same **discipline and persistence** required in athletics to solving complex technical problems and building scalable software systems.

This project demonstrates my ability to:

- 🧠 Design custom recommendation algorithms  
- 🔌 Integrate external APIs  
- ⚙️ Build data processing pipelines  
- 💻 Develop interactive web applications  
- ☁️ Deploy cloud-hosted software  
- 📦 Manage the full development lifecycle
