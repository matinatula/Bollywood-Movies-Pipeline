import requests
import json
from dotenv import load_dotenv
import os
import time
from logger_config import get_logger

logger=get_logger(__name__)
load_dotenv()

api_key = os.getenv('API_KEY')

url = "https://api.themoviedb.org/3/discover/movie"

def fetch_from_api_to_json(language):
    os.makedirs("data/bronze", exist_ok=True)
    temp_list = []
    count_results = 0
    file_name = f"data/bronze/raw_{language}_movies.json"
    for i in range(1,101):
        params={'api_key':api_key,'with_original_language':language,'page':i}
        try:
            response = requests.get(url,params=params, timeout=10)
            response.raise_for_status()
            data= json.loads(response.text)         # convert JSON to python
            temp_list.append(data['results'])   
            count_results += len(data['results'])
            logger.info(f"Fetched page {i}, total : {count_results}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"\nPage {i} request failed: {e}")
        time.sleep(0.3)

    json_str = json.dumps(temp_list, indent=4, ensure_ascii=False) # convert python object to JSON string

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(json_str)
    logger.info(f"\nSaved {count_results} movies to {file_name}.\n")


fetch_from_api_to_json("en")
fetch_from_api_to_json("hi")
fetch_from_api_to_json("ko")


