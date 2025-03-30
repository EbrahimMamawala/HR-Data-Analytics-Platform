import os
import mysql.connector
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
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
# Global MySQL Connection Setup (SuccessFactorsDB)
# -----------------------------------------------------------------
DB_NAME = os.getenv("MYSQL_SUCCESSFACTORS_DATABASE")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_AUTH_PLUGIN = os.getenv("MYSQL_AUTH_PLUGIN")  # e.g., mysql_native_password

try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        auth_plugin=DB_AUTH_PLUGIN  # Adjust if needed
    )
    # Ensure autocommit is enabled for immediate visibility
    conn.autocommit = True
except Exception as e:
    raise Exception(f"Error connecting to database: {e}")

# -----------------------------------------------------------------
# FastAPI Application Initialization
# -----------------------------------------------------------------
app = FastAPI(title="SuccessFactors API")

# -----------------------------------------------------------------
# Pydantic Models
# -----------------------------------------------------------------
class EmployeeBase(BaseModel):
    EmployeeNumber: str
    FirstName: str
    LastName: str
    MiddleName: Optional[str] = None
    PreferredName: str
    Gender: str
    DateOfBirth: date
    Nationality: str
    MaritalStatus: str
    Email: str
    ContactNumber: str
    Address: str
    PhotoURL: str

class Employee(EmployeeBase):
    EmployeeID: int
    CreatedAt: datetime
    UpdatedAt: datetime

class EmploymentDetails(BaseModel):
    EmployeeID: int
    JobTitle: str
    Department: Optional[str] = None
    BusinessUnit: Optional[str] = None
    ManagerID: Optional[int] = None
    JobCode: Optional[str] = None
    EmploymentType: Optional[str] = None
    HireDate: date
    TerminationDate: Optional[date] = None
    EmploymentStatus: str

class Compensation(BaseModel):
    EmployeeID: int
    BaseSalary: float
    Currency: str
    SalaryFrequency: str
    LastSalaryChange: date
    BonusEligibility: bool
    VariablePay: float
    StockOptions: int

class Performance(BaseModel):
    EmployeeID: int
    PerformanceYear: int
    PerformanceRating: int
    ManagerFeedback: Optional[str] = None
    TrainingCompleted: Optional[str] = None
    SkillsDeveloped: Optional[str] = None
    PromotionIndicator: bool

# -----------------------------------------------------------------
# Authentication Endpoint
# -----------------------------------------------------------------
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In production, replace this with proper user authentication
    fake_users_db = {os.getenv("ADMIN_USERNAME"): os.getenv("ADMIN_PASSWORD")}
    if form_data.username in fake_users_db and fake_users_db[form_data.username] == form_data.password:
        access_token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# -----------------------------------------------------------------
# Employee Endpoints
# -----------------------------------------------------------------
@app.get("/employees", response_model=List[Employee])
def get_employees(user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM Employee;")
        employees = cur.fetchall()
        cur.close()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM Employee WHERE EmployeeID = %s;", (employee_id,))
        employee = cur.fetchone()
        cur.close()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/employees", response_model=Employee)
def create_employee(emp: EmployeeBase, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        insert_sql = """
            INSERT INTO Employee 
            (EmployeeNumber, FirstName, LastName, MiddleName, PreferredName, Gender, DateOfBirth, Nationality, MaritalStatus, Email, ContactNumber, Address, PhotoURL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_sql, (
            emp.EmployeeNumber, emp.FirstName, emp.LastName, emp.MiddleName, emp.PreferredName,
            emp.Gender, emp.DateOfBirth, emp.Nationality, emp.MaritalStatus, emp.Email,
            emp.ContactNumber, emp.Address, emp.PhotoURL
        ))
        new_employee_id = cur.lastrowid
        conn.commit()
        cur.execute("SELECT * FROM Employee WHERE EmployeeID = %s;", (new_employee_id,))
        new_employee = cur.fetchone()
        cur.close()
        return new_employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# EmploymentDetails Endpoints
# -----------------------------------------------------------------
@app.get("/employment_details/{employee_id}", response_model=EmploymentDetails)
def get_employment_details(employee_id: int, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM EmploymentDetails WHERE EmployeeID = %s;", (employee_id,))
        details = cur.fetchone()
        cur.close()
        if not details:
            raise HTTPException(status_code=404, detail="Employment details not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/employment_details", response_model=EmploymentDetails)
def create_employment_details(details: EmploymentDetails, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        insert_sql = """
            INSERT INTO EmploymentDetails 
            (EmployeeID, JobTitle, Department, BusinessUnit, ManagerID, JobCode, EmploymentType, HireDate, TerminationDate, EmploymentStatus)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_sql, (
            details.EmployeeID, details.JobTitle, details.Department, details.BusinessUnit, details.ManagerID,
            details.JobCode, details.EmploymentType, details.HireDate, details.TerminationDate, details.EmploymentStatus
        ))
        conn.commit()
        cur.execute("SELECT * FROM EmploymentDetails WHERE EmployeeID = %s;", (details.EmployeeID,))
        new_details = cur.fetchone()
        cur.close()
        return new_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# Compensation Endpoints
# -----------------------------------------------------------------
@app.get("/compensation/{employee_id}", response_model=Compensation)
def get_compensation(employee_id: int, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM Compensation WHERE EmployeeID = %s;", (employee_id,))
        comp = cur.fetchone()
        cur.close()
        if not comp:
            raise HTTPException(status_code=404, detail="Compensation details not found")
        return comp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compensation", response_model=Compensation)
def create_compensation(comp: Compensation, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        insert_sql = """
            INSERT INTO Compensation 
            (EmployeeID, BaseSalary, Currency, SalaryFrequency, LastSalaryChange, BonusEligibility, VariablePay, StockOptions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_sql, (
            comp.EmployeeID, comp.BaseSalary, comp.Currency, comp.SalaryFrequency,
            comp.LastSalaryChange, comp.BonusEligibility, comp.VariablePay, comp.StockOptions
        ))
        conn.commit()
        cur.execute("SELECT * FROM Compensation WHERE EmployeeID = %s;", (comp.EmployeeID,))
        new_comp = cur.fetchone()
        cur.close()
        return new_comp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# Performance Endpoints
# -----------------------------------------------------------------
@app.get("/performance/{employee_id}/{year}", response_model=Performance)
def get_performance(employee_id: int, year: int, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM Performance WHERE EmployeeID = %s AND PerformanceYear = %s;",
            (employee_id, year)
        )
        perf = cur.fetchone()
        cur.close()
        if not perf:
            raise HTTPException(status_code=404, detail="Performance record not found")
        return perf
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/performance", response_model=Performance)
def create_performance(perf: Performance, user: str = Depends(get_current_user)):
    try:
        cur = conn.cursor(dictionary=True)
        insert_sql = """
            INSERT INTO Performance 
            (EmployeeID, PerformanceYear, PerformanceRating, ManagerFeedback, TrainingCompleted, SkillsDeveloped, PromotionIndicator)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_sql, (
            perf.EmployeeID, perf.PerformanceYear, perf.PerformanceRating, perf.ManagerFeedback,
            perf.TrainingCompleted, perf.SkillsDeveloped, perf.PromotionIndicator
        ))
        conn.commit()
        cur.execute("SELECT * FROM Performance WHERE EmployeeID = %s AND PerformanceYear = %s;", (perf.EmployeeID, perf.PerformanceYear))
        new_perf = cur.fetchone()
        cur.close()
        return new_perf
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# Application Shutdown Handler
# -----------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    if conn:
        conn.close()

# -----------------------------------------------------------------
# Running the Application
# -----------------------------------------------------------------
# Save this file (e.g., as main.py) and run with:
# uvicorn main:app --reload
