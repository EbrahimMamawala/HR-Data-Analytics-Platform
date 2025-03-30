import os
import random
import datetime
import uuid
import json
from faker import Faker
from pymongo import MongoClient
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------
# 1. Connect to MySQL (SuccessFactorsDB) to fetch employees
# -----------------------------------------------------------
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_successfactors_db = os.getenv("MYSQL_SUCCESSFACTORS_DATABASE")
mysql_auth_plugin = os.getenv("MYSQL_AUTH_PLUGIN")  # e.g., caching_sha2_password

mysql_conn = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_successfactors_db,
    auth_plugin=mysql_auth_plugin
)
mysql_cur = mysql_conn.cursor()

# Retrieve all EmployeeIDs from SuccessFactorsDB
mysql_cur.execute("SELECT EmployeeID FROM Employee;")
employee_rows = mysql_cur.fetchall()
mysql_cur.close()
mysql_conn.close()

employee_ids = [row[0] for row in employee_rows]
if not employee_ids:
    raise ValueError("No employees found in SuccessFactorsDB. Cannot create consistent data in MongoDB.")

# -----------------------------------------------------------
# 2. Connect to MongoDB (LearningPlatformDB)
# -----------------------------------------------------------
mongo_uri = os.getenv("MONGO_URI")
mongo_db_name = os.getenv("MONGO_DB")
client = MongoClient(mongo_uri)
db = client[mongo_db_name]

# Optional: drop collections if you want a clean slate
db.courses.drop()
db.modules.drop()
db.enrollments.drop()
db.assessments.drop()
db.certificates.drop()

courses_collection = db["courses"]
modules_collection = db["modules"]
enrollments_collection = db["enrollments"]
assessments_collection = db["assessments"]
certificates_collection = db["certificates"]

# -----------------------------------------------------------
# 3. Generate 10,000 documents per collection
# -----------------------------------------------------------
fake = Faker()
now = datetime.datetime.now()

def random_course_dates():
    """Generate random start/end dates within the next 30 to 90 days."""
    start_date = fake.date_between(start_date="today", end_date="+30d")
    end_date = start_date + datetime.timedelta(days=random.randint(15, 90))
    return start_date, end_date

# Utility to convert date -> datetime for MongoDB
def date_to_datetime(date_obj):
    return datetime.datetime.combine(date_obj, datetime.time(0, 0, 0))

# ------------------------------------------
# 3A. Generate 10,000 Courses
# ------------------------------------------
course_categories = ["Technology", "Finance", "Management", "Marketing", "HR", "Data Science"]
course_docs = []

for i in range(1, 10001):
    start_date, end_date = random_course_dates()
    # Convert date objects to datetime
    start_dt = date_to_datetime(start_date)
    end_dt = date_to_datetime(end_date)

    doc = {
        "CourseID": i,  # Simulate a SERIAL-like ID
        "CourseName": fake.catch_phrase()[:50],
        "Description": fake.paragraph(nb_sentences=2),
        "Category": random.choice(course_categories),
        "Duration": round(random.uniform(5, 200), 2),
        "Price": round(random.uniform(500.0, 5000.0), 2),
        "StartDate": start_dt,
        "EndDate": end_dt,
        "CreatedAt": now,
        "UpdatedAt": now
    }
    course_docs.append(doc)

courses_collection.insert_many(course_docs)
print("Inserted 10,000 courses into MongoDB.")

# ------------------------------------------
# 3B. Generate 10,000 Modules
# ------------------------------------------
module_docs = []
for i in range(1, 10001):
    random_course_id = random.randint(1, 10000)
    doc = {
        "ModuleID": i,
        "CourseID": random_course_id,  # references a CourseID
        "ModuleName": f"Module {i}",
        "ModuleDescription": fake.paragraph(nb_sentences=1),
        "CreatedAt": now,
        "UpdatedAt": now
    }
    module_docs.append(doc)

modules_collection.insert_many(module_docs)
print("Inserted 10,000 modules into MongoDB.")

# ------------------------------------------
# 3C. Generate 10,000 Enrollments
# ------------------------------------------
status_choices = ["active", "completed", "in_progress", "cancelled"]
enrollment_docs = []
for i in range(1, 10001):
    enroll_date = fake.date_between(start_date="-60d", end_date="today")
    enroll_dt = date_to_datetime(enroll_date)

    doc = {
        "EnrollmentID": i,
        "EmployeeID": random.choice(employee_ids),  # from SuccessFactors
        "CourseID": random.randint(1, 10000),         # must match a valid course
        "EnrollDate": enroll_dt,
        "Status": random.choice(status_choices),
        "CreatedAt": now,
        "UpdatedAt": now
    }
    enrollment_docs.append(doc)

enrollments_collection.insert_many(enrollment_docs)
print("Inserted 10,000 enrollments into MongoDB.")

# ------------------------------------------
# 3D. Generate 10,000 Assessments
# ------------------------------------------
assessment_docs = []
for i in range(1, 10001):
    doc = {
        "AssessmentID": i,
        "EnrollmentID": random.randint(1, 10000),  # references an Enrollment
        "Title": f"Assessment #{i}",
        "PassingMarks": round(random.uniform(30, 80), 2),
        "CreatedAt": now,
        "UpdatedAt": now
    }
    assessment_docs.append(doc)

assessments_collection.insert_many(assessment_docs)
print("Inserted 10,000 assessments into MongoDB.")

# ------------------------------------------
# 3E. Generate 10,000 Certificates
# ------------------------------------------
certificate_docs = []
for i in range(1, 10001):
    issue_date = fake.date_between(start_date="-60d", end_date="today")
    issue_dt = date_to_datetime(issue_date)

    doc = {
        "CertificateID": i,
        "EnrollmentID": random.randint(1, 10000),  # references an Enrollment
        "CertificateName": f"Certificate {i}",
        "IssuedDate": issue_dt,
        "CreatedAt": now,
        "UpdatedAt": now
    }
    certificate_docs.append(doc)

certificates_collection.insert_many(certificate_docs)
print("Inserted 10,000 certificates into MongoDB.")

# -----------------------------------------------------------
# 4. Done!
# -----------------------------------------------------------
print("All data inserted successfully into LearningPlatformDB in MongoDB.")
