import requests
import csv
from collections import Counter
import re
import time

# Define a function to clean author IDs for use as file names
def clean_author_id(author_id):
    return re.sub(r'\W+', '_', author_id)

# Define the list of author IDs from the author API
author_ids = []

# Define the API endpoint for author data
author_api_url = "https://api.openalex.org/authors"

# Define the query parameters for the author API
author_query_params = {
    "filter": "concepts.id:https://openalex.org/C2985322473",
    "per-page": 200,
    "page": 1
}

# Function to send HTTP requests with exponential backoff retries
def send_request_with_retries(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Check if the response is already in JSON format
            if 'application/json' in response.headers.get('content-type', '').lower():
                return response.json()
            else:
                return response.content  # Return the raw content if not JSON
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    return None

# Send multiple HTTP requests to retrieve author IDs in batches
for page in range(1, 16):  # Loop from page 1 to 15
    print(page)
    author_query_params["page"] = page
    author_response = send_request_with_retries(author_api_url, params=author_query_params)

    if author_response:
        author_data = author_response.get("results", [])

        # Extract author IDs and append them to the list
        for author_result in author_data:
            author_id = author_result.get("id")
            author_ids.append(author_id)

    else:
        print(f"Failed to retrieve author data for page {page}.")

# Define the API endpoint for works data
api_url = "https://api.openalex.org/works"

# Define the list of publication years
publication_years = list(range(1950, 2024))
print(len(author_ids))
c = 1
# Create a dictionary to store data for each author
author_data_dict = {}

# Loop through the author IDs
for author_id in author_ids:
    print(c)
    c = c+1
    x = author_id
    author_ids_by_year = {}
    author_display_names_by_year = {}
    author_counts_by_year = {}

    for year in publication_years:
        author_ids_by_year[year] = set()
        author_display_names_by_year[year] = set()  # Use a set to store unique display names
        author_counts_by_year[year] = Counter()

    # Construct the query parameter for the author ID
    query_params = {
        "filter": f"concepts.id:https://openalex.org/C2985322473,author.id:{author_id}",
        "per-page": 200,
        "page": 1
    }

    # Send the HTTP request for the author ID with retries
    response = send_request_with_retries(api_url, params=query_params)

    if response:
        data = response.json()
        works = data.get("results", [])

        for work in works:
            publication_year = work.get("publication_year")
            authors = work.get("authorships", [])

            for author in authors:
                author_id = author.get("author").get("id")
                author_name = author.get("author").get("display_name")

                if publication_year in publication_years:
                    author_ids_by_year[publication_year].add(author_id)
                    author_display_names_by_year[publication_year].add(author_name)
                    # Only increment co-author counts if the author is not the main author
                    if author_id != x:
                        author_counts_by_year[publication_year][author_id] += 1

        # Store author data in the dictionary
        author_data_dict[x] = {
            "author_ids_by_year": author_ids_by_year,
            "author_display_names_by_year": author_display_names_by_year,
            "author_counts_by_year": author_counts_by_year
        }

    else:
        print(f"Failed to retrieve data for author {author_id}. Status code: {response.status_code}")

# Fetch additional author information from the given link
additional_info_url = "https://api.openalex.org/authors?filter=concepts.id:https://openalex.org/C2985322473&per-page=200&page={page_num}"
additional_info_results = []

for page_num in range(1, 16):  # Loop from page 1 to 15
    page_url = additional_info_url.format(page_num=page_num)
    additional_info_response = send_request_with_retries(page_url)

    if additional_info_response:
        additional_info_data = additional_info_response.get("results", [])
        additional_info_results.extend(additional_info_data)
    else:
        print(f"Failed to retrieve additional author information from page {page_num}.")

# Create a dictionary to store additional author information
additional_info_dict = {}

for result in additional_info_results:
    author_id = result.get("id")
    display_name = result.get("display_name")
    h_index = result.get("summary_stats").get("h_index")
    x_index = result.get("summary_stats").get("i10_index")
    two_year_mean_citedness = result.get("summary_stats").get("2yr_mean_citedness")

    # Check if "last_known_institution" exists in the result
    last_known_institution = result.get("last_known_institution")
    
    if last_known_institution:
        institution_display_name = last_known_institution.get("display_name")
        country_code = last_known_institution.get("country_code")
    else:
        institution_display_name = ""
        country_code = ""

    additional_info_dict[author_id] = {
        "display_name": display_name,
        "h_index": h_index,
        "x_index": x_index,
        "two_year_mean_citedness": two_year_mean_citedness,
        "last_known_institution": institution_display_name,
        "country_code": country_code
    }

# Write data to a single CSV file
with open("co_authorship_data1.csv", mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([
        "Main Author ID",
        "Author Name",
        "H-Index",
        "I-Index",
        "Two-Year Mean Citedness",
        "Institution",
        "Country Code",
        "Publication Year",
        "Co-Author ID",
        "Co-Author Display Name",
        "Co-Author Counts"
    ])

    for author_id, author_data in author_data_dict.items():
        for year in publication_years:
            main_author_id = author_id  # Store the main author's ID
            author_ids = list(author_data["author_ids_by_year"][year])

            # Remove the main author's ID from the list of co-authors
            if main_author_id in author_ids:
                author_ids.remove(main_author_id)

            author_names = list(author_data["author_display_names_by_year"][year])
            author_counts = author_data["author_counts_by_year"][year]

            additional_info = additional_info_dict.get(main_author_id, {})
            display_name = additional_info.get("display_name", "")
            h_index = additional_info.get("h_index", "")
            x_index = additional_info.get("x_index", "")
            two_year_mean_citedness = additional_info.get("two_year_mean_citedness", "")
            last_known_institution = additional_info.get("last_known_institution", "")
            country_code = additional_info.get("country_code", "")

            # Loop through the co-authors for this main author and create a separate row for each
            for co_author_id, co_author_name in zip(author_ids, author_names):
                co_author_count = author_counts[co_author_id]
                writer.writerow([
                    main_author_id,
                    display_name,
                    h_index,
                    x_index,
                    two_year_mean_citedness,
                    last_known_institution,
                    country_code,
                    year,
                    co_author_id,
                    co_author_name,
                    co_author_count
                ])

print("CSV file 'co_authorship_data.csv' has been created.")
