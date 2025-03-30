import os
import psycopg2
import mysql.connector
from faker import Faker
import random
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --------------------------------------------------------------------
# 1. Connect to Postgres (SuccessFactorsDB) to fetch existing employees
# --------------------------------------------------------------------
pg_db = os.getenv("DB_NAME")
pg_user = os.getenv("DB_USER")
pg_password = os.getenv("DB_PASSWORD")
pg_host = os.getenv("DB_HOST")
pg_port = int(os.getenv("PG_PORT"))

pg_conn = psycopg2.connect(
    dbname=pg_db,
    user=pg_user,
    password=pg_password,
    host=pg_host,
    port=pg_port
)
pg_cur = pg_conn.cursor()

# Retrieve all EmployeeIDs from the SuccessFactorsDB
pg_cur.execute("SELECT EmployeeID FROM Employee;")
employee_rows = pg_cur.fetchall()
pg_cur.close()
pg_conn.close()

# Build a list of valid EmployeeIDs
employee_ids = [row[0] for row in employee_rows]
if not employee_ids:
    raise ValueError("No employees found in SuccessFactorsDB. Cannot create consistent data.")

# --------------------------------------------------------------------
# 2. Connect to MySQL (TimeAndAttendanceDB) and create tables
# --------------------------------------------------------------------
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
mysql_auth_plugin = os.getenv("MYSQL_AUTH_PLUGIN")

mysql_conn = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
    auth_plugin=mysql_auth_plugin
)
mysql_cur = mysql_conn.cursor()

# Optional: Drop tables if you want to start clean
tables_to_drop = ["OvertimeRecords", "ShiftSchedules", "LeaveRecords", "AttendanceRecords"]
for tbl in tables_to_drop:
    drop_sql = f"DROP TABLE IF EXISTS {tbl};"
    mysql_cur.execute(drop_sql)

# Create AttendanceRecords table
attendance_table_sql = """
CREATE TABLE IF NOT EXISTS AttendanceRecords (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    AttendanceDate DATE NOT NULL,
    ClockIn TIME,
    ClockOut TIME,
    BreakDuration TIME,
    LateBy TIME,
    EarlyBy TIME,
    Notes TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""
mysql_cur.execute(attendance_table_sql)

# Create LeaveRecords table
leave_table_sql = """
CREATE TABLE IF NOT EXISTS LeaveRecords (
    LeaveID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    LeaveType VARCHAR(50),
    StartDate DATE,
    EndDate DATE,
    TotalDays DECIMAL(5,2),
    Status VARCHAR(10),
    Reason TEXT,
    ApprovedBy INT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""
mysql_cur.execute(leave_table_sql)

# Create ShiftSchedules table
shift_table_sql = """
CREATE TABLE IF NOT EXISTS ShiftSchedules (
    ScheduleID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    ShiftDate DATE NOT NULL,
    ScheduledIn TIME,
    ScheduledOut TIME,
    ShiftType VARCHAR(20),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""
mysql_cur.execute(shift_table_sql)

# Create OvertimeRecords table
overtime_table_sql = """
CREATE TABLE IF NOT EXISTS OvertimeRecords (
    OvertimeID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    OvertimeDate DATE,
    OvertimeHours DECIMAL(5,2),
    ApprovedBy INT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""
mysql_cur.execute(overtime_table_sql)

mysql_conn.commit()

# --------------------------------------------------------------------
# 3. Generate 10,000 rows of data per table
# --------------------------------------------------------------------
fake = Faker()
today = datetime.date.today()

# Helper function to convert an integer number of minutes to a TIME string (HH:MM:SS)
def minutes_to_time_str(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}:00"

# ----------------------------------
# 3A. Generate AttendanceRecords data
# ----------------------------------
attendance_data = []
for _ in range(10000):
    emp_id = random.choice(employee_ids)

    # Random attendance date in the last 180 days
    attendance_date = fake.date_between(start_date="-180d", end_date="today")

    # Random ClockIn between 8:00 and 10:00
    clock_in_hour = random.randint(8, 10)
    clock_in_minute = random.randint(0, 59)
    clock_in = datetime.time(clock_in_hour, clock_in_minute, 0)

    # Random ClockOut between 16:00 and 19:00
    clock_out_hour = random.randint(16, 19)
    clock_out_minute = random.randint(0, 59)
    clock_out = datetime.time(clock_out_hour, clock_out_minute, 0)

    # Random break duration between 30 and 90 minutes
    break_duration_minutes = random.randint(30, 90)
    break_duration_str = minutes_to_time_str(break_duration_minutes)

    # Scheduled times for calculating lateness/earliness
    scheduled_in = datetime.time(9, 0, 0)
    scheduled_out = datetime.time(17, 0, 0)

    # Calculate LateBy (if clock_in is later than scheduled_in)
    in_delta = (clock_in.hour * 60 + clock_in.minute) - (scheduled_in.hour * 60 + scheduled_in.minute)
    late_by_str = minutes_to_time_str(in_delta) if in_delta > 0 else "00:00:00"

    # Calculate EarlyBy (if clock_out is earlier than scheduled_out)
    out_delta = (scheduled_out.hour * 60 + scheduled_out.minute) - (clock_out.hour * 60 + clock_out.minute)
    early_by_str = minutes_to_time_str(out_delta) if out_delta > 0 else "00:00:00"

    notes = fake.sentence(nb_words=8)

    attendance_data.append((
        emp_id,
        attendance_date,
        clock_in,
        clock_out,
        break_duration_str,
        late_by_str,
        early_by_str,
        notes
    ))

attendance_insert_sql = """
INSERT INTO AttendanceRecords
(EmployeeID, AttendanceDate, ClockIn, ClockOut, BreakDuration, LateBy, EarlyBy, Notes)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
mysql_cur.executemany(attendance_insert_sql, attendance_data)
mysql_conn.commit()

# -----------------------------
# 3B. Generate LeaveRecords data
# -----------------------------
leave_types = ["Sick", "Casual", "Earned", "Maternity", "Paternity"]
leave_statuses = ["Pending", "Approved", "Rejected"]
leave_data = []

for _ in range(10000):
    emp_id = random.choice(employee_ids)
    leave_type = random.choice(leave_types)
    start_date = fake.date_between(start_date="-180d", end_date="today")
    days_off = random.randint(1, 10)
    end_date = start_date + datetime.timedelta(days=days_off)
    total_days = float(days_off)
    status = random.choice(leave_statuses)
    reason = fake.sentence(nb_words=10)
    approved_by = random.choice(employee_ids) if status == "Approved" else None

    leave_data.append((
        emp_id,
        leave_type,
        start_date,
        end_date,
        total_days,
        status,
        reason,
        approved_by
    ))

leave_insert_sql = """
INSERT INTO LeaveRecords
(EmployeeID, LeaveType, StartDate, EndDate, TotalDays, Status, Reason, ApprovedBy)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
mysql_cur.executemany(leave_insert_sql, leave_data)
mysql_conn.commit()

# --------------------------------
# 3C. Generate ShiftSchedules data
# --------------------------------
shift_types = ["Morning", "Afternoon", "Night", "General"]
shift_data = []

for _ in range(10000):
    emp_id = random.choice(employee_ids)
    shift_date = fake.date_between(start_date="today", end_date="+30d")
    shift_type = random.choice(shift_types)

    if shift_type == "Morning":
        scheduled_in = datetime.time(6, 0, 0)
        scheduled_out = datetime.time(14, 0, 0)
    elif shift_type == "Afternoon":
        scheduled_in = datetime.time(14, 0, 0)
        scheduled_out = datetime.time(22, 0, 0)
    elif shift_type == "Night":
        scheduled_in = datetime.time(22, 0, 0)
        scheduled_out = datetime.time(6, 0, 0)  # next day
    else:  # General
        scheduled_in = datetime.time(9, 0, 0)
        scheduled_out = datetime.time(17, 0, 0)

    shift_data.append((
        emp_id,
        shift_date,
        scheduled_in,
        scheduled_out,
        shift_type
    ))

shift_insert_sql = """
INSERT INTO ShiftSchedules
(EmployeeID, ShiftDate, ScheduledIn, ScheduledOut, ShiftType)
VALUES (%s, %s, %s, %s, %s)
"""
mysql_cur.executemany(shift_insert_sql, shift_data)
mysql_conn.commit()

# ---------------------------------
# 3D. Generate OvertimeRecords data
# ---------------------------------
overtime_data = []
for _ in range(10000):
    emp_id = random.choice(employee_ids)
    overtime_date = fake.date_between(start_date="-90d", end_date="today")
    overtime_hours = round(random.uniform(0.5, 4.0), 2)
    approved_by = random.choice(employee_ids)

    overtime_data.append((
        emp_id,
        overtime_date,
        overtime_hours,
        approved_by
    ))

overtime_insert_sql = """
INSERT INTO OvertimeRecords
(EmployeeID, OvertimeDate, OvertimeHours, ApprovedBy)
VALUES (%s, %s, %s, %s)
"""
mysql_cur.executemany(overtime_insert_sql, overtime_data)
mysql_conn.commit()

# --------------------------------------------------------------------
# 4. Close MySQL connection
# --------------------------------------------------------------------
mysql_cur.close()
mysql_conn.close()

print("Data generation complete. 10,000 rows inserted into each table in TimeAndAttendanceDB!")
