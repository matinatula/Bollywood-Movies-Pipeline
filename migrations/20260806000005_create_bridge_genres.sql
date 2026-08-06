CREATE TABLE IF NOT EXISTS bridge_genres(
    movie_id INT,
    genre_id INT,
    PRIMARY KEY(movie_id, genre_id),
    CONSTRAINT fk_bridge_genres_movie_id 
        FOREIGN KEY (movie_id) REFERENCES dim_movies(movie_id) ON DELETE CASCADE,
    CONSTRAINT fk_bridge_genres_genre_id
        FOREIGN KEY (genre_id) REFERENCES dim_genres(genre_id) ON DELETE CASCADE
);

