import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------
# Configuration (loaded from environment)
# ---------------------------
BASE_URL = os.getenv("BASE_URL")  # Update if your API is hosted elsewhere
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# Endpoints to retrieve data from.
# These keys correspond to the route names defined in your MySQL API.
ENDPOINTS = {
    "attendance": "/attendance",
    "leave": "/leave",
    "shift": "/shift",
    "overtime": "/overtime"
}

# ---------------------------
# Step 1: Authenticate and Get JWT Token
# ---------------------------
def get_token() -> str:
    token_url = f"{BASE_URL}/token"
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(token_url, data=payload)
    response.raise_for_status()  # Raise error for non-200 responses
    token_data = response.json()
    return token_data["access_token"]

# ---------------------------
# Step 2: Retrieve Data from Endpoints
# ---------------------------
def get_data(endpoint: str, token: str) -> list:
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# ---------------------------
# Step 3: Clean Data Using Pandas
# ---------------------------
def clean_data(data: list) -> pd.DataFrame:
    """
    Converts list of dictionaries to a DataFrame, 
    attempts to convert columns containing 'Date', 'Time', or 'At' to datetime,
    removes any MongoDB-specific _id fields (if present), and fills missing values.
    """
    df = pd.DataFrame(data)
    
    # Attempt to parse columns with "Date", "Time", or "At" in the name as datetime
    for col in df.columns:
        if any(x in col.lower() for x in ["date", "time", "at"]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass  # If conversion fails, leave the column as-is
    
    # Drop unwanted fields if present (e.g., MongoDB's _id)
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)
    
    # Fill missing values
    df.fillna("", inplace=True)
    return df

# ---------------------------
# Step 4: Save Cleaned Data to CSV
# ---------------------------
def save_to_csv(df: pd.DataFrame, name: str):
    filename = f"{name}_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved cleaned data to {filename}")

# ---------------------------
# Main ETL Process
# ---------------------------
def main():
    try:
        token = get_token()
        print("Obtained JWT token.")
    except Exception as e:
        print("Error during authentication:", e)
        return

    # Loop over each endpoint, fetch, clean, and save the data.
    for key, endpoint in ENDPOINTS.items():
        try:
            print(f"Fetching data from {endpoint}...")
            data = get_data(endpoint, token)
            print(f"Retrieved {len(data)} records for {key}.")
            
            df = clean_data(data)
            print(f"Cleaned data for {key}: {df.shape[0]} rows, {df.shape[1]} columns.")
            
            save_to_csv(df, key)
        except Exception as e:
            print(f"Error processing {key} data: {e}")

if __name__ == "__main__":
    main()
