import os
import requests
import pymongo
from pymongo import MongoClient
import datetime
from datetime import date, datetime, timedelta, timezone
import calendar
import statistics
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# ---------------------------
# Configuration
# ---------------------------
SUCCESSFACTORS_URL = os.getenv("SUCCESSFACTORS_URL")
MONGO_URI = os.getenv("MONGO_ATLAS_URI")
MONGO_DB = os.getenv("MONGO_ATLAS_DB")
API_USERNAME = os.getenv("ADMIN_USERNAME")
API_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not SUCCESSFACTORS_URL or not MONGO_URI or not MONGO_DB:
   raise Exception("Missing required environment variables.")

# ---------------------------
# Helper functions for date boundaries
# ---------------------------
def get_month_boundaries(year: int, month: int):
   start = date(year, month, 1)
   end = date(year, month, calendar.monthrange(year, month)[1])
   return start, end

def get_previous_month(year: int, month: int):
   if month == 1:
       return year - 1, 12
   else:
       return year, month - 1

def parse_iso_date(date_str):
   # Expecting date in ISO format "YYYY-MM-DD"
   if not date_str:
       return None
   try:
       return datetime.strptime(date_str, "%Y-%m-%d").date()
   except Exception:
       print(f"Failed to parse date: {date_str}")
       return None

# ---------------------------
# Fetch employee data from SuccessFactors API
# ---------------------------
def get_base_url():
   """Extract base URL from the SUCCESSFACTORS_URL."""
   # Split URL into parts and take the scheme and domain part
   parts = SUCCESSFACTORS_URL.split('/')
   if len(parts) >= 3:
       return f"{parts[0]}//{parts[2]}"
   return SUCCESSFACTORS_URL  # Fallback to original URL if can't parse

def get_jwt_token():
   """Obtain a JWT token from the /token endpoint."""
   base_url = get_base_url()
   url = f"{base_url}/token"
   data = {"username": API_USERNAME, "password": API_PASSWORD}
   response = requests.post(url, data=data)
   response.raise_for_status()
   return response.json()["access_token"]

def fetch_employee_data():
   """Fetch all employees from SuccessFactors API."""
   token = get_jwt_token()
   url = f"{SUCCESSFACTORS_URL}/employees"
   headers = {"Authorization": f"Bearer {token}"}
   response = requests.get(url, headers=headers)
   response.raise_for_status()
   return response.json()

