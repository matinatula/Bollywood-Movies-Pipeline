CREATE TABLE IF NOT EXISTS bridge_cast(
    movie_id INT,
    cast_id INT,
    cast_order INT,
    PRIMARY KEY (movie_id, cast_id),
    CONSTRAINT fk_bridge_cast_movie_id
        FOREIGN KEY(movie_id) REFERENCES dim_movies(movie_id) ON DELETE CASCADE,
    CONSTRAINT fk_bridge_cast_cast_id
        FOREIGN KEY(cast_id) REFERENCES dim_cast(cast_id) ON DELETE CASCADE
);