import os
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime, timedelta
import jwt
from jwt import PyJWTError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------
# JWT Configuration
# -----------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user: str = payload.get("sub")
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------------------------------------------
# Global MySQL Connection Setup
# -----------------------------------------------------------------
try:
    mysql_conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_TIMEATTENDANCE_DATABASE"),
        auth_plugin=os.getenv("MYSQL_AUTH_PLUGIN")
    )
    if not mysql_conn.is_connected():
        raise Exception("Failed to connect to MySQL")
except Error as e:
    raise Exception(f"MySQL connection error: {e}")

app = FastAPI(title="Time and Attendance API")

# -----------------------------------------------------------------
# Pydantic Models
# -----------------------------------------------------------------
class AttendanceRecord(BaseModel):
    RecordID: Optional[int] = None
    EmployeeID: int
    AttendanceDate: date
    ClockIn: Optional[time] = None
    ClockOut: Optional[time] = None
    BreakDuration: Optional[str] = None  # stored as string in HH:MM:SS format
    LateBy: Optional[str] = None         # HH:MM:SS format
    EarlyBy: Optional[str] = None        # HH:MM:SS format
    Notes: Optional[str] = None
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None

class LeaveRecord(BaseModel):
    LeaveID: Optional[int] = None
    EmployeeID: int
    LeaveType: Optional[str] = None
    StartDate: Optional[date] = None
    EndDate: Optional[date] = None
    TotalDays: Optional[float] = None
    Status: Optional[str] = None
    Reason: Optional[str] = None
    ApprovedBy: Optional[int] = None
    CreatedAt: Optional[datetime] = None

class ShiftSchedule(BaseModel):
    ScheduleID: Optional[int] = None
    EmployeeID: int
    ShiftDate: date
    ScheduledIn: Optional[time] = None
    ScheduledOut: Optional[time] = None
    ShiftType: Optional[str] = None
    CreatedAt: Optional[datetime] = None

class OvertimeRecord(BaseModel):
    OvertimeID: Optional[int] = None
    EmployeeID: int
    OvertimeDate: Optional[date] = None
    OvertimeHours: Optional[float] = None
    ApprovedBy: Optional[int] = None
    CreatedAt: Optional[datetime] = None

# -----------------------------------------------------------------
# Authentication Endpoint
# -----------------------------------------------------------------
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    fake_users_db = {os.getenv("ADMIN_USERNAME"): os.getenv("ADMIN_PASSWORD")}
    if form_data.username in fake_users_db and fake_users_db[form_data.username] == form_data.password:
        access_token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# -----------------------------------------------------------------
# Helper Function to Get a New Cursor
# -----------------------------------------------------------------
def get_cursor():
    try:
        return mysql_conn.cursor(dictionary=True)
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# Helper Functions to Convert Timedelta to Time or String
# -----------------------------------------------------------------
def timedelta_to_time(td: timedelta) -> time:
    total_seconds = int(td.total_seconds())
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)

def timedelta_to_str(td: timedelta) -> str:
    t = timedelta_to_time(td)
    return t.strftime("%H:%M:%S")

def transform_attendance_record(record: dict) -> dict:
    # Convert timedeltas to the expected types
    if isinstance(record.get("ClockIn"), timedelta):
        record["ClockIn"] = timedelta_to_time(record["ClockIn"])
    if isinstance(record.get("ClockOut"), timedelta):
        record["ClockOut"] = timedelta_to_time(record["ClockOut"])
    for field in ["BreakDuration", "LateBy", "EarlyBy"]:
        if isinstance(record.get(field), timedelta):
            record[field] = timedelta_to_str(record[field])
    return record

# -----------------------------------------------------------------
# AttendanceRecords Endpoints
# -----------------------------------------------------------------
@app.get("/attendance", response_model=List[AttendanceRecord])
def get_attendance_records(user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM AttendanceRecords;"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    # Transform each record if needed
    transformed = [transform_attendance_record(r) for r in records]
    return transformed

@app.get("/attendance/{record_id}", response_model=AttendanceRecord)
def get_attendance_record(record_id: int, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM AttendanceRecords WHERE RecordID = %s;"
    cursor.execute(query, (record_id,))
    record = cursor.fetchone()
    cursor.close()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return transform_attendance_record(record)

@app.post("/attendance", response_model=AttendanceRecord)
def create_attendance_record(record: AttendanceRecord, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = """
        INSERT INTO AttendanceRecords
        (EmployeeID, AttendanceDate, ClockIn, ClockOut, BreakDuration, LateBy, EarlyBy, Notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        record.EmployeeID,
        record.AttendanceDate,
        record.ClockIn,
        record.ClockOut,
        record.BreakDuration,
        record.LateBy,
        record.EarlyBy,
        record.Notes
    )
    try:
        cursor.execute(query, values)
        mysql_conn.commit()
        record_id = cursor.lastrowid
        cursor.close()
        return get_attendance_record(record_id, user)
    except Error as e:
        mysql_conn.rollback()
        cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# LeaveRecords Endpoints
# -----------------------------------------------------------------
@app.get("/leave", response_model=List[LeaveRecord])
def get_leave_records(user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM LeaveRecords;"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/leave/{leave_id}", response_model=LeaveRecord)
def get_leave_record(leave_id: int, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM LeaveRecords WHERE LeaveID = %s;"
    cursor.execute(query, (leave_id,))
    record = cursor.fetchone()
    cursor.close()
    if not record:
        raise HTTPException(status_code=404, detail="Leave record not found")
    return record

@app.post("/leave", response_model=LeaveRecord)
def create_leave_record(record: LeaveRecord, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = """
        INSERT INTO LeaveRecords
        (EmployeeID, LeaveType, StartDate, EndDate, TotalDays, Status, Reason, ApprovedBy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        record.EmployeeID,
        record.LeaveType,
        record.StartDate,
        record.EndDate,
        record.TotalDays,
        record.Status,
        record.Reason,
        record.ApprovedBy
    )
    try:
        cursor.execute(query, values)
        mysql_conn.commit()
        leave_id = cursor.lastrowid
        cursor.close()
        return get_leave_record(leave_id, user)
    except Error as e:
        mysql_conn.rollback()
        cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# ShiftSchedules Endpoints
# -----------------------------------------------------------------
@app.get("/shift", response_model=List[ShiftSchedule])
def get_shift_schedules(user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM ShiftSchedules;"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/shift/{schedule_id}", response_model=ShiftSchedule)
def get_shift_schedule(schedule_id: int, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM ShiftSchedules WHERE ScheduleID = %s;"
    cursor.execute(query, (schedule_id,))
    record = cursor.fetchone()
    cursor.close()
    if not record:
        raise HTTPException(status_code=404, detail="Shift schedule not found")
    return record

@app.post("/shift", response_model=ShiftSchedule)
def create_shift_schedule(schedule: ShiftSchedule, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = """
        INSERT INTO ShiftSchedules
        (EmployeeID, ShiftDate, ScheduledIn, ScheduledOut, ShiftType)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        schedule.EmployeeID,
        schedule.ShiftDate,
        schedule.ScheduledIn,
        schedule.ScheduledOut,
        schedule.ShiftType
    )
    try:
        cursor.execute(query, values)
        mysql_conn.commit()
        schedule_id = cursor.lastrowid
        cursor.close()
        return get_shift_schedule(schedule_id, user)
    except Error as e:
        mysql_conn.rollback()
        cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# OvertimeRecords Endpoints
# -----------------------------------------------------------------
@app.get("/overtime", response_model=List[OvertimeRecord])
def get_overtime_records(user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM OvertimeRecords;"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/overtime/{overtime_id}", response_model=OvertimeRecord)
def get_overtime_record(overtime_id: int, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = "SELECT * FROM OvertimeRecords WHERE OvertimeID = %s;"
    cursor.execute(query, (overtime_id,))
    record = cursor.fetchone()
    cursor.close()
    if not record:
        raise HTTPException(status_code=404, detail="Overtime record not found")
    return record

@app.post("/overtime", response_model=OvertimeRecord)
def create_overtime_record(record: OvertimeRecord, user: str = Depends(get_current_user)):
    cursor = get_cursor()
    query = """
        INSERT INTO OvertimeRecords
        (EmployeeID, OvertimeDate, OvertimeHours, ApprovedBy)
        VALUES (%s, %s, %s, %s)
    """
    values = (
        record.EmployeeID,
        record.OvertimeDate,
        record.OvertimeHours,
        record.ApprovedBy
    )
    try:
        cursor.execute(query, values)
        mysql_conn.commit()
        overtime_id = cursor.lastrowid
        cursor.close()
        return get_overtime_record(overtime_id, user)
    except Error as e:
        mysql_conn.rollback()
        cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# Shutdown Handler
# -----------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    if mysql_conn.is_connected():
        mysql_conn.close()

# -----------------------------------------------------------------
# Running the Application
# -----------------------------------------------------------------
# Save this file (e.g., as main.py) and run with:
# uvicorn main:app --reload