# ---------------------------
# Compute Dashboard Metrics
# ---------------------------
def compute_dashboard_metrics(employees):
   # Set current date to April 2021
   today = date(2021, 4, 30)
   
   # Debug: Print first few employees to check structure
   print(f"Sample employee data (first item): {employees[0] if employees else 'No employees'}")
   
   # Use "HireDate" as the join date instead of "JoinDate", checking both key variations
   def get_hire_date(e):
       hire_date = e.get("HireDate") or e.get("hireDate")
       return hire_date
   
   # Debug: Count employees with hire dates
   employees_with_hire_dates = [e for e in employees if get_hire_date(e)]
   print(f"Employees with hire dates: {len(employees_with_hire_dates)} out of {len(employees)}")
   
   # Filter active employees: those who have joined before or by the current month end
   # and have not been terminated yet
   current_year, current_month = today.year, today.month
   current_start, current_end = get_month_boundaries(current_year, current_month)
   
   # Debug: Check termination date field
   employees_with_term_dates = [e for e in employees if e.get("TerminationDate") or e.get("terminationDate")]
   print(f"Employees with termination dates: {len(employees_with_term_dates)} out of {len(employees)}")
   
   # Make field access case-insensitive
   def get_termination_date(e):
       return e.get("TerminationDate") or e.get("terminationDate")

   # Updated active employees logic with more robust checks
   active_employees = []
   for e in employees:
       hire_date_str = get_hire_date(e)
       term_date_str = get_termination_date(e)
       
       hire_date = parse_iso_date(hire_date_str)
       term_date = parse_iso_date(term_date_str)
       
       if hire_date and hire_date <= current_end and (not term_date or term_date > today):
           active_employees.append(e)
   
   print(f"Active employees found: {len(active_employees)}")
   total_active = len(active_employees)
   
   # New hires in current month and departures in current month
   new_hires = []
   for e in employees:
       hire_date_str = get_hire_date(e)
       hire_date = parse_iso_date(hire_date_str)
       
       if hire_date and current_start <= hire_date <= current_end:
           new_hires.append(e)
   
   print(f"New hires found: {len(new_hires)}")
   
   departures = []
   for e in employees:
       term_date_str = get_termination_date(e)
       term_date = parse_iso_date(term_date_str)
       
       if term_date and current_start <= term_date <= current_end:
           departures.append(e)
   
   print(f"Departures found: {len(departures)}")
   
   # For MoM growth and attrition, fetch previous month's active count and departures
   prev_year, prev_month = get_previous_month(current_year, current_month)
   prev_start, prev_end = get_month_boundaries(prev_year, prev_month)
   
   active_prev = []
   for e in employees:
       hire_date_str = get_hire_date(e)
       term_date_str = get_termination_date(e)
       
       hire_date = parse_iso_date(hire_date_str)
       term_date = parse_iso_date(term_date_str)
       
       if hire_date and hire_date <= prev_end and (not term_date or term_date > prev_end):
           active_prev.append(e)
   
   print(f"Previous month active employees: {len(active_prev)}")
   
   new_hires_prev = []
   for e in employees:
       hire_date_str = get_hire_date(e)
       hire_date = parse_iso_date(hire_date_str)
       
       if hire_date and prev_start <= hire_date <= prev_end:
           new_hires_prev.append(e)
   
   departures_prev = []
   for e in employees:
       term_date_str = get_termination_date(e)
       term_date = parse_iso_date(term_date_str)
       
       if term_date and prev_start <= term_date <= prev_end:
           departures_prev.append(e)
   
   total_active_prev = len(active_prev)
   
   mom_growth = ((total_active - total_active_prev) / total_active_prev * 100) if total_active_prev > 0 else None
   current_attrition_rate = (len(departures) / total_active_prev * 100) if total_active_prev > 0 else None
   prev_attrition_rate = (len(departures_prev) / total_active_prev * 100) if total_active_prev > 0 else None
   mom_attrition_change = (current_attrition_rate - prev_attrition_rate) if (current_attrition_rate is not None and prev_attrition_rate is not None) else None

   # Gender ratio between male and female among active employees
   male_count = 0
   female_count = 0
   for e in active_employees:
       # Make gender field access case-insensitive
       gender = (e.get("Gender") or e.get("gender") or "Unknown").lower()
       if gender == "male":
           male_count += 1
       elif gender == "female":
           female_count += 1
   
   print(f"Gender counts - Male: {male_count}, Female: {female_count}")
   
   gender_ratio = None
   if female_count > 0:
       gender_ratio = male_count / female_count
   
   gender_counts = {
       "Male": male_count,
       "Female": female_count,
       "MaleToFemaleRatio": gender_ratio
   }

   # Average tenure for active employees (years)
   tenures = []
   for e in active_employees:
       hire_date_str = get_hire_date(e)
       hire_date = parse_iso_date(hire_date_str)
       if hire_date:
           tenure = (today - hire_date).days / 365.25
           tenures.append(tenure)
   
   print(f"Tenures calculated for {len(tenures)} employees")
   average_tenure = statistics.mean(tenures) if tenures else None

   # Metrics for the past 5 months
   metrics_past_5_months = []
   for i in range(5):
       year, month = current_year, current_month - i
       while month <= 0:
           month += 12
           year -= 1
       m_start, m_end = get_month_boundaries(year, month)
       
       new_hires_month = 0
       departures_month = 0
       active_month = 0
       
       for e in employees:
           hire_date_str = get_hire_date(e)
           term_date_str = get_termination_date(e)
           
           hire_date = parse_iso_date(hire_date_str)
           term_date = parse_iso_date(term_date_str)
           
           if hire_date and m_start <= hire_date <= m_end:
               new_hires_month += 1
               
           if term_date and m_start <= term_date <= m_end:
               departures_month += 1
               
           if hire_date and hire_date <= m_end and (not term_date or term_date > m_end):
               active_month += 1
       
       metrics_past_5_months.append({
           "month": f"{year}-{str(month).zfill(2)}",
           "newHires": new_hires_month,
           "departures": departures_month,
           "totalActiveEmployees": active_month,
       })

   # Recent activity for current month
   def get_name_and_department(e):
       first_name = e.get("FirstName") or e.get("firstName") or ""
       last_name = e.get("LastName") or e.get("lastName") or ""
       department = e.get("Department") or e.get("department") or "N/A"
       return {"name": f"{first_name} {last_name}".strip(), "department": department}
   
   recent_joined = [get_name_and_department(e) for e in new_hires]
   recent_left = [get_name_and_department(e) for e in departures]

   dashboard = {
       "reportDate": today.isoformat(),
       "totalActiveEmployees": total_active,
       "newHires": len(new_hires),
       "departures": len(departures),
       "MoMGrowth": mom_growth,
       "currentAttritionRate": current_attrition_rate,
       "MoMAttritionChange": mom_attrition_change,
       "genderRatio": gender_counts,
       "averageTenure": average_tenure,
       "metricsPast5Months": metrics_past_5_months,
       "recentActivity": {
           "joined": recent_joined,
           "left": recent_left,
       },
       "createdAt": datetime.now(timezone.utc),
       "updatedAt": datetime.now(timezone.utc),
   }

   return dashboard

# ---------------------------
# Main function: Fetch data, compute metrics, store in MongoDB
# ---------------------------
def main():
   try:
       employees = fetch_employee_data()
       print(f"Fetched {len(employees)} employees from SuccessFactors API.")
   except Exception as e:
       print(f"Error fetching employees: {e}")
       return

   dashboardData = compute_dashboard_metrics(employees)

   try:
       client = MongoClient(MONGO_URI)
       db = client[MONGO_DB]
       dashboard_coll = db["Dashboard"]
       # Clear previous dashboard documents:
       deleted = dashboard_coll.delete_many({})
       print(f"Cleared {deleted.deleted_count} existing dashboard documents.")
       result = dashboard_coll.insert_one(dashboardData)
       print("Dashboard data inserted with id:", result.inserted_id)
       client.close()
   except Exception as e:
       print(f"Error storing dashboard data in MongoDB: {e}")

if __name__ == "__main__":
   main()