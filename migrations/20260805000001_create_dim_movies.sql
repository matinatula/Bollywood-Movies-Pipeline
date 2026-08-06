CREATE TABLE IF NOT EXISTS dim_movies (
    movie_id INTEGER PRIMARY KEY,
    movie_title TEXT NOT NULL,
    original_language TEXT NOT NULL
);