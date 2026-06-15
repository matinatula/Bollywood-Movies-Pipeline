import requests
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()

api_key = os.getenv('API_KEY')

url = "https://api.themoviedb.org/3/discover/movie"

def fetch_from_api_to_json(language):
    temp_list = []
    count_results = 0
    file_name = f"raw_{language}_movies.json"
    for i in range(1,101):
        params={'api_key':api_key,'with_original_language':language,'page':i}

        response = requests.get(url,params=params)
        if response.status_code == 200:
            print(f"Fetching page {i}, Currently stored results = {count_results}")
            data= json.loads(response.text)         # convert JSON to python
            temp_list.append(data['results'])   
        else:
            print(f"\nError: {response.status_code}")
        time.sleep(0.3)
        count_results+=len(data['results'])

    json_str = json.dumps(temp_list, indent=4, ensure_ascii=False) # convert python object to JSON string

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(json_str)
    print(f"\nSaved {count_results} movies to {file_name}.\n")


fetch_from_api_to_json("en")
fetch_from_api_to_json("hi")
fetch_from_api_to_json("ko")


