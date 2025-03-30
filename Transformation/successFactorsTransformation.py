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
BASE_URL = os.getenv("BASE_URL")  # Update if your backend is hosted elsewhere
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# Endpoints to fetch data from
# Note: Adjust the endpoints as needed (e.g., using valid EmployeeIDs)
ENDPOINTS = {
    "employees": "/employees",
    "employment_details": "/employment_details/1",  # Example: for EmployeeID 1
    "compensation": "/compensation/1",              # Example: for EmployeeID 1
    "performance": "/performance/1/2023"            # Example: for EmployeeID 1 and year 2023
}

# ---------------------------
# Step 1: Authenticate and Get JWT Token
# ---------------------------
def get_token():
    token_url = f"{BASE_URL}/token"
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(token_url, data=payload)
    response.raise_for_status()  # Raise an error if the status is not 200
    token_data = response.json()
    return token_data["access_token"]

# ---------------------------
# Step 2: Retrieve Data from Endpoints
# ---------------------------
def get_data(endpoint: str, token: str):
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
    Convert list of dictionaries to DataFrame,
    attempt to parse date/datetime columns,
    and remove any unwanted columns.
    """
    df = pd.DataFrame(data)
    
    # Attempt to convert columns with 'Date' or 'Time' to datetime if possible
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    
    # Optionally drop columns (e.g., internal IDs) if not needed
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    
    # Fill missing values
    df = df.fillna("")
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
        print(f"Authentication failed: {e}")
        return

    # For each endpoint, retrieve, clean, and save the data.
    for key, endpoint in ENDPOINTS.items():
        try:
            print(f"Fetching data from {endpoint}...")
            data = get_data(endpoint, token)
            print(f"Fetched {len(data)} records for {key}.")
            
            df = clean_data(data)
            print(f"Cleaned data for {key}: {df.shape[0]} rows and {df.shape[1]} columns.")
            
            save_to_csv(df, key)
        except Exception as e:
            print(f"Error processing {key}: {e}")

if __name__ == "__main__":
    main()
