import os
import uuid
import json
import random
import datetime
from datetime import date, datetime, timedelta  # Ensure this is at the top
import mysql.connector
from faker import Faker
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exitManagementSystemDB")

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------
# 1. Connect to MySQL (SuccessFactorsDB) to fetch Terminated Employees
# -----------------------------------------------------------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_SUCCESSFACTORS_DATABASE = os.getenv("MYSQL_SUCCESSFACTORS_DATABASE")
MYSQL_AUTH_PLUGIN = os.getenv("MYSQL_AUTH_PLUGIN")  # e.g., caching_sha2_password

try:
    sf_conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_SUCCESSFACTORS_DATABASE,
        auth_plugin=MYSQL_AUTH_PLUGIN
    )
except mysql.connector.Error as err:
    raise Exception(f"Error connecting to SuccessFactorsDB: {err}")

sf_cursor = sf_conn.cursor()
sf_cursor.execute("""
    SELECT E.EmployeeID, ED.TerminationDate
    FROM EmploymentDetails ED
    JOIN Employee E ON E.EmployeeID = ED.EmployeeID
    WHERE ED.EmploymentStatus = 'Terminated'
      AND ED.TerminationDate IS NOT NULL
""")
terminated_rows = sf_cursor.fetchall()
sf_cursor.close()
sf_conn.close()

terminated_employees = []
for row in terminated_rows:
    emp_id, term_date = row
    terminated_employees.append({
        "EmployeeID": emp_id,
        "TerminationDate": term_date  # assumed to be a date object
    })

if not terminated_employees:
    logger.info("No terminated employees found in SuccessFactorsDB. Exiting.")
    exit(0)

logger.info(f"Found {len(terminated_employees)} terminated employees in SuccessFactorsDB.")

# -----------------------------------------------------------------
# 2. Connect to MySQL (ExitManagementDB) and Create Tables
# -----------------------------------------------------------------
MYSQL_EXIT_DB = os.getenv("MYSQL_EXITMANAGEMENT_DATABASE")

try:
    # Connect without specifying a database so we can create it if needed
    exit_conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        auth_plugin=MYSQL_AUTH_PLUGIN
    )
    exit_cursor = exit_conn.cursor()
    exit_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_EXIT_DB};")
    exit_conn.commit()
    # Switch to the ExitManagementDB
    exit_conn.database = MYSQL_EXIT_DB
except mysql.connector.Error as err:
    raise Exception(f"Error connecting to ExitManagementDB: {err}")

# Optionally drop existing tables to start fresh
tables = ["ResignationRequests", "ExitInterviews", "ExitChecklists", "ExitSurveys"]
for tbl in tables:
    exit_cursor.execute(f"DROP TABLE IF EXISTS {tbl};")

# Create ResignationRequests table
exit_cursor.execute("""
    CREATE TABLE IF NOT EXISTS ResignationRequests (
        RequestID CHAR(36) PRIMARY KEY,
        EmployeeID INT,
        NoticeDate DATE,
        EffectiveDate DATE,
        Reason TEXT,
        Status VARCHAR(50),
        ApprovedBy INT,
        Comments TEXT,
        CreatedAt DATETIME
    );
""")

# Create ExitInterviews table
exit_cursor.execute("""
    CREATE TABLE IF NOT EXISTS ExitInterviews (
        InterviewID CHAR(36) PRIMARY KEY,
        EmployeeID INT,
        Interviewer VARCHAR(255),
        ReasonForExit TEXT,
        Feedback TEXT,
        InterviewDate DATE,
        CreatedAt DATETIME
    );
""")

# Create ExitChecklists table
exit_cursor.execute("""
    CREATE TABLE IF NOT EXISTS ExitChecklists (
        ChecklistID CHAR(36) PRIMARY KEY,
        EmployeeID INT,
        TaskCompleted BOOLEAN,
        TaskDescription TEXT,
        CompletionDate DATE,
        Comments TEXT,
        CreatedAt DATETIME
    );
""")

# Create ExitSurveys table
exit_cursor.execute("""
    CREATE TABLE IF NOT EXISTS ExitSurveys (
        SurveyID CHAR(36) PRIMARY KEY,
        EmployeeID INT,
        SurveyDate DATE,
        QuestionsAnswers TEXT,
        OverallSatisfaction INT,
        Comments TEXT,
        CreatedAt DATETIME
    );
""")

exit_conn.commit()
logger.info("Created tables in ExitManagementDB.")

# -----------------------------------------------------------------
# 3. Generate and Insert Data for Each Terminated Employee
# -----------------------------------------------------------------
fake = Faker()
now = datetime.utcnow()  # using UTC for consistency

