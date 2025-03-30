import os
import requests
import pandas as pd
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------
# Configuration (loaded from env)
# ---------------------------
BASE_URL = os.getenv("BASE_URL")  # Backend API URL
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

DREMIO_HOST = os.getenv("DREMIO_HOST")
DREMIO_PORT = os.getenv("DREMIO_PORT")
DREMIO_USER = os.getenv("DREMIO_USER")
DREMIO_PASSWORD = os.getenv("DREMIO_PASSWORD")
DREMIO_DATABASE = os.getenv("DREMIO_DATABASE")
DREMIO_WORKSPACE = os.getenv("DREMIO_WORKSPACE")  # Dremio workspace name

# ODBC connection string for Dremio
DREMIO_CONN_STR = f"DRIVER=Dremio Connector;HOST={DREMIO_HOST};PORT={DREMIO_PORT};AuthenticationType=Plain;UID={DREMIO_USER};PWD={DREMIO_PASSWORD}"

# Endpoints to fetch data from
ENDPOINTS = {
    "courses": "/courses",
    "modules": "/modules",
    "enrollments": "/enrollments",
    "assessments": "/assessments",
    "certificates": "/certificates"
}

# ---------------------------
# Step 1: Authenticate to Get JWT Token
# ---------------------------
def get_token():
    token_url = f"{BASE_URL}/token"
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

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
    df = pd.DataFrame(data)
    for col in df.columns:
        if "Date" in col or "Time" in col:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    df = df.fillna("")
    return df

# ---------------------------
# Step 4: Store Data in Dremio Data Lake
# ---------------------------
def store_in_dremio(df: pd.DataFrame, table_name: str):
    try:
        conn = pyodbc.connect(DREMIO_CONN_STR, autocommit=True)
        cursor = conn.cursor()

        # Ensure Dremio table exists (all columns defined as VARCHAR)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {DREMIO_WORKSPACE}.{table_name} (
            {', '.join([f'"{col}" VARCHAR' for col in df.columns])}
        )
        """
        cursor.execute(create_table_query)

        # Insert data into Dremio
        for _, row in df.iterrows():
            columns = ', '.join([f'"{col}"' for col in df.columns])
            values = ', '.join(['?' for _ in df.columns])
            insert_query = f"INSERT INTO {DREMIO_WORKSPACE}.{table_name} ({columns}) VALUES ({values})"
            cursor.execute(insert_query, tuple(row))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Stored {df.shape[0]} records in Dremio table: {table_name}")
    except Exception as e:
        print(f"Error storing data in Dremio: {e}")

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

    for key, endpoint in ENDPOINTS.items():
        try:
            print(f"Fetching data from {endpoint}...")
            data = get_data(endpoint, token)
            print(f"Fetched {len(data)} records from {key}.")
            
            df = clean_data(data)
            print(f"Cleaned data for {key}: {df.shape[0]} rows, {df.shape[1]} columns.")
            
            store_in_dremio(df, key)
        except Exception as e:
            print(f"Error processing {key} data: {e}")

if __name__ == "__main__":
    main()
