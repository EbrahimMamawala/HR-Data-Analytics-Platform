import os
import uuid
import json
import random
import datetime
import psycopg2
from cassandra.cluster import Cluster
from faker import Faker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------
# 1. Connect to Postgres (SuccessFactorsDB) to fetch Terminated Employees
# -----------------------------------------------------------------
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

pg_conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
)
pg_cur = pg_conn.cursor()

# Fetch employees who are terminated (with a non-null TerminationDate)
pg_cur.execute("""
    SELECT E.EmployeeID, ED.TerminationDate
    FROM EmploymentDetails ED
    JOIN Employee E ON E.EmployeeID = ED.EmployeeID
    WHERE ED.EmploymentStatus = 'Terminated'
      AND ED.TerminationDate IS NOT NULL
""")
terminated_rows = pg_cur.fetchall()
pg_cur.close()
pg_conn.close()

terminated_employees = []
for row in terminated_rows:
    emp_id, term_date = row
    terminated_employees.append({
        "EmployeeID": emp_id,
        "TerminationDate": term_date
    })

if not terminated_employees:
    print("No terminated employees found in SuccessFactorsDB. Exiting.")
    exit(0)

print(f"Found {len(terminated_employees)} terminated employees in SuccessFactorsDB.")

# -----------------------------------------------------------------
# 2. Connect to Cassandra and Create Keyspace + Tables
# -----------------------------------------------------------------
# Load Cassandra connection settings from environment variables
cassandra_hosts = os.getenv("CASSANDRA_HOSTS").split(",")
cassandra_port = int(os.getenv("CASSANDRA_PORT"))

cluster = Cluster(cassandra_hosts, port=cassandra_port)
session = cluster.connect()

