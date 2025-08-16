import pickle
import streamlit as st
import requests

# TMDB API Key
API_KEY = "600702cd5a00af6d60467540689bad79"

# Function to fetch movie details
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Failed to fetch movie details: {e}")
        return {}

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_data = fetch_poster(movie_id)

        if not movie_data:
            continue

        # Fetching additional data like cast and crew
        try:
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
            credits_response = requests.get(credits_url, timeout=10)
            credits_response.raise_for_status()
            credits_data = credits_response.json()

            cast = ", ".join(actor['name'] for actor in credits_data.get('cast', [])[:5])
            cast = cast + " ..." if len(credits_data.get('cast', [])) > 5 else cast
            crew = ", ".join(c['name'] for c in credits_data.get('crew', []) if c.get('job') == "Director")
        except requests.exceptions.RequestException:
            cast, crew = "N/A", "N/A"

        movie_data['cast'] = cast
        movie_data['crew'] = crew
        recommended_movies.append(movie_data)
    
    return recommended_movies

# Header
st.markdown("""
<div style="text-align: center;">
    <h1 style="color: #ff6600; font-size: 3em; white-space: nowrap;">🎥 CineMate: Your Movie Matchmaker</h1>
    <p style="color: #555; font-size: 1.2em;">Discover movies tailored to your taste!</p>
</div>
""", unsafe_allow_html=True)

# Load data
movies = pickle.load(open('C:/Users/singh/Downloads/Telegram Desktop/Movie Recomendation/movie_list.pkl', 'rb'))
similarity = pickle.load(open('C:/Users/singh/Downloads/Telegram Desktop/Movie Recomendation/similarity.pkl', 'rb'))

# Background
bg_image_path = "file:///C:/Users/singh/Downloads/Telegram Desktop/Movie Recomendation/bg.jpg"
st.markdown(f"""
<style>
    body {{
        background-image: url('{bg_image_path}');
        background-size: cover;
        background-position: center;
        height: 100vh;
        margin: 0;
        padding: 0;
    }}
</style>
""", unsafe_allow_html=True)

# Styling
st.markdown("""
<style>
    .stButton > button {
        background-color: #ff6600;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #e65c00;
    }
    .movie-poster {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .movie-poster:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    hr {
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox("🔍 Type or select a movie from the dropdown", movie_list)

# Recommendations
if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        recommended_movies = recommend(selected_movie)

    cols = st.columns(2)
    for idx, movie_data in enumerate(recommended_movies):
        poster_path = movie_data.get('poster_path')
        if poster_path:
            poster_image = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            poster_image = "https://via.placeholder.com/500x750?text=No+Image"

        with cols[idx % 2]:
            st.markdown(f"""
            <img src="{poster_image}" class="movie-poster" style="width: 100%; height: auto;" />
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <h3 style="color: #333;">{movie_data.get('title', 'Unknown')}</h3>
            <p><strong>Release Date:</strong> {movie_data.get('release_date', 'N/A')}</p>
            <p><strong>Genres:</strong> {', '.join(genre['name'] for genre in movie_data.get('genres', []))}</p>
            <p><strong>Cast:</strong> {movie_data.get('cast', 'N/A')}</p>
            <p><strong>Director:</strong> {movie_data.get('crew', 'N/A')}</p>
            <p style="color: #555;">{movie_data.get('overview', 'No description available.')}</p>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; color: #888;">
</div>
""", unsafe_allow_html=True)
