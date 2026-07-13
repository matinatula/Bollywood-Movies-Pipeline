import json
import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

api_key = os.getenv('API_KEY')

def fetch_movie_details(language):
    results = []
    file_name = f"filtered/filtered_{language}_movies.json"
    os.makedirs("details", exist_ok=True)
    with open(file_name,"r") as f:
        movies = json.load(f)
    for movie in movies:
        budget_url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
        cast_url = f"https://api.themoviedb.org/3/movie/{movie['id']}/credits"

        params = {'api_key':api_key}

        try:
            budget_response = requests.get(budget_url,params=params,timeout=10)
            cast_response = requests.get(cast_url,params=params,timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Skipping movie {movie['id']}: {e}")
            continue

        if budget_response.status_code == 200 and cast_response.status_code ==200 :
            print(f"Fetching details for movie {movie['id']} : {movie['title']}")
            data_budget = json.loads(budget_response.text)
            data_credits = json.loads(cast_response.text)

            temp_dict = {
                'movie_id': data_budget['id'],
                'movie_title': data_budget['original_title'],
                'original_language': data_budget['original_language'],
                'release_date': data_budget['release_date'],
                'genres': [data_budget['genres'][i]['name'] for i in range(min(3,len(data_budget['genres'])))],
                'popularity': data_budget['popularity'],
                'revenue':data_budget['revenue'],
                'runtime': data_budget['runtime'],
                'vote_average':data_budget['vote_average'],
                'vote_count':data_budget['vote_count'],
                'budget': data_budget['budget'],
                'cast':[data_credits['cast'][i]['name'] for i in range(min(5,len(data_credits['cast'])))],
                
            }
            results.append(temp_dict)

        else:
            print(f"\nError occurred: {budget_response.status_code} / {cast_response.status_code}")
        time.sleep(0.3)

        
    with open(f"details/{language}_movie_details.json", "w") as f:
        json.dump(results, f)

fetch_movie_details("en")
fetch_movie_details("hi")
fetch_movie_details("ko")


     
        
