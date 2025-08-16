import numpy as np
from pathlib import Path
import pandas as pd
import ast
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Define the folder where your data files are stored
data_folder = Path(r"C:\Users\singh\Downloads\Telegram Desktop\Movie Recomendation")

# Load CSV files using pathlib (no more unicodeescape errors)
movies = pd.read_csv(data_folder / "tmdb_5000_movies.csv")
credits = pd.read_csv(data_folder / "tmdb_5000_credits.csv")

# Merging movies and credits on the basis of title
movies = movies.merge(credits, on="title")

movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
movies.dropna(inplace=True)

# Function to convert JSON-like string to list of names
def convert(obj):
    return [i["name"] for i in ast.literal_eval(obj)]

# Function to get first 5 cast members
def convert5(obj):
    L = []
    for count, i in enumerate(ast.literal_eval(obj)):
        if count < 5:
            L.append(i["name"])
        else:
            break
    return L

# Function to get director's name from crew
def fetch_director(obj):
    for i in ast.literal_eval(obj):
        if i["job"] == "Director":
            return [i["name"]]
    return []

# Applying transformations
movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(convert5)
movies["crew"] = movies["crew"].apply(fetch_director)
movies["overview"] = movies["overview"].apply(lambda x: x.split())

# Remove spaces in multi-word names
for col in ["genres", "keywords", "cast", "crew"]:
    movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

# Create "tag" column
movies["tag"] = movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + movies["crew"]

# Keep only useful columns
new_df = movies[["movie_id", "title", "tag"]].copy()

# Convert tag list into a single lowercase string
new_df["tag"] = new_df["tag"].apply(lambda x: " ".join(x).lower())

# Stemming
ps = PorterStemmer()
def stem(text):
    return " ".join([ps.stem(i) for i in text.split()])

new_df["tag"] = new_df["tag"].apply(stem)

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(new_df["tag"]).toarray()

# Similarity matrix
similarity = cosine_similarity(vectors)

# Recommendation function
def recommend(movie):
    if movie not in new_df["title"].values:
        print(f"Movie '{movie}' not found in the dataset.")
        return
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[movie_index])), reverse=True, key=lambda x: x[1])
    for i in distances[1:6]:
        print(new_df.iloc[i[0]].title)

# Save pickle files
pickle.dump(new_df, open('movie_list.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))