# To simulate realistic exit management data,
# we assume that realistic exit reasons and tasks are used.
resignation_reasons = [
    "Personal reasons",
    "Relocation",
    "Better career opportunity",
    "Work-life balance",
    "Health issues"
]
resignation_statuses = ["Pending", "Approved"]
exit_tasks = [
    "Return company laptop",
    "Submit ID card",
    "Clear desk and personal belongings",
    "Handover pending work"
]

# We now use batches to improve performance.
resignation_batch = []
exit_interview_batch = []
exit_checklist_batch = []
exit_survey_batch = []

progress_interval = 500
total = len(terminated_employees)

logger.info("Starting data generation for exit management records...")

for idx, term_emp in enumerate(terminated_employees, start=1):
    emp_id = term_emp["EmployeeID"]
    termination_date = term_emp["TerminationDate"]
    
    # 3A. ResignationRequests
    if termination_date is not None:
        notice_days_before = random.randint(15, 30)
        notice_date = termination_date - timedelta(days=notice_days_before)
        effective_date = termination_date
    else:
        notice_date = fake.date_between(start_date="-60d", end_date="today")
        effective_date = notice_date + timedelta(days=random.randint(15, 30))
    reason = random.choice(resignation_reasons)
    status_val = random.choice(resignation_statuses)
    approved_by = random.choice(terminated_employees)["EmployeeID"] if status_val == "Approved" else None
    comments = fake.sentence(nb_words=8)
    resignation_id = str(uuid.uuid4())
    resignation_batch.append((
        resignation_id, emp_id, notice_date, effective_date,
        reason, status_val, approved_by, comments, now
    ))
    
    # 3B. ExitInterviews
    if termination_date is not None:
        interview_date = termination_date - timedelta(days=5)
    else:
        interview_date = fake.date_between(start_date="-30d", end_date="today")
    interviewer = fake.name()
    feedback = fake.paragraph(nb_sentences=2)
    interview_id = str(uuid.uuid4())
    exit_interview_batch.append((
        interview_id, emp_id, interviewer, reason,  # using same reason for simplicity
        feedback, interview_date, now
    ))
    
    # 3C. ExitChecklists
    tasks_for_employee = random.sample(exit_tasks, k=random.randint(1, 2))
    for task in tasks_for_employee:
        completed = random.random() < 0.7
        completion_date = interview_date if completed else None
        checklist_id = str(uuid.uuid4())
        checklist_comments = fake.sentence(nb_words=6)
        exit_checklist_batch.append((
            checklist_id, emp_id, completed, task,
            completion_date, checklist_comments, now
        ))
    
    # 3D. ExitSurveys
    qa_sample = {
        "Q1": "How would you rate your overall experience?",
        "Q2": "What did you like most about the company?",
        "Q3": "What could be improved?"
    }
    answers = {
        "Q1": random.choice(["Great", "Good", "Average", "Poor"]),
        "Q2": fake.sentence(nb_words=5),
        "Q3": fake.sentence(nb_words=7)
    }
    questions_answers = json.dumps({"questions": qa_sample, "answers": answers})
    overall_satisfaction = random.randint(1, 5)
    survey_comments = fake.paragraph(nb_sentences=1)
    survey_date = termination_date if termination_date else fake.date_between(start_date="-30d", end_date="today")
    survey_id = str(uuid.uuid4())
    exit_survey_batch.append((
        survey_id, emp_id, survey_date, questions_answers,
        overall_satisfaction, survey_comments, now
    ))
    
    if idx % progress_interval == 0:
        logger.info(f"Processed {idx} / {total} terminated employees.")

# Bulk insert using executemany()
resignation_insert_query = """
INSERT INTO ResignationRequests 
(RequestID, EmployeeID, NoticeDate, EffectiveDate, Reason, Status, ApprovedBy, Comments, CreatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
exit_cursor.executemany(resignation_insert_query, resignation_batch)

exit_interview_insert_query = """
INSERT INTO ExitInterviews 
(InterviewID, EmployeeID, Interviewer, ReasonForExit, Feedback, InterviewDate, CreatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
exit_cursor.executemany(exit_interview_insert_query, exit_interview_batch)

exit_checklist_insert_query = """
INSERT INTO ExitChecklists 
(ChecklistID, EmployeeID, TaskCompleted, TaskDescription, CompletionDate, Comments, CreatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
exit_cursor.executemany(exit_checklist_insert_query, exit_checklist_batch)

exit_survey_insert_query = """
INSERT INTO ExitSurveys 
(SurveyID, EmployeeID, SurveyDate, QuestionsAnswers, OverallSatisfaction, Comments, CreatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
exit_cursor.executemany(exit_survey_insert_query, exit_survey_batch)

exit_conn.commit()
logger.info("Data inserted successfully into ExitManagementDB in MySQL!")

# -----------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------
exit_cursor.close()
exit_conn.close()

logger.info("MySQL connection closed.")
