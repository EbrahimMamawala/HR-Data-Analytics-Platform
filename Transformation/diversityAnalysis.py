import os
import requests
import pymongo
from datetime import datetime, date, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import calendar

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------
# SuccessFactors API (FastAPI) base URL; e.g., http://localhost:8000
BASE_URL = os.getenv("SUCCESSFACTORS_URL")

# Credentials for obtaining JWT token from SuccessFactors API
API_USERNAME = os.getenv("ADMIN_USERNAME")
API_PASSWORD = os.getenv("ADMIN_PASSWORD")

# MongoDB Atlas connection details
MONGO_URI = os.getenv("MONGO_ATLAS_URI")
MONGO_DB = os.getenv("MONGO_ATLAS_DB")

# Collections
EMPLOYEES_COLLECTION = "Employees"        # (if needed)
DIVERSITY_COLLECTION = "Diversity"

# -----------------------------------------------------------------
# Helper Functions for API Calls
# -----------------------------------------------------------------
def get_jwt_token():
    """Obtain a JWT token from the /token endpoint."""
    url = f"{BASE_URL}/token"
    data = {"username": API_USERNAME, "password": API_PASSWORD}
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_employees(token):
    """Fetch all employees from SuccessFactors API (/employees)."""
    url = f"{BASE_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()  # Expecting a list of employee dicts

def get_employment_details(token, employee_id):
    """Fetch employment details for a given employee using /employment_details/{employee_id}."""
    url = f"{BASE_URL}/employment_details/{employee_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    # If not found, return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def calculate_age(dob):
    """Given a date of birth (as date object), calculate age."""
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# -----------------------------------------------------------------
# Helper Functions for Aggregation
# -----------------------------------------------------------------
def get_age_group(age):
    if age is None:
        return None
    if 18 <= age <= 25:
        return "18-25"
    elif 26 <= age <= 35:
        return "26-35"
    elif 36 <= age <= 45:
        return "36-45"
    elif 46 <= age <= 55:
        return "46-55"
    elif age >= 56:
        return "56+"
    else:
        return "Unknown"

def get_tenure_group(tenure_years):
    if tenure_years < 1:
        return "<1"
    elif 1 <= tenure_years < 3:
        return "1-3"
    elif 3 <= tenure_years < 5:
        return "3-5"
    elif 5 <= tenure_years < 10:
        return "5-10"
    else:
        return "10+"

def init_agg():
    """Initialize an aggregation dictionary structure."""
    return {
       "gender_distribution": defaultdict(int),
       "age_distribution": defaultdict(int),
       "tenure_distribution": defaultdict(int),
       "diversity_by_department": defaultdict(lambda: defaultdict(int))
    }

def get_period_start(frequency, period):
    """Compute the start date for a given period.
       - For month: period format "YYYY-MM"
       - For quarter: period format "YYYY-Qn"
       - For year: period is "YYYY"
       - For last_5_months: we approximate by today - 150 days.
    """
    if frequency == "month":
        year, month = map(int, period.split("-"))
        return date(year, month, 1)
    elif frequency == "quarter":
        parts = period.split("-Q")
        year = int(parts[0])
        quarter = int(parts[1])
        month = (quarter - 1) * 3 + 1
        return date(year, month, 1)
    elif frequency == "year":
        return date(int(period), 1, 1)
    elif frequency == "last_5_months":
        return date.today() - timedelta(days=150)
    else:
        return None

def get_period_end(frequency, period):
    """Compute the end date for a given period."""
    if frequency == "month":
        year, month = map(int, period.split("-"))
        # Get the last day of the month
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, last_day)
    elif frequency == "quarter":
        parts = period.split("-Q")
        year = int(parts[0])
        quarter = int(parts[1])
        end_month = quarter * 3
        last_day = calendar.monthrange(year, end_month)[1]
        return date(year, end_month, last_day)
    elif frequency == "year":
        year = int(period)
        return date(year, 12, 31)
    elif frequency == "last_5_months":
        return date.today()
    else:
        return None

# Helper to convert aggregation dictionary to regular dict
def make_doc(frequency, period, agg):
    return {
        "frequency": frequency,
        "period": period,
        "gender_distribution": dict(agg["gender_distribution"]),
        "age_distribution": dict(agg["age_distribution"]),
        "tenure_distribution": dict(agg["tenure_distribution"]),
        "diversity_by_department": {dept: dict(genders) for dept, genders in agg["diversity_by_department"].items()}
    }

