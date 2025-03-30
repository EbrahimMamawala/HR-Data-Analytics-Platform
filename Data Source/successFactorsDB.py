import os
import mysql.connector
from mysql.connector import errorcode
from faker import Faker
import random
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------
# 1. Database connection parameters from environment
# ------------------------------------------------------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_SUCCESSFACTORS_DATABASE")
MYSQL_AUTH_PLUGIN = os.getenv("MYSQL_AUTH_PLUGIN")  

try:
    # Connect without specifying a database first
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        auth_plugin=MYSQL_AUTH_PLUGIN
    )
    cur = conn.cursor()

    # Create the database if it doesn't exist
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE};")
    cur.execute(f"USE {MYSQL_DATABASE};")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit(1)
# ------------------------------------------------------------
# 2. Create Tables (if they don't already exist)
# ------------------------------------------------------------
employee_table_sql = """
CREATE TABLE IF NOT EXISTS Employee (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeNumber VARCHAR(50) NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    MiddleName VARCHAR(100),
    PreferredName VARCHAR(100),
    Gender VARCHAR(20),
    DateOfBirth DATE,
    Nationality VARCHAR(50),
    MaritalStatus VARCHAR(20),
    Email VARCHAR(150) UNIQUE,
    ContactNumber VARCHAR(30),
    Address TEXT,
    PhotoURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

employment_details_sql = """
CREATE TABLE IF NOT EXISTS EmploymentDetails (
    EmployeeID INT PRIMARY KEY,
    JobTitle VARCHAR(100) NOT NULL,
    Department VARCHAR(100),
    BusinessUnit VARCHAR(100),
    ManagerID INT,
    JobCode VARCHAR(50),
    EmploymentType VARCHAR(50),
    HireDate DATE,
    TerminationDate DATE,
    EmploymentStatus VARCHAR(50),
    TerminationType VARCHAR(50),
    CONSTRAINT fk_emp FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    CONSTRAINT fk_mgr FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

compensation_sql = """
CREATE TABLE IF NOT EXISTS Compensation (
    EmployeeID INT PRIMARY KEY,
    BaseSalary DECIMAL(12,2),
    Currency VARCHAR(10),
    SalaryFrequency VARCHAR(20),
    LastSalaryChange DATE,
    BonusEligibility BOOLEAN,
    VariablePay DECIMAL(12,2),
    StockOptions INT,
    CONSTRAINT fk_emp_comp FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

performance_sql = """
CREATE TABLE IF NOT EXISTS Performance (
    EmployeeID INT,
    PerformanceYear INT,
    PerformanceRating INT,
    ManagerFeedback TEXT,
    TrainingCompleted TEXT,
    SkillsDeveloped TEXT,
    PromotionIndicator BOOLEAN,
    PRIMARY KEY (EmployeeID, PerformanceYear),
    CONSTRAINT fk_emp_perf FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    CHECK (PerformanceRating BETWEEN 1 AND 5)
) ENGINE=InnoDB;
"""

cur.execute(employee_table_sql)
cur.execute(employment_details_sql)
cur.execute(compensation_sql)
cur.execute(performance_sql)
conn.commit()

# ------------------------------------------------------------
# 3. Delete Existing Data
# ------------------------------------------------------------
# Disable foreign key checks, truncate tables individually, then re-enable foreign key checks.
cur.execute("SET FOREIGN_KEY_CHECKS=0;")
tables_to_truncate = ["Performance", "Compensation", "EmploymentDetails", "Employee"]
for table in tables_to_truncate:
    cur.execute(f"TRUNCATE TABLE {table};")
cur.execute("SET FOREIGN_KEY_CHECKS=1;")
conn.commit()

# ------------------------------------------------------------
# 4. Generate Data for 10,000 Employees and Related Tables
# ------------------------------------------------------------
fake = Faker('en_IN')
num_employees = 10000
today = datetime.date.today()

# Lists to accumulate bulk data
employee_data = []         # For Employee table; keep full tuple to later retrieve DateOfBirth
employment_data = []       # For EmploymentDetails table
compensation_data = []     # For Compensation table
performance_data = []      # For Performance table

# Pre-defined lists/choices
genders = ["Male", "Female", "Other"]
marital_statuses = ["Single", "Married", "Divorced", "Widowed"]
employment_types = ["Full-time", "Part-time", "Contractor", "Intern"]
job_titles = ["Intern", "Junior Developer", "Senior Developer", "Manager", "Director", "Analyst", "Consultant"]
departments = ["IT", "HR", "Finance", "Sales", "Marketing", "Operations"]
business_units = ["North India", "South India", "East India", "West India", "Central India"]
termination_types = ["Resigned", "Fired"]

# Salary ranges in INR (monthly)
salary_ranges = {
    "Intern": (10000, 25000),
    "Junior Developer": (30000, 60000),
    "Senior Developer": (70000, 150000),
    "Manager": (100000, 200000),
    "Director": (200000, 400000),
    "Analyst": (40000, 80000),
    "Consultant": (50000, 120000)
}

# Generate data for Employee table
for i in range(num_employees):
    employee_number = f"E{10000 + i}"
    first_name = fake.first_name()
    last_name = fake.last_name()
    middle_name = fake.first_name() if random.random() < 0.5 else None
    preferred_name = first_name
    gender = random.choice(genders)
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65)
    nationality = "Indian"
    marital_status = random.choice(marital_statuses)
    email = fake.unique.email()
    contact_number = fake.phone_number()[:30]
    address = fake.address().replace("\n", ", ")
    photo_url = "http://example.in/photo.jpg"
    created_at = datetime.datetime.now()
    updated_at = datetime.datetime.now()
    
    employee_data.append((
        employee_number, first_name, last_name, middle_name, preferred_name,
        gender, dob, nationality, marital_status, email, contact_number,
        address, photo_url, created_at, updated_at
    ))

# MySQL insert for Employee table
employee_insert_query = """
INSERT INTO Employee 
(EmployeeNumber, FirstName, LastName, MiddleName, PreferredName, Gender, DateOfBirth, Nationality, MaritalStatus, Email, ContactNumber, Address, PhotoURL, CreatedAt, UpdatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
cur.executemany(employee_insert_query, employee_data)
conn.commit()

# Since the table was truncated, auto-increment starts at 1.
# We assume the inserted rows get sequential EmployeeIDs from 1 to num_employees.
employee_info = {}
for idx, data in enumerate(employee_data):
    emp_id = idx + 1
    dob = data[6]  # the 7th element is DateOfBirth
    employee_info[emp_id] = {"dob": dob}

employee_ids = list(employee_info.keys())

# Generate data for EmploymentDetails, Compensation, and Performance tables for each employee
for emp_id in employee_ids:
    dob = employee_info[emp_id]["dob"]
    earliest_hire = datetime.date(dob.year + 18, 1, 1)
    hire_date = fake.date_between(start_date=earliest_hire, end_date=today)
    
    terminated = random.random() < 0.1
    termination_date = fake.date_between(start_date=hire_date, end_date=today) if terminated else None
    employment_status = "Terminated" if terminated else "Active"
    
    job_title = random.choice(job_titles)
    department = random.choice(departments)
    business_unit = random.choice(business_units)
    if emp_id == min(employee_ids) or job_title in ["Manager", "Director"]:
        manager_id = None
    else:
        possible_managers = [mid for mid in employee_ids if mid < emp_id]
        manager_id = random.choice(possible_managers) if possible_managers else None
    
    job_code = f"JC{random.randint(1000,9999)}"
    employment_type = random.choice(employment_types)
    termination_type = random.choice(termination_types) if terminated else None
    
    employment_data.append((
        emp_id, job_title, department, business_unit, manager_id,
        job_code, employment_type, hire_date, termination_date, employment_status, termination_type
    ))
    
    # Generate Compensation details based on job title salary range in INR
    salary_min, salary_max = salary_ranges.get(job_title, (30000, 60000))
    base_salary = round(random.uniform(salary_min, salary_max), 2)
    currency = "INR"
    salary_frequency = "Monthly"
    last_salary_change = fake.date_between(start_date=hire_date, end_date=today)
    bonus_eligibility = True if employment_type == "Full-time" and random.random() < 0.7 else False
    variable_pay = round(base_salary * random.uniform(0.05, 0.15), 2)
    stock_options = random.randint(100, 1000) if job_title in ["Manager", "Director"] else 0
    
    compensation_data.append((
        emp_id, base_salary, currency, salary_frequency, last_salary_change,
        bonus_eligibility, variable_pay, stock_options
    ))
    
    # Generate Performance details
    performance_year = random.choice(range(hire_date.year, today.year + 1)) if hire_date.year < today.year else today.year
    years_of_service = today.year - hire_date.year
    if years_of_service < 2:
        rating_weights = [0.4, 0.3, 0.2, 0.07, 0.03]
    elif years_of_service < 5:
        rating_weights = [0.2, 0.3, 0.3, 0.15, 0.05]
    else:
        rating_weights = [0.1, 0.2, 0.3, 0.25, 0.15]
    performance_rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights, k=1)[0]
    
    manager_feedback = fake.text(max_nb_chars=200)
    trainings = random.sample(
        ["Time Management", "Leadership", "Communication", "Advanced Python", "Data Analysis", "Project Management"],
        k=random.randint(1, 3)
    )
    training_completed = ", ".join(trainings)
    skills = random.sample(
        ["Python", "SQL", "Communication", "Leadership", "Problem Solving", "Data Analysis", "Project Management"],
        k=random.randint(1, 3)
    )
    skills_developed = ", ".join(skills)
    promotion_indicator = True if performance_rating >= 4 and years_of_service > 1 and random.random() < 0.2 else False
    
    performance_data.append((
        emp_id, performance_year, performance_rating, manager_feedback,
        training_completed, skills_developed, promotion_indicator
    ))

# ------------------------------------------------------------
# 5. Bulk Insert Data into EmploymentDetails, Compensation, and Performance
# ------------------------------------------------------------
employment_insert_sql = """
INSERT INTO EmploymentDetails 
(EmployeeID, JobTitle, Department, BusinessUnit, ManagerID, JobCode, EmploymentType, HireDate, TerminationDate, EmploymentStatus, TerminationType)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
cur.executemany(employment_insert_sql, employment_data)

compensation_insert_sql = """
INSERT INTO Compensation 
(EmployeeID, BaseSalary, Currency, SalaryFrequency, LastSalaryChange, BonusEligibility, VariablePay, StockOptions)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""
cur.executemany(compensation_insert_sql, compensation_data)

performance_insert_sql = """
INSERT INTO Performance 
(EmployeeID, PerformanceYear, PerformanceRating, ManagerFeedback, TrainingCompleted, SkillsDeveloped, PromotionIndicator)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""
cur.executemany(performance_insert_sql, performance_data)

conn.commit()
cur.close()
conn.close()

print("Existing data deleted and new consistent, Indian-style data for 10,000 employees inserted successfully!")
