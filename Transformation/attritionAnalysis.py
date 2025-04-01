import os
import requests
import pymongo
from datetime import datetime, date, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------
# SuccessFactors API (FastAPI) base URL
SUCCESSFACTORS_URL = os.getenv("SUCCESSFACTORS_URL")
# Exit Management API base URL
EXITMANAGEMENT_URL = os.getenv("EXITMANAGEMENT_URL")

# Credentials for obtaining JWT token (assumed same for both APIs)
API_USERNAME = os.getenv("ADMIN_USERNAME")
API_PASSWORD = os.getenv("ADMIN_PASSWORD")

# MongoDB Atlas connection details
MONGO_URI = os.getenv("MONGO_ATLAS_URI")
MONGO_DB = os.getenv("MONGO_ATLAS_DB")
ATTRITION_COLLECTION = "Attrition"

# Predefined voluntary exit reasons
resignation_reasons = [
    "Personal reasons",
    "Relocation",
    "Better career opportunity",
    "Work-life balance",
    "Health issues"
]

# -----------------------------------------------------------------
# Helper Functions for API Calls
# -----------------------------------------------------------------
def get_jwt_token(url_base):
    """Obtain a JWT token from the /token endpoint of the given base URL."""
    url = f"{url_base}/token"
    data = {"username": API_USERNAME, "password": API_PASSWORD}
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_employees(token):
    """Fetch all employees from SuccessFactors API."""
    url = f"{SUCCESSFACTORS_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_employment_details(token, employee_id):
    """Fetch employment details for a given employee from SuccessFactors API."""
    url = f"{SUCCESSFACTORS_URL}/employment_details/{employee_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def get_resignation_requests(token):
    """Fetch all resignation requests from Exit Management API."""
    url = f"{EXITMANAGEMENT_URL}/resignation_requests"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# -----------------------------------------------------------------
# Helper Functions for Period Keys and Aggregation
# -----------------------------------------------------------------
def get_month_key(d):
    return d.strftime("%Y-%m")

def get_quarter_key(d):
    quarter = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{quarter}"

def get_year_key(d):
    return str(d.year)

def get_period_start(frequency, period):
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

def init_attrition_agg():
    return {
        "new_hires": 0,
        "active_employees": 0,
        "voluntary_exit": 0,
        "attrition_by_department": defaultdict(int),
        "exit_reasons": defaultdict(int)
    }

def make_attrition_doc(frequency, period, agg):
    total = agg["active_employees"] + agg["voluntary_exit"]
    attrition_rate = (agg["voluntary_exit"] / total * 100) if total > 0 else 0
    return {
        "frequency": frequency,
        "period": period,
        "new_hires": agg["new_hires"],
        "active_employees": agg["active_employees"],
        "voluntary_exit": agg["voluntary_exit"],
        "attrition_rate": attrition_rate,
        "attrition_by_department": dict(agg["attrition_by_department"]),
        "exit_reasons": dict(agg["exit_reasons"])
    }

