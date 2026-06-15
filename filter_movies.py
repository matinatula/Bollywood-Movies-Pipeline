import json
import pandas as pd
import itertools

languages = ["en", "hi", "ko"]


def fetch_details_from_json():
    for lang in languages:
        file_name_1 = f"raw_{lang}_movies.json"
        file_name_2 = f"filtered_{lang}_movies.json"
        try:
            with open(file_name_1, "r", encoding="utf-8") as file:
                list_of_lists_of_movies = json.load(file)

            flattened_list = list(itertools.chain.from_iterable(list_of_lists_of_movies))

            df = pd.DataFrame(flattened_list)
            New_df = df.loc[(df['release_date'] >= "2016-01-01")
                            & (df['release_date'] <= "2026-12-12")]
            
            json_str = json.dumps(flattened_list, indent=4, ensure_ascii=False)
            
            with open(file_name_2,"w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"\nSaved {len(New_df)} movies to {file_name_2}.\n")

        except FileNotFoundError:
            print(f"Error: The file raw_{lang}_movies.json was not found.")

fetch_details_from_json()