# -----------------------------------------------------------------
# Main Script
# -----------------------------------------------------------------
def main():
    # Connect to MongoDB Atlas first
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    diversity_coll = db[DIVERSITY_COLLECTION]

    # Clear all collections before starting
    diversity_result = diversity_coll.delete_many({})
    
    print(f"Cleared MongoDB collection '{DIVERSITY_COLLECTION}'. Deleted {diversity_result.deleted_count} documents.")

    # 1. Get JWT token from SuccessFactors API
    token = get_jwt_token()
    print("Obtained JWT token.")

    # 2. Fetch employees from SuccessFactors API
    employees = get_employees(token)
    print(f"Fetched {len(employees)} employees from SuccessFactors API.")

    today = date.today()

    # Prepare aggregation dictionaries
    monthly = {}
    quarterly = {}
    yearly = {}
    last_5_months = init_agg()

    # Get all possible periods for aggregation
    all_periods = set()
    for emp in employees:
        emp_id = emp.get("EmployeeID")
        emp_details = get_employment_details(token, emp_id)
        if not emp_details or not emp_details.get("HireDate"):
            continue

        # Parse HireDate
        join_date_raw = emp_details.get("HireDate")
        if isinstance(join_date_raw, str):
            try:
                join_date = datetime.strptime(join_date_raw, "%Y-%m-%d").date()
            except ValueError:
                continue
        elif isinstance(join_date_raw, datetime):
            join_date = join_date_raw.date()
        else:
            continue
            
        # Create period keys and add to our sets
        month_key = join_date.strftime("%Y-%m")
        quarter = (join_date.month - 1) // 3 + 1
        quarter_key = f"{join_date.year}-Q{quarter}"
        year_key = str(join_date.year)
        
        all_periods.add(("month", month_key))
        all_periods.add(("quarter", quarter_key))
        all_periods.add(("year", year_key))

    # Initialize aggregation structures for all periods
    for freq, period in all_periods:
        if freq == "month":
            monthly[period] = init_agg()
        elif freq == "quarter":
            quarterly[period] = init_agg()
        elif freq == "year":
            yearly[period] = init_agg()

    # Process each employee for each period
    for emp in employees:
        emp_id = emp.get("EmployeeID")
        # Get employment details (which includes HireDate and TerminationDate)
        emp_details = get_employment_details(token, emp_id)
        if not emp_details or not emp_details.get("HireDate"):
            continue  # Skip if no HireDate

        # Parse HireDate
        join_date_raw = emp_details.get("HireDate")
        if isinstance(join_date_raw, str):
            try:
                join_date = datetime.strptime(join_date_raw, "%Y-%m-%d").date()
            except ValueError:
                continue
        elif isinstance(join_date_raw, datetime):
            join_date = join_date_raw.date()
        else:
            continue

        # Parse TerminationDate (if exists)
        termination_date = None
        term_date_raw = emp_details.get("TerminationDate")
        if term_date_raw:
            try:
                if isinstance(term_date_raw, str):
                    termination_date = datetime.strptime(term_date_raw, "%Y-%m-%d").date()
                elif isinstance(term_date_raw, datetime):
                    termination_date = term_date_raw.date()
            except Exception:
                termination_date = None

        # Compute Age from employee document's DateOfBirth if available
        dob_str = emp.get("DateOfBirth")
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                dob = None
        else:
            dob = None
        age = calculate_age(dob) if dob else None
        age_group = get_age_group(age) if age is not None else None

        gender = emp.get("Gender")
        department = emp_details.get("Department")  # assume department from employment details

        # Aggregate for each period
        for freq, period_key in all_periods:
            period_start = get_period_start(freq, period_key)
            period_end = get_period_end(freq, period_key)
            
            # Check if employee was active during this period:
            # 1. Employee joined on or before the end of the period
            # 2. Employee was not terminated before the start of the period
            if join_date <= period_end and (termination_date is None or termination_date >= period_start):
                # Employee was active during this period
                if freq == "month":
                    agg = monthly[period_key]
                elif freq == "quarter":
                    agg = quarterly[period_key]
                elif freq == "year":
                    agg = yearly[period_key]
                else:
                    continue
                
                # Compute tenure as of the end of the period
                tenure_days = (min(period_end, termination_date or today) - join_date).days
                tenure_years = tenure_days / 365.25
                tenure_group = get_tenure_group(tenure_years)
                
                # Add to aggregation
                if gender:
                    agg["gender_distribution"][gender] += 1
                if age_group:
                    agg["age_distribution"][age_group] += 1
                if tenure_group:
                    agg["tenure_distribution"][tenure_group] += 1
                if department and gender:
                    agg["diversity_by_department"][department][gender] += 1
        
        # Handle the special case for last 5 months
        last_5_months_start = get_period_start("last_5_months", "last_5_months")
        if join_date <= today and (termination_date is None or termination_date >= last_5_months_start):
            # Only include in last_5_months if join_date is within last 5 months
            if join_date >= last_5_months_start:
                if gender:
                    last_5_months["gender_distribution"][gender] += 1

    # Build Diversity Documents
    diversity_docs = []
    for period, agg in monthly.items():
        diversity_docs.append(make_doc("month", period, agg))
    for period, agg in quarterly.items():
        diversity_docs.append(make_doc("quarter", period, agg))
    for period, agg in yearly.items():
        diversity_docs.append(make_doc("year", period, agg))
    diversity_docs.append(make_doc("last_5_months", "last_5_months", last_5_months))

    # Insert Diversity Documents into MongoDB Atlas
    if diversity_docs:
        diversity_coll.insert_many(diversity_docs)
        print(f"Inserted {len(diversity_docs)} Diversity documents into collection '{DIVERSITY_COLLECTION}'.")
    else:
        print("No diversity data computed.")

    client.close()
    print("Done.")

if __name__ == "__main__":
    main()