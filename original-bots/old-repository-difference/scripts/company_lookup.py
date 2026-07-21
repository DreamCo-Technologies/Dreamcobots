import requests
import json
import sys

API_URL = "https://api.crunchbase.com/v3.1/organizations"
API_KEY = "YOUR_CRUNCHBASE_API_KEY"

def fetch_company_info(company_name):
    params = {"query": company_name, "user_key": API_KEY}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return {}

def save_company_data(company_name, data):
    with open("data/lookups.json", "r+") as file:
        try:
            existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = {}

        existing_data[company_name] = data

        file.seek(0)
        json.dump(existing_data, file, indent=4)
        file.truncate()

if __name__ == "__main__":
    company_name = sys.argv[1]
    print(f"Fetching data for: {company_name}")
    company_data = fetch_company_info(company_name)
    if company_data:
        save_company_data(company_name, company_data)
        print(f"Successfully saved data for {company_name}")
    else:
        print("No data found.")