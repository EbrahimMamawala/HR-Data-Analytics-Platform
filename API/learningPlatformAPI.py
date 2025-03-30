import os
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
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
# MongoDB Connection Setup
# -----------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
DB_NAME = os.getenv("MONGO_DB")
db = client[DB_NAME]

# Collections
courses_collection = db["courses"]
modules_collection = db["modules"]
enrollments_collection = db["enrollments"]
assessments_collection = db["assessments"]
certificates_collection = db["certificates"]

# -----------------------------------------------------------------
# Pydantic Models
# -----------------------------------------------------------------
class Course(BaseModel):
    CourseID: int
    CourseName: str
    Description: str
    Category: str
    Duration: float
    Price: float
    StartDate: datetime
    EndDate: datetime
    CreatedAt: datetime
    UpdatedAt: datetime

class Module(BaseModel):
    ModuleID: int
    CourseID: int
    ModuleName: str
    ModuleDescription: str
    CreatedAt: datetime
    UpdatedAt: datetime

class Enrollment(BaseModel):
    EnrollmentID: int
    EmployeeID: int
    CourseID: int
    EnrollDate: datetime
    Status: str
    CreatedAt: datetime
    UpdatedAt: datetime

class Assessment(BaseModel):
    AssessmentID: int
    EnrollmentID: int
    Title: str
    PassingMarks: float
    CreatedAt: datetime
    UpdatedAt: datetime

class Certificate(BaseModel):
    CertificateID: int
    EnrollmentID: int
    CertificateName: str
    IssuedDate: datetime
    CreatedAt: datetime
    UpdatedAt: datetime

# -----------------------------------------------------------------
# Helper function to remove MongoDB's _id field
# -----------------------------------------------------------------
def serialize_doc(doc):
    if doc.get("_id"):
        del doc["_id"]
    return doc

# -----------------------------------------------------------------
# FastAPI Application Initialization
# -----------------------------------------------------------------
app = FastAPI(title="Learning Platform API")

# -----------------------------------------------------------------
# Authentication Endpoint
# -----------------------------------------------------------------
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    fake_users_db = {os.getenv("ADMIN_USERNAME"): os.getenv("ADMIN_PASSWORD")}
    if form_data.username in fake_users_db and fake_users_db[form_data.username] == form_data.password:
        access_token = create_access_token(
            {"sub": form_data.username},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# -----------------------------------------------------------------
# Courses Endpoints
# -----------------------------------------------------------------
@app.get("/courses", response_model=List[Course])
def get_courses(user: str = Depends(get_current_user)):
    courses = list(courses_collection.find())
    return [serialize_doc(course) for course in courses]

@app.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: int, user: str = Depends(get_current_user)):
    course = courses_collection.find_one({"CourseID": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return serialize_doc(course)

@app.post("/courses", response_model=Course)
def create_course(course: Course, user: str = Depends(get_current_user)):
    if courses_collection.find_one({"CourseID": course.CourseID}):
        raise HTTPException(status_code=400, detail="Course with this CourseID already exists")
    courses_collection.insert_one(course.dict())
    return course

# -----------------------------------------------------------------
# Modules Endpoints
# -----------------------------------------------------------------
@app.get("/modules", response_model=List[Module])
def get_modules(user: str = Depends(get_current_user)):
    modules = list(modules_collection.find())
    return [serialize_doc(module) for module in modules]

@app.get("/modules/{module_id}", response_model=Module)
def get_module(module_id: int, user: str = Depends(get_current_user)):
    module = modules_collection.find_one({"ModuleID": module_id})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return serialize_doc(module)

@app.post("/modules", response_model=Module)
def create_module(module: Module, user: str = Depends(get_current_user)):
    if modules_collection.find_one({"ModuleID": module.ModuleID}):
        raise HTTPException(status_code=400, detail="Module with this ModuleID already exists")
    modules_collection.insert_one(module.dict())
    return module

# -----------------------------------------------------------------
# Enrollments Endpoints
# -----------------------------------------------------------------
@app.get("/enrollments", response_model=List[Enrollment])
def get_enrollments(user: str = Depends(get_current_user)):
    enrollments = list(enrollments_collection.find())
    return [serialize_doc(enrollment) for enrollment in enrollments]

@app.get("/enrollments/{enrollment_id}", response_model=Enrollment)
def get_enrollment(enrollment_id: int, user: str = Depends(get_current_user)):
    enrollment = enrollments_collection.find_one({"EnrollmentID": enrollment_id})
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return serialize_doc(enrollment)

@app.post("/enrollments", response_model=Enrollment)
def create_enrollment(enrollment: Enrollment, user: str = Depends(get_current_user)):
    if enrollments_collection.find_one({"EnrollmentID": enrollment.EnrollmentID}):
        raise HTTPException(status_code=400, detail="Enrollment with this EnrollmentID already exists")
    enrollments_collection.insert_one(enrollment.dict())
    return enrollment

# -----------------------------------------------------------------
# Assessments Endpoints
# -----------------------------------------------------------------
@app.get("/assessments", response_model=List[Assessment])
def get_assessments(user: str = Depends(get_current_user)):
    assessments = list(assessments_collection.find())
    return [serialize_doc(assessment) for assessment in assessments]

@app.get("/assessments/{assessment_id}", response_model=Assessment)
def get_assessment(assessment_id: int, user: str = Depends(get_current_user)):
    assessment = assessments_collection.find_one({"AssessmentID": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return serialize_doc(assessment)

@app.post("/assessments", response_model=Assessment)
def create_assessment(assessment: Assessment, user: str = Depends(get_current_user)):
    if assessments_collection.find_one({"AssessmentID": assessment.AssessmentID}):
        raise HTTPException(status_code=400, detail="Assessment with this AssessmentID already exists")
    assessments_collection.insert_one(assessment.dict())
    return assessment

# -----------------------------------------------------------------
# Certificates Endpoints
# -----------------------------------------------------------------
@app.get("/certificates", response_model=List[Certificate])
def get_certificates(user: str = Depends(get_current_user)):
    certificates = list(certificates_collection.find())
    return [serialize_doc(certificate) for certificate in certificates]

@app.get("/certificates/{certificate_id}", response_model=Certificate)
def get_certificate(certificate_id: int, user: str = Depends(get_current_user)):
    certificate = certificates_collection.find_one({"CertificateID": certificate_id})
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return serialize_doc(certificate)

@app.post("/certificates", response_model=Certificate)
def create_certificate(certificate: Certificate, user: str = Depends(get_current_user)):
    if certificates_collection.find_one({"CertificateID": certificate.CertificateID}):
        raise HTTPException(status_code=400, detail="Certificate with this CertificateID already exists")
    certificates_collection.insert_one(certificate.dict())
    return certificate

# -----------------------------------------------------------------
# Run the FastAPI Application
# -----------------------------------------------------------------
# Save this file (e.g., as main.py) and run with:
# uvicorn main:app --reload