# -----------------------------------------------------------------
# Main Script
# -----------------------------------------------------------------
def main():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    attrition_coll = db[ATTRITION_COLLECTION]
    print("Obtained JWT tokens for SuccessFactors and Exit Management APIs.")
    
    # 1. Get JWT tokens for both APIs
    token_sf = get_jwt_token(SUCCESSFACTORS_URL)
    token_exit = get_jwt_token(EXITMANAGEMENT_URL)
    
    # Clear the Attrition collection
    result = attrition_coll.delete_many({})
    print(f"Cleared MongoDB collection '{ATTRITION_COLLECTION}'. Deleted {result.deleted_count} documents.")

    # 2. Fetch employees from SuccessFactors API and build a dictionary of employment details.
    employees = get_employees(token_sf)
    emp_data = {}  # key: EmployeeID, value: dict with HireDate, TerminationDate, Department
    for emp in employees:
        emp_id = emp.get("EmployeeID")
        details = get_employment_details(token_sf, emp_id)
        if not details or not details.get("HireDate"):
            continue
        try:
            hire_date = datetime.strptime(details.get("HireDate"), "%Y-%m-%d").date()
        except Exception:
            continue
        termination_date = None
        if details.get("TerminationDate"):
            try:
                termination_date = datetime.strptime(details.get("TerminationDate"), "%Y-%m-%d").date()
            except Exception:
                termination_date = None
        department = details.get("Department")
        emp_data[emp_id] = {
            "HireDate": hire_date,
            "TerminationDate": termination_date,
            "Department": department
        }
    print(f"Processed employment details for {len(emp_data)} employees.")

    # 3. Fetch voluntary exit requests from Exit Management API.
    resignation_requests = get_resignation_requests(token_exit)
    # Filter only voluntary exits (Reason in resignation_reasons and EffectiveDate exists)
    voluntary_requests = []
    for req in resignation_requests:
        if req.get("Reason") in resignation_reasons and req.get("EffectiveDate"):
            try:
                req["EffectiveDate"] = datetime.strptime(req["EffectiveDate"], "%Y-%m-%d").date()
            except Exception:
                req["EffectiveDate"] = None
            if req["EffectiveDate"]:
                voluntary_requests.append(req)
    print(f"Found {len(voluntary_requests)} voluntary exit requests.")

    # 4. Prepare aggregation dictionaries for each frequency.
    frequencies = ["month", "quarter", "year", "last_5_months"]
    agg_data = {freq: defaultdict(init_attrition_agg) for freq in frequencies}
    # For last_5_months, we use a single key "last_5_months".
    today = date.today()

    # 5. Aggregate employee data from SuccessFactors.
    # For each employee, determine new hires and active employees by period.
    for emp_id, data in emp_data.items():
        hire_date = data["HireDate"]
        termination_date = data["TerminationDate"]
        month_key = get_month_key(hire_date)
        quarter_key = get_quarter_key(hire_date)
        year_key = get_year_key(hire_date)
        # New hires: count in the period where HireDate falls.
        agg_data["month"][month_key]["new_hires"] += 1
        agg_data["quarter"][quarter_key]["new_hires"] += 1
        agg_data["year"][year_key]["new_hires"] += 1
        # Active employees: For each period from hire year to current,
        # if the employee was active at the start of that period (i.e. termination_date is None or >= period start).
        start_year = hire_date.year
        current_year = today.year
        for year in range(start_year, current_year + 1):
            # Monthly aggregation for this year
            for m in range(1, 13):
                period_date = date(year, m, 1)
                if period_date < hire_date or period_date > today:
                    continue
                if termination_date is None or termination_date >= period_date:
                    period_key = f"{year}-{m:02d}"
                    agg_data["month"][period_key]["active_employees"] += 1
            # Quarterly aggregation
            for q in range(1, 5):
                month_start = (q - 1) * 3 + 1
                period_date = date(year, month_start, 1)
                if period_date < hire_date or period_date > today:
                    continue
                if termination_date is None or termination_date >= period_date:
                    period_key = f"{year}-Q{q}"
                    agg_data["quarter"][period_key]["active_employees"] += 1
            # Yearly aggregation
            period_date = date(year, 1, 1)
            if period_date >= hire_date and period_date <= today:
                if termination_date is None or termination_date >= period_date:
                    period_key = str(year)
                    agg_data["year"][period_key]["active_employees"] += 1
        # Last 5 months: if hire_date is within last 150 days and employee active in that window.
        if (today - hire_date).days <= 150:
            if termination_date is None or termination_date >= (today - timedelta(days=150)):
                agg_data["last_5_months"]["last_5_months"]["active_employees"] += 1
                agg_data["last_5_months"]["last_5_months"]["new_hires"] += 1

    # 6. Aggregate voluntary exit requests (from Exit Management API).
    # For each voluntary exit, use its EffectiveDate to determine the period.
    for req in voluntary_requests:
        eff_date = req.get("EffectiveDate")
        if not eff_date:
            continue
        month_key = get_month_key(eff_date)
        quarter_key = get_quarter_key(eff_date)
        year_key = get_year_key(eff_date)
        agg_data["month"][month_key]["voluntary_exit"] += 1
        agg_data["quarter"][quarter_key]["voluntary_exit"] += 1
        agg_data["year"][year_key]["voluntary_exit"] += 1
        # Attrition by department: use employee department from emp_data (if available)
        emp_id = req.get("EmployeeID")
        dept = emp_data.get(emp_id, {}).get("Department")
        if dept:
            agg_data["month"][month_key]["attrition_by_department"][dept] += 1
            agg_data["quarter"][quarter_key]["attrition_by_department"][dept] += 1
            agg_data["year"][year_key]["attrition_by_department"][dept] += 1
        # Exit reasons
        reason = req.get("Reason")
        if reason in resignation_reasons:
            agg_data["month"][month_key]["exit_reasons"][reason] += 1
            agg_data["quarter"][quarter_key]["exit_reasons"][reason] += 1
            agg_data["year"][year_key]["exit_reasons"][reason] += 1

    # Also, for last 5 months, aggregate voluntary exits if effective date is within 150 days.
    for req in voluntary_requests:
        eff_date = req.get("EffectiveDate")
        if not eff_date:
            continue
        if (today - eff_date).days <= 150:
            agg_data["last_5_months"]["last_5_months"]["voluntary_exit"] += 1
            emp_id = req.get("EmployeeID")
            dept = emp_data.get(emp_id, {}).get("Department")
            if dept:
                agg_data["last_5_months"]["last_5_months"]["attrition_by_department"][dept] += 1
            reason = req.get("Reason")
            if reason in resignation_reasons:
                agg_data["last_5_months"]["last_5_months"]["exit_reasons"][reason] += 1

    # 7. Build Attrition Documents for each frequency.
    attrition_docs = []
    for freq in ["month", "quarter", "year"]:
        for period, agg in agg_data[freq].items():
            attrition_docs.append(make_attrition_doc(freq, period, agg))
    attrition_docs.append(make_attrition_doc("last_5_months", "last_5_months", agg_data["last_5_months"]["last_5_months"]))

    # 8. Insert Attrition Documents into MongoDB Atlas (wipe previous data)
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    attrition_coll = db["Attrition"]

    # Wipe previous attrition documents
    attrition_coll.delete_many({})
    if attrition_docs:
        attrition_coll.insert_many(attrition_docs)
        print(f"Inserted {len(attrition_docs)} Attrition documents into collection 'Attrition'.")
    else:
        print("No attrition data computed.")

    client.close()
    print("Done.")

if __name__ == "__main__":
    main()
