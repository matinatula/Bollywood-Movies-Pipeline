CREATE TABLE IF NOT EXISTS fact_movies(
    movie_id INTEGER PRIMARY KEY,
    release_date TIMESTAMP NOT NULL,
    popularity FLOAT NOT NULL,      
    revenue BIGINT, 
    runtime INT,
    vote_average FLOAT NOT NULL,                              
    vote_count INT NOT NULL,
    budget BIGINT,
    CONSTRAINT fk_fact_movies_movie_id
        FOREIGN KEY(movie_id) REFERENCES dim_movies(movie_id) ON DELETE CASCADE
);