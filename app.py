"""
CineMitra - Movies. Magic. Memories.
Complete Flask Web Application for Indian Movie Recommendations and Ticket Booking.
"""

import os
import re
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Optional pandas and scikit-learn import with graceful fallback
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cinemitra_super_secret_key_2025")

# Path to dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'indian movies.csv')

# Poster mapping for popular Indian movies to high quality public movie poster images
POSTER_MAP = {
    "3 idiots": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80",
    "dangal": "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=500&auto=format&fit=crop&q=80",
    "rrr": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop&q=80",
    "k.g.f: chapter 2": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=500&auto=format&fit=crop&q=80",
    "baahubali 2: the conclusion": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
    "sairat": "https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=500&auto=format&fit=crop&q=80",
    "kantara": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
    "vikram": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=500&auto=format&fit=crop&q=80",
    "drishyam": "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=500&auto=format&fit=crop&q=80",
    "tumbbad": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
    "stree": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=500&auto=format&fit=crop&q=80",
    "stree 2": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=500&auto=format&fit=crop&q=80",
    "jawan": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500&auto=format&fit=crop&q=80",
    "sholay": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=500&auto=format&fit=crop&q=80",
    "dilwale dulhania le jayenge": "https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=500&auto=format&fit=crop&q=80",
    "lagaan: once upon a time in india": "https://images.unsplash.com/photo-1512719357-ac8a939f50e8?w=500&auto=format&fit=crop&q=80",
    "taare zameen par": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&auto=format&fit=crop&q=80",
    "swades": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=500&auto=format&fit=crop&q=80",
    "andhadhun": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
    "queen": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500&auto=format&fit=crop&q=80",
    "hera pheri": "https://images.unsplash.com/photo-1514306191717-452ec28c7814?w=500&auto=format&fit=crop&q=80",
    "chhichhore": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=500&auto=format&fit=crop&q=80",
    "zindagi na milegi dobara": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=500&auto=format&fit=crop&q=80",
    "kalki 2898 ad": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
    "pushpa: the rise": "https://images.unsplash.com/photo-1533488765986-dfa2a9939acd?w=500&auto=format&fit=crop&q=80",
    "jailer": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=500&auto=format&fit=crop&q=80",
    "manjummel boys": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500&auto=format&fit=crop&q=80",
    "premalu": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
    "aavesham": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500&auto=format&fit=crop&q=80",
    "natsamrat": "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=500&auto=format&fit=crop&q=80",
    "12th fail": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500&auto=format&fit=crop&q=80",
    "laapataa ladies": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=80"
}

# Theaters mapping per city
THEATERS_BY_CITY = {
    "Pune": [
        {"id": "pune-1", "name": "PVR ICON: The Pavilion Mall", "area": "SB Road, Pune", "screens": 6, "experience": "4DX, IMAX, Gold Class"},
        {"id": "pune-2", "name": "Cinepolis: Seasons Mall", "area": "Magarpatta, Pune", "screens": 15, "experience": "VIP, Dolby Atmos"},
        {"id": "pune-3", "name": "City Pride Multiplex", "area": "Kothrud, Pune", "screens": 5, "experience": "Dolby 7.1, Recliner"},
        {"id": "pune-4", "name": "INOX: Phoenix Marketcity", "area": "Viman Nagar, Pune", "screens": 8, "experience": "Insignia, Laser 4K"}
    ],
    "Mumbai": [
        {"id": "mum-1", "name": "PVR ICON: Phoenix Palladium", "area": "Lower Parel, Mumbai", "screens": 7, "experience": "Director's Cut, IMAX"},
        {"id": "mum-2", "name": "INOX: Megaplex", "area": "Inorbit Mall, Malad, Mumbai", "screens": 11, "experience": "ScreenX, MX4D, Dolby Atmos"},
        {"id": "mum-3", "name": "PVR: Dynamix Mall", "area": "Juhu, Mumbai", "screens": 5, "experience": "PXL, Dolby Atmos"},
        {"id": "mum-4", "name": "Cinepolis: Viviana Mall", "area": "Thane, Mumbai", "screens": 14, "experience": "VIP 4DX"}
    ],
    "Nashik": [
        {"id": "nsk-1", "name": "Cinemax: City Centre Mall", "area": "Untwadi Road, Nashik", "screens": 5, "experience": "Dolby 7.1"},
        {"id": "nsk-2", "name": "PVR: The Zone Mall", "area": "College Road, Nashik", "screens": 4, "experience": "Laser Projection"},
        {"id": "nsk-3", "name": "Inox: City Star", "area": "Mumbai-Agra Highway, Nashik", "screens": 3, "experience": "Dolby Digital"}
    ],
    "Nagpur": [
        {"id": "ngp-1", "name": "Cinepolis: VR Nagpur Mall", "area": "Medical Square, Nagpur", "screens": 6, "experience": "Dolby Atmos"},
        {"id": "ngp-2", "name": "PVR: Empress Mall", "area": "Gandhi Sagar Lake, Nagpur", "screens": 5, "experience": "4K Digital"},
        {"id": "ngp-3", "name": "Inox: Jaswant Tuli Mall", "area": "Indora Chowk, Nagpur", "screens": 4, "experience": "Dolby Surround"}
    ],
    "Delhi": [
        {"id": "del-1", "name": "PVR Plaza: Connaught Place", "area": "CP, Central Delhi", "screens": 3, "experience": "Heritage IMAX, Gold"},
        {"id": "del-2", "name": "PVR Director's Cut: Ambience Mall", "area": "Vasant Kunj, Delhi", "screens": 4, "experience": "Ultra Luxury Dining"},
        {"id": "del-3", "name": "Cinepolis: DLF Avenue", "area": "Saket, Delhi", "screens": 6, "experience": "Dolby Atmos, Real 3D"}
    ],
    "Bengaluru": [
        {"id": "blr-1", "name": "PVR Superplex: Vega City Mall", "area": "Bannerghatta Rd, Bengaluru", "screens": 12, "experience": "IMAX, 4DX, Playhouse"},
        {"id": "blr-2", "name": "Inox: Nexus Mall (Forum)", "area": "Koramangala, Bengaluru", "screens": 9, "experience": "Dolby Atmos"},
        {"id": "blr-3", "name": "Cinepolis: Orion East Mall", "area": "Banaswadi, Bengaluru", "screens": 5, "experience": "VIP, Laser"}
    ],
    "Hyderabad": [
        {"id": "hyd-1", "name": "Prasad's Multiplex", "area": "Necklace Road, Hyderabad", "screens": 6, "experience": "Giant Screen, 4K Laser"},
        {"id": "hyd-2", "name": "PVR: Inorbit Mall", "area": "Cyberabad, Hitec City, Hyderabad", "screens": 7, "experience": "Gold Class, Dolby Atmos"},
        {"id": "hyd-3", "name": "AMB Cinemas", "area": "Gachibowli, Hyderabad", "screens": 7, "experience": "Super Luxury, M-Lounge"}
    ],
    "Chennai": [
        {"id": "chn-1", "name": "SPI: Sathyam Cinemas", "area": "Royapettah, Chennai", "screens": 6, "experience": "RGB 4K Laser, Dolby Atmos"},
        {"id": "chn-2", "name": "PVR: VR Chennai", "area": "Anna Nagar, Chennai", "screens": 10, "experience": "P[XL], IMAX 2D"},
        {"id": "chn-3", "name": "AGS Cinemas", "area": "T. Nagar, Chennai", "screens": 4, "experience": "Dolby 7.1, 4K"}
    ],
    "Kolkata": [
        {"id": "kol-1", "name": "Inox: South City Mall", "area": "Prince Anwar Shah Rd, Kolkata", "screens": 6, "experience": "IMAX, Insignia"},
        {"id": "kol-2", "name": "PVR: Mani Square Mall", "area": "EM Bypass, Kolkata", "screens": 5, "experience": "Gold Class, Dolby Atmos"},
        {"id": "kol-3", "name": "Cinepolis: Acropolis Mall", "area": "Kasba, Kolkata", "screens": 4, "experience": "VIP Recliners"}
    ]
}

