import os
import requests
import pymongo
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------
# 1. Configuration
# -----------------------------------------------------------------
# FastAPI (SuccessFactors API) base URL
BASE_URL = os.getenv("BASE_URL")

# Credentials for obtaining JWT token from /token
API_USERNAME = os.getenv("ADMIN_USERNAME")
API_PASSWORD = os.getenv("ADMIN_PASSWORD")

# MongoDB Atlas connection details
MONGO_URI = os.getenv("MONGO_ATLAS_URI")
MONGO_DB = os.getenv("MONGO_ATLAS_DB")

# Name of the MongoDB collection where we'll store employee documents
EMPLOYEES_COLLECTION = "Employees"

# -----------------------------------------------------------------
# 2. Helper Functions
# -----------------------------------------------------------------
def get_jwt_token():
    """
    Obtain a JWT token by posting credentials to /token endpoint.
    Returns the token string (without 'Bearer').
    """
    url = f"{BASE_URL}/token"
    data = {
        "username": API_USERNAME,
        "password": API_PASSWORD
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    result = response.json()
    return result["access_token"]

def get_employees(token):
    """
    Fetch all employees from the SuccessFactors API.
    Returns a list of employee dictionaries.
    """
    url = f"{BASE_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()  # list of dicts

def get_employment_details(token, employee_id):
    """
    Fetch employment details for a specific employee.
    Returns a dict or None if not found.
    """
    url = f"{BASE_URL}/employment_details/{employee_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def calculate_age(dob):
    """
    Given a date of birth (YYYY-MM-DD), calculate the integer age.
    """
    if not dob:
        return None
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# -----------------------------------------------------------------
# 3. Main Script
# -----------------------------------------------------------------
def main():
    # 3A. Get a JWT token
    token = get_jwt_token()
    print("Obtained JWT token successfully.")

    # 3B. Connect to MongoDB
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    employees_coll = db[EMPLOYEES_COLLECTION]

    # 3C. Fetch all employees
    employees_list = get_employees(token)
    print(f"Fetched {len(employees_list)} employees from SuccessFactors API.")

    # 3D. Process each employee, fetch their EmploymentDetails, build doc, and store in MongoDB
    docs_to_insert = []
    for emp in employees_list:
        # Employee object has keys like:
        #  - EmployeeID
        #  - FirstName
        #  - LastName
        #  - Email
        #  - Gender
        #  - DateOfBirth
        #  - etc.

        emp_id = emp["EmployeeID"]

        # Fetch EmploymentDetails
        emp_details = get_employment_details(token, emp_id)

        # Compute Age from DateOfBirth
        dob_str = emp.get("DateOfBirth")  # e.g. "1990-01-01"
        dob_obj = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
        age = calculate_age(dob_obj) if dob_obj else None

        # Build a combined document
        # Fields from the image:
        #   - First Name => emp["FirstName"]
        #   - Last Name  => emp["LastName"]
        #   - Email      => emp["Email"]
        #   - Department => emp_details["Department"] if present
        #   - Position   => emp_details["JobTitle"] if present
        #   - Status     => emp_details["EmploymentStatus"] if present
        #   - Join Date  => emp_details["HireDate"] if present
        #   - Gender     => emp["Gender"]
        #   - Age        => computed from DateOfBirth
        # Note: The top label "Employees" might just be the doc name in your spreadsheet.

        doc = {
            "EmployeeID": emp_id,
            "FirstName": emp["FirstName"],
            "LastName": emp["LastName"],
            "Email": emp["Email"],
            "Department": emp_details["Department"] if emp_details else None,
            "Position": emp_details["JobTitle"] if emp_details else None,
            "Status": emp_details["EmploymentStatus"] if emp_details else None,
            "JoinDate": emp_details["HireDate"] if emp_details else None,
            "Gender": emp["Gender"],
            "Age": age
        }

        docs_to_insert.append(doc)

    # 3E. Insert or Upsert into MongoDB
    # We can insert them all at once, or upsert by EmployeeID if you want updates.
    # For simplicity, let's just do a bulk insert (or replace).
    # If you want to avoid duplicates, you could do upsert logic with e.g. update_one(..., upsert=True).
    for doc in docs_to_insert:
        employees_coll.update_one(
            {"EmployeeID": doc["EmployeeID"]},  # filter
            {"$set": doc},                      # update
            upsert=True                         # insert if not found
        )

    print(f"Upserted {len(docs_to_insert)} documents into MongoDB collection '{EMPLOYEES_COLLECTION}'.")

    client.close()
    print("Done!")

if __name__ == "__main__":
    main()
