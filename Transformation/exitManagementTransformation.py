import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------
# Configuration (loaded from environment)
# -------------------------------
BASE_URL = os.getenv("BASE_URL")  # Update if your backend is running elsewhere
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# Endpoints to collect data from
ENDPOINTS = {
    "resignation_requests": "/resignation_requests",
    "exit_interviews": "/exit_interviews",
    "exit_checklists": "/exit_checklists",
    "exit_surveys": "/exit_surveys"
}

# -------------------------------
# Step 1: Authenticate and Get JWT Token
# -------------------------------
def get_token():
    token_url = f"{BASE_URL}/token"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"]

# -------------------------------
# Step 2: Retrieve Data from Endpoints
# -------------------------------
def get_data(endpoint: str, token: str):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# -------------------------------
# Step 3: Clean Data using Pandas
# -------------------------------
def clean_data(data: list) -> pd.DataFrame:
    # Create DataFrame from list of dicts
    df = pd.DataFrame(data)
    
    # Convert columns that are dates (if they exist)
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass  # skip if conversion fails
    # Drop columns not needed, e.g., if _id exists
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    # Fill missing values if necessary
    df = df.fillna('')
    return df

# -------------------------------
# Step 4: Save Clean Data to CSV Files (simulate ETL to data lake)
# -------------------------------
def save_to_csv(df: pd.DataFrame, name: str):
    filename = f"{name}_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved cleaned data to {filename}")

# -------------------------------
# Main ETL Process
# -------------------------------
def main():
    try:
        token = get_token()
        print("Obtained JWT token.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    for key, endpoint in ENDPOINTS.items():
        try:
            print(f"Fetching data from {endpoint}...")
            data = get_data(endpoint, token)
            print(f"Retrieved {len(data)} records from {key}.")
            
            # Clean the data
            df = clean_data(data)
            print(f"Cleaned data for {key}: {df.shape[0]} rows, {df.shape[1]} columns.")
            
            # Save cleaned data to CSV
            save_to_csv(df, key)
        except Exception as e:
            print(f"Error processing {key}: {e}")

if __name__ == "__main__":
    main()