# Mood to genres mapping
MOOD_GENRE_MAP = {
    "Happy": ["Comedy", "Family", "Drama", "Musical", "Adventure"],
    "Funny": ["Comedy"],
    "Romantic": ["Romance", "Drama"],
    "Emotional": ["Drama", "Family", "Biography"],
    "Scared": ["Horror", "Thriller", "Mystery"],
    "Excited": ["Action", "Adventure", "Sci-Fi", "Crime"],
    "Thoughtful": ["Drama", "Mystery", "Biography", "Crime"],
    "Relaxed": ["Family", "Comedy", "Musical"],
    "Motivated": ["Drama", "Inspirational", "Sport", "Biography", "Action"],
    "Suspenseful": ["Thriller", "Mystery", "Crime"]
}


def load_movies_dataset():
    """
    Loads movie dataset from CSV file using pandas,
    with rigorous type parsing and error handling.
    """
    if not os.path.exists(DATA_PATH):
        print(f"Warning: CSV file not found at {DATA_PATH}")
        return []

    try:
        if PANDAS_AVAILABLE:
            df = pd.read_csv(DATA_PATH)
            # Normalize whitespace and ensure expected columns exist
            df.columns = [c.strip() for c in df.columns]
            
            # Fill missing values
            df['Movie Name'] = df['Movie Name'].fillna('Unknown Title')
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(2022).astype(int)
            df['Timing(min)'] = pd.to_numeric(df['Timing(min)'], errors='coerce').fillna(140).astype(int)
            df['Rating(10)'] = pd.to_numeric(df['Rating(10)'], errors='coerce').fillna(7.0).astype(float)
            df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce').fillna(1000).astype(int)
            df['Genre'] = df['Genre'].fillna('Drama').astype(str)
            df['Language'] = df['Language'].fillna('Hindi').astype(str)
            
            movies = df.to_dict('records')
        else:
            # Fallback standard csv reader
            import csv
            movies = []
            with open(DATA_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    movies.append({
                        'ID': int(row.get('ID', len(movies) + 1)),
                        'Movie Name': row.get('Movie Name', '').strip(),
                        'Year': int(row.get('Year', 2022) or 2022),
                        'Timing(min)': int(row.get('Timing(min)', 140) or 140),
                        'Rating(10)': float(row.get('Rating(10)', 7.0) or 7.0),
                        'Votes': int(row.get('Votes', 1000) or 1000),
                        'Genre': row.get('Genre', 'Drama').strip(),
                        'Language': row.get('Language', 'Hindi').strip()
                    })

        # Enrich movies with poster fallback
        for m in movies:
            name_lower = m['Movie Name'].lower().strip()
            # Match directly or sub-string
            m['Poster'] = POSTER_MAP.get(name_lower, "")
            if not m['Poster']:
                for k, v in POSTER_MAP.items():
                    if k in name_lower or name_lower in k:
                        m['Poster'] = v
                        break
            if not m['Poster']:
                # Clean cinema placeholder based on language and genre
                m['Poster'] = f"https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80"

        return movies
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []


# Global cache of movies
MOVIES_CACHE = load_movies_dataset()


def get_cached_movies():
    global MOVIES_CACHE
    if not MOVIES_CACHE:
        MOVIES_CACHE = load_movies_dataset()
    return MOVIES_CACHE


# -------------------------------------------------------------
# Web Page Routes
# -------------------------------------------------------------

@app.route('/')
@app.route('/index.html')
def index():
    """Renders the CineMitra Home Page."""
    return render_template('index.html')


@app.route('/signin.html')
@app.route('/signin')
def signin():
    """Renders the Sign In / Sign Up Page."""
    return render_template('signin.html')


@app.route('/location.html')
@app.route('/location')
def location():
    """Renders City / Location Selection Page."""
    return render_template('location.html')


@app.route('/theaters.html')
@app.route('/theaters')
def theaters():
    """Renders Available Theaters Page."""
    return render_template('theaters.html')


@app.route('/movies.html')
@app.route('/movies')
def movies_page():
    """Renders Movies Listing Page."""
    return render_template('movies.html')


@app.route('/shows.html')
@app.route('/shows')
def shows():
    """Renders Show Timing Selection Page."""
    return render_template('shows.html')


@app.route('/seats.html')
@app.route('/seats')
def seats():
    """Renders Interactive Seat Booking Page."""
    return render_template('seats.html')


@app.route('/recommend.html')
@app.route('/recommend')
def recommend():
    """Renders AI Movie Recommendation Page."""
    return render_template('recommend.html')


@app.route('/mood.html')
@app.route('/mood')
def mood():
    """Renders Mood-based Recommendation Page."""
    return render_template('mood.html')


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.route('/api/movies', methods=['GET'])
def api_movies():
    """
    Returns list of movies from CSV, optionally filtered by
    search query, language, genre, or sorted by rating.
    """
    movies = get_cached_movies()
    if not movies:
        return jsonify({"success": False, "message": "No movie data available in dataset", "movies": []}), 200

    search_query = request.args.get('search', '').strip().lower()
    language = request.args.get('language', '').strip()
    genre = request.args.get('genre', '').strip()
    limit = request.args.get('limit', type=int)

    filtered = movies

    if search_query:
        filtered = [
            m for m in filtered
            if search_query in m['Movie Name'].lower()
            or search_query in m['Genre'].lower()
            or search_query in m['Language'].lower()
        ]

    if language and language.lower() != 'all':
        filtered = [m for m in filtered if m['Language'].lower() == language.lower()]

    if genre and genre.lower() != 'all':
        filtered = [m for m in filtered if genre.lower() in m['Genre'].lower()]

    if limit:
        filtered = filtered[:limit]

    return jsonify({
        "success": True,
        "count": len(filtered),
        "movies": filtered
    })


@app.route('/api/search', methods=['GET'])
def api_search():
    """
    Search endpoint across movie name, genre, and language.
    """
    query = request.args.get('q', '').strip().lower()
    movies = get_cached_movies()

    if not query:
        return jsonify({"success": True, "count": len(movies), "movies": movies[:20]})

    results = []
    for m in movies:
        name_match = query in m['Movie Name'].lower()
        genre_match = query in m['Genre'].lower()
        lang_match = query in m['Language'].lower()

        if name_match or genre_match or lang_match:
            score = 0
            if name_match:
                score += 10
            if genre_match:
                score += 5
            if lang_match:
                score += 3
            results.append((score, m))

    results.sort(key=lambda x: (x[0], x[1]['Rating(10)']), reverse=True)
    matched_movies = [item[1] for item in results]

    return jsonify({
        "success": True,
        "query": query,
        "count": len(matched_movies),
        "movies": matched_movies
    })


@app.route('/api/theaters', methods=['GET'])
def api_theaters():
    """
    Returns available cinema halls for the requested city.
    """
    city = request.args.get('city', 'Pune').strip()
    all_movies = get_cached_movies()

    theaters = THEATERS_BY_CITY.get(city)
    if not theaters:
        # Default or fallback to Pune
        city = "Pune"
        theaters = THEATERS_BY_CITY.get(city, [])

    # Attach available movie sample and show timings to each theater
    enriched_theaters = []
    default_timings = ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM", "10:00 PM"]
    
    for i, t in enumerate(theaters):
        # Pick 4-6 representative movies for this theater
        sample_movies = all_movies[i * 3: i * 3 + 6] if len(all_movies) >= 10 else all_movies
        enriched_theaters.append({
            "id": t["id"],
            "name": t["name"],
            "city": city,
            "area": t["area"],
            "screens": t["screens"],
            "experience": t["experience"],
            "timings": default_timings,
            "movieCount": len(sample_movies),
            "availableMovies": [{"id": m["ID"], "name": m["Movie Name"], "rating": m["Rating(10)"]} for m in sample_movies]
        })

    return jsonify({
        "success": True,
        "city": city,
        "theaters": enriched_theaters
    })


@app.route('/api/recommend', methods=['POST', 'GET'])
def api_recommend():
    """
    Content-based recommendation engine using TF-IDF & Cosine Similarity
    augmented by rating, language match, and genre overlap.
    """
    movies = get_cached_movies()
    if not movies:
        return jsonify({"success": False, "message": "Movie dataset is empty", "recommendations": []})

    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()

    pref_lang = data.get('language', 'All').strip()
    pref_genre = data.get('genre', 'All').strip()
    min_rating = float(data.get('min_rating', 6.0) or 6.0)
    year_pref = data.get('year_preference', 'All').strip()
    mood = data.get('mood', '').strip()

    # Pre-filter by minimum rating
    candidates = [m for m in movies if m['Rating(10)'] >= min_rating]
    if not candidates:
        candidates = movies

    # Prepare features for TF-IDF / Content-based matching
    # Feature text: Language + Genre repeated + Year bucket + Rating strength
    feature_texts = []
    for m in candidates:
        text = f"{m['Language']} {m['Genre']} {m['Genre']} {m['Year']} rating_{int(m['Rating(10)'])}"
        feature_texts.append(text)

    # Build query text
    query_parts = []
    if pref_lang and pref_lang.lower() != 'all':
        query_parts.extend([pref_lang] * 2)
    if pref_genre and pref_genre.lower() != 'all':
        query_parts.extend([pref_genre] * 3)
    if mood and mood in MOOD_GENRE_MAP:
        query_parts.extend(MOOD_GENRE_MAP[mood])

    query_str = " ".join(query_parts) if query_parts else "Hindi Action Drama Comedy 8"

    recommendations = []

    if SKLEARN_AVAILABLE and len(feature_texts) > 1:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(feature_texts)
            query_vec = vectorizer.transform([query_str])
            cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()

            # Rank candidates
            scored = []
            for idx, score in enumerate(cosine_sim):
                m = candidates[idx]
                total_score = score

                # Boost if language matches
                if pref_lang.lower() != 'all' and m['Language'].lower() == pref_lang.lower():
                    total_score += 0.35

                # Boost if genre matches
                if pref_genre.lower() != 'all' and pref_genre.lower() in m['Genre'].lower():
                    total_score += 0.45

                # Year preference check
                if year_pref == 'classic' and m['Year'] < 2010:
                    total_score += 0.2
                elif year_pref == 'recent' and m['Year'] >= 2020:
                    total_score += 0.2

                # Rating weight
                total_score += (m['Rating(10)'] / 10.0) * 0.25

                # Generate beginner-friendly, descriptive reason
                reasons = []
                if pref_lang.lower() != 'all' and m['Language'].lower() == pref_lang.lower():
                    reasons.append(f"authentic {m['Language']} cinema")
                if pref_genre.lower() != 'all' and pref_genre.lower() in m['Genre'].lower():
                    reasons.append(f"delivers top-tier {pref_genre}")
                if m['Rating(10)'] >= 8.0:
                    reasons.append(f"acclaimed {m['Rating(10)']}/10 rating")
                if not reasons:
                    reasons.append(f"popular {m['Genre']} release in {m['Language']}")

                reason_text = f"Recommended because it features {' and '.join(reasons)}."

                scored.append((total_score, m, reason_text))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_matches = scored[:12]
            for s, m, r in top_matches:
                rec_item = dict(m)
                rec_item['reason'] = r
                rec_item['match_score'] = round(float(s) * 100, 1)
                recommendations.append(rec_item)

        except Exception as e:
            print(f"Scikit-learn recommendation fallback: {e}")

    # Fallback if sklearn is not available or produced no results
    if not recommendations:
        for m in candidates:
            score = 0
            reasons = []
            if pref_lang.lower() != 'all' and m['Language'].lower() == pref_lang.lower():
                score += 5
                reasons.append(f"{m['Language']} language")
            if pref_genre.lower() != 'all' and pref_genre.lower() in m['Genre'].lower():
                score += 6
                reasons.append(f"{pref_genre} genre")
            if m['Rating(10)'] >= 8.0:
                score += 4
                reasons.append(f"outstanding {m['Rating(10)']}/10 rating")

            score += (m['Rating(10)'] / 2.0)
            reason_str = "Recommended for " + (" and ".join(reasons) if reasons else f"{m['Genre']} storytelling")
            rec_item = dict(m)
            rec_item['reason'] = reason_str
            rec_item['match_score'] = round(min(score * 8.5, 99.0), 1)
            recommendations.append(rec_item)

        recommendations.sort(key=lambda x: (x['match_score'], x['Rating(10)']), reverse=True)
        recommendations = recommendations[:12]

    return jsonify({
        "success": True,
        "count": len(recommendations),
        "criteria": {
            "language": pref_lang,
            "genre": pref_genre,
            "min_rating": min_rating,
            "year_preference": year_pref,
            "mood": mood
        },
        "recommendations": recommendations
    })


@app.route('/api/mood', methods=['GET'])
def api_mood():
    """
    Recommends movies by mapping the user's selected emotional mood
    to genres and ranking the best matching titles from the CSV dataset.
    """
    mood_name = request.args.get('mood', 'Happy').strip()
    movies = get_cached_movies()

    if not movies:
        return jsonify({"success": False, "message": "No movies available in dataset", "movies": []})

    target_genres = MOOD_GENRE_MAP.get(mood_name, ["Comedy", "Drama", "Family"])

    matched = []
    for m in movies:
        movie_genres = [g.strip().lower() for g in m['Genre'].split(',')]
        match_count = sum(1 for tg in target_genres if tg.lower() in movie_genres)

        if match_count > 0:
            # Score based on number of genre overlaps + rating
            score = (match_count * 3.0) + (m['Rating(10)'] * 1.2)
            matched.append((score, m, match_count))

    matched.sort(key=lambda x: (x[0], x[1]['Rating(10)']), reverse=True)
    top_mood_movies = []

    for score, m, match_count in matched[:12]:
        item = dict(m)
        item['mood'] = mood_name
        item['reason'] = f"Matches your '{mood_name}' vibe with {item['Genre']} storytelling and {item['Rating(10)']}/10 rating."
        top_mood_movies.append(item)

    return jsonify({
        "success": True,
        "mood": mood_name,
        "mapped_genres": target_genres,
        "count": len(top_mood_movies),
        "movies": top_mood_movies
    })


@app.route('/api/booking', methods=['POST'])
def api_booking():
    """
    Saves and confirms a user's movie ticket booking.
    """
    data = request.get_json() or {}
    movie = data.get('movie', 'Selected Movie')
    theater = data.get('theater', 'CineMitra Partner Theater')
    city = data.get('city', 'Pune')
    show_date = data.get('date', 'Today')
    show_time = data.get('time', '7:00 PM')
    seats = data.get('seats', [])
    total_price = data.get('totalPrice', 0)
    user_email = data.get('userEmail', 'guest@cinemitra.in')

    if not seats:
        return jsonify({"success": False, "message": "Please select at least one seat to proceed."}), 400

    booking_id = f"CM-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    booking_record = {
        "bookingId": booking_id,
        "movie": movie,
        "theater": theater,
        "city": city,
        "date": show_date,
        "time": show_time,
        "seats": seats,
        "seatCount": len(seats),
        "totalPrice": total_price,
        "userEmail": user_email,
        "bookingTime": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "status": "CONFIRMED"
    }

    return jsonify({
        "success": True,
        "message": "Tickets booked successfully! Enjoy your CineMitra cinema experience.",
        "booking": booking_record
    })


if __name__ == '__main__':
    port = int(os.environ.get("FLASK_PORT", os.environ.get("PORT", 5000)))
    print(f"Starting CineMitra Flask Server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