# Create Keyspace (simple replication strategy for local testing)
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS ExitManagementDB
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
""")

# Switch to the new keyspace
session.set_keyspace("exitmanagementdb")

# Drop tables if you want a clean slate (optional)
session.execute("DROP TABLE IF EXISTS ResignationRequests;")
session.execute("DROP TABLE IF EXISTS ExitInterviews;")
session.execute("DROP TABLE IF EXISTS ExitChecklists;")
session.execute("DROP TABLE IF EXISTS ExitSurveys;")

# Create tables in Cassandra
session.execute("""
    CREATE TABLE IF NOT EXISTS ResignationRequests (
        RequestID uuid PRIMARY KEY,
        EmployeeID int,
        NoticeDate date,
        EffectiveDate date,
        Reason text,
        Status text,
        ApprovedBy int,
        Comments text,
        CreatedAt timestamp
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS ExitInterviews (
        InterviewID uuid PRIMARY KEY,
        EmployeeID int,
        Interviewer text,
        ReasonForExit text,
        Feedback text,
        InterviewDate date,
        CreatedAt timestamp
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS ExitChecklists (
        ChecklistID uuid PRIMARY KEY,
        EmployeeID int,
        TaskCompleted boolean,
        TaskDescription text,
        CompletionDate date,
        Comments text,
        CreatedAt timestamp
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS ExitSurveys (
        SurveyID uuid PRIMARY KEY,
        EmployeeID int,
        SurveyDate date,
        QuestionsAnswers text,
        OverallSatisfaction int,
        Comments text,
        CreatedAt timestamp
    );
""")

print("Created keyspace and tables in Cassandra.")

# -----------------------------------------------------------------
# 3. Generate and Insert Data for Each Terminated Employee
# -----------------------------------------------------------------
fake = Faker()
now = datetime.datetime.now()

# Helper: pick a random manager from the same set of employees (for demonstration)
def random_manager_id():
    return random.choice(terminated_employees)["EmployeeID"]

resignation_insert_cql = session.prepare("""
    INSERT INTO ResignationRequests (
        RequestID, EmployeeID, NoticeDate, EffectiveDate, Reason, Status, ApprovedBy, Comments, CreatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

exitinterview_insert_cql = session.prepare("""
    INSERT INTO ExitInterviews (
        InterviewID, EmployeeID, Interviewer, ReasonForExit, Feedback, InterviewDate, CreatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""")

exitchecklist_insert_cql = session.prepare("""
    INSERT INTO ExitChecklists (
        ChecklistID, EmployeeID, TaskCompleted, TaskDescription, CompletionDate, Comments, CreatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""")

exitsurvey_insert_cql = session.prepare("""
    INSERT INTO ExitSurveys (
        SurveyID, EmployeeID, SurveyDate, QuestionsAnswers, OverallSatisfaction, Comments, CreatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""")

# Sample data for resignation reasons and statuses
resignation_reasons = [
    "Personal reasons",
    "Relocation",
    "Better career opportunity",
    "Work-life balance",
    "Health issues"
]
resignation_statuses = ["Pending", "Approved", "Rejected"]

# Sample exit tasks
exit_tasks = [
    "Return company laptop",
    "Submit ID card",
    "Clear desk and personal belongings",
    "Handover pending work"
]

for term_emp in terminated_employees:
    emp_id = term_emp["EmployeeID"]
    termination_date = term_emp["TerminationDate"]
    
    # 3A. ResignationRequests
    if termination_date is not None:
        notice_days_before = random.randint(15, 30)
        notice_date = termination_date - datetime.timedelta(days=notice_days_before)
        effective_date = termination_date
    else:
        notice_date = fake.date_between(start_date="-60d", end_date="today")
        effective_date = notice_date + datetime.timedelta(days=random.randint(15, 30))

    reason = random.choice(resignation_reasons)
    status = random.choice(resignation_statuses)
    approved_by = random_manager_id() if status == "Approved" else None
    comments = fake.sentence(nb_words=8)

    session.execute(resignation_insert_cql, [
        uuid.uuid4(),            # RequestID
        emp_id,                  # EmployeeID
        notice_date,             # NoticeDate (date)
        effective_date,          # EffectiveDate (date)
        reason,                  # Reason (text)
        status,                  # Status (text)
        approved_by,             # ApprovedBy (int)
        comments,                # Comments (text)
        now                      # CreatedAt (timestamp)
    ])

    # 3B. ExitInterviews
    if termination_date is not None:
        interview_date = termination_date - datetime.timedelta(days=5)
    else:
        interview_date = fake.date_between(start_date="-30d", end_date="today")

    interviewer = fake.name()
    feedback = fake.paragraph(nb_sentences=2)
    session.execute(exitinterview_insert_cql, [
        uuid.uuid4(),           # InterviewID
        emp_id,                 # EmployeeID
        interviewer,            # Interviewer (text)
        reason,                 # ReasonForExit (text)
        feedback,               # Feedback (text)
        interview_date,         # InterviewDate (date)
        now                     # CreatedAt (timestamp)
    ])

    # 3C. ExitChecklists
    tasks_for_employee = random.sample(exit_tasks, k=random.randint(1, 2))
    for task in tasks_for_employee:
        completed = random.random() < 0.7
        completion_date = interview_date if completed else None
        comments = fake.sentence(nb_words=6)
        session.execute(exitchecklist_insert_cql, [
            uuid.uuid4(),       # ChecklistID
            emp_id,             # EmployeeID
            completed,          # TaskCompleted (boolean)
            task,               # TaskDescription (text)
            completion_date,    # CompletionDate (date or None)
            comments,           # Comments (text)
            now                 # CreatedAt (timestamp)
        ])

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
    questions_answers = {
        "questions": qa_sample,
        "answers": answers
    }
    overall_satisfaction = random.randint(1, 5)
    survey_comments = fake.paragraph(nb_sentences=1)
    survey_date = termination_date or fake.date_between(start_date="-30d", end_date="today")

    session.execute(exitsurvey_insert_cql, [
        uuid.uuid4(),                     # SurveyID
        emp_id,                           # EmployeeID
        survey_date,                      # SurveyDate (date)
        json.dumps(questions_answers),    # QuestionsAnswers (text as JSON)
        overall_satisfaction,             # OverallSatisfaction (int)
        survey_comments,                  # Comments (text)
        now                               # CreatedAt (timestamp)
    ])

print("Data inserted successfully into ExitManagementDB in Cassandra!")

# -----------------------------------------------------------------
# 4. Cleanup
# -----------------------------------------------------------------
session.shutdown()
cluster.shutdown()
print("Cassandra session closed.")
