import os
import uuid
import logging
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel, Field

# -----------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exitManagementAPI")

# -----------------------------------------------------------------
# JWT Configuration
# -----------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(encoded_jwt, bytes):
        return encoded_jwt.decode("utf-8")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------------------------------------------
# MySQL Connection to ExitManagementDB
# -----------------------------------------------------------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_EXIT_DB = os.getenv("MYSQL_EXITMANAGEMENT_DATABASE")
MYSQL_AUTH_PLUGIN = os.getenv("MYSQL_AUTH_PLUGIN")

exit_conn = None

def get_exit_connection():
    global exit_conn
    if exit_conn is None or not exit_conn.is_connected():
        try:
            exit_conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_EXIT_DB,
                auth_plugin=MYSQL_AUTH_PLUGIN
            )
        except Error as err:
            logger.error(f"Error connecting to ExitManagementDB: {err}")
            raise HTTPException(status_code=500, detail=f"Error connecting to ExitManagementDB: {err}")
    return exit_conn

def get_exit_cursor():
    conn = get_exit_connection()
    return conn.cursor(dictionary=True)

# -----------------------------------------------------------------
# Pydantic Models (Field names exactly match DB columns)
# -----------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class ResignationRequest(BaseModel):
    RequestID: Optional[UUID] = None
    EmployeeID: int
    NoticeDate: date
    EffectiveDate: date
    Reason: str
    Status: str
    ApprovedBy: Optional[int] = None
    Comments: str
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True

class ExitInterview(BaseModel):
    InterviewID: Optional[UUID] = None
    EmployeeID: int
    Interviewer: str
    ReasonForExit: str
    Feedback: str
    InterviewDate: date
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True

class ExitChecklist(BaseModel):
    ChecklistID: Optional[UUID] = None
    EmployeeID: int
    TaskCompleted: bool
    TaskDescription: str
    CompletionDate: Optional[date] = None
    Comments: str
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True

class ExitSurvey(BaseModel):
    SurveyID: Optional[UUID] = None
    EmployeeID: int
    SurveyDate: date
    QuestionsAnswers: str
    OverallSatisfaction: int
    Comments: str
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True

# -----------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------
app = FastAPI(title="Exit Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------
# Startup & Shutdown Events
# -----------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    get_exit_connection()

@app.on_event("shutdown")
def shutdown_event():
    global exit_conn
    logger.info("Application shutting down")
    if exit_conn and exit_conn.is_connected():
        exit_conn.close()

# -----------------------------------------------------------------
# Database Helper Functions using MySQL
# -----------------------------------------------------------------
def fetch_all(query: str, params: tuple = ()):
    try:
        cursor = get_exit_cursor()
        logger.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchall()
        logger.info(f"Query returned {len(result)} rows")
        cursor.close()
        return result
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

def execute_query(query: str, params: tuple):
    try:
        cursor = get_exit_cursor()
        logger.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        get_exit_connection().commit()
        cursor.close()
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}", exc_info=True)
        get_exit_connection().rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

# -----------------------------------------------------------------
# Authentication Endpoint (/token)
# -----------------------------------------------------------------
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    fake_users_db = {"admin": "password"}
    if form_data.username not in fake_users_db or fake_users_db[form_data.username] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------------------------------------------------------
# ResignationRequests Endpoints
# -----------------------------------------------------------------
@app.get("/resignation_requests", response_model=List[ResignationRequest])
async def get_resignation_requests(current_user: str = Depends(get_current_user)):
    rows = fetch_all("SELECT * FROM ResignationRequests", ())
    return rows

@app.post("/resignation_requests", response_model=ResignationRequest, status_code=status.HTTP_201_CREATED)
async def create_resignation_request(request: ResignationRequest, current_user: str = Depends(get_current_user)):
    request_id = request.RequestID or uuid.uuid4()
    if not request.CreatedAt:
        request.CreatedAt = datetime.utcnow()
    execute_query(
        """
        INSERT INTO ResignationRequests (
            RequestID, EmployeeID, NoticeDate, EffectiveDate, Reason, Status, ApprovedBy, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(request_id), request.EmployeeID, request.NoticeDate, request.EffectiveDate,
            request.Reason, request.Status, request.ApprovedBy, request.Comments, request.CreatedAt
        )
    )
    request.RequestID = request_id
    return request

# -----------------------------------------------------------------
# ExitInterviews Endpoints
# -----------------------------------------------------------------
@app.get("/exit_interviews", response_model=List[ExitInterview])
async def get_exit_interviews(current_user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitInterviews", ())

@app.post("/exit_interviews", response_model=ExitInterview, status_code=status.HTTP_201_CREATED)
async def create_exit_interview(interview: ExitInterview, current_user: str = Depends(get_current_user)):
    interview_id = interview.InterviewID or uuid.uuid4()
    if not interview.CreatedAt:
        interview.CreatedAt = datetime.utcnow()
    execute_query(
        """
        INSERT INTO ExitInterviews (
            InterviewID, EmployeeID, Interviewer, ReasonForExit, Feedback, InterviewDate, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(interview_id), interview.EmployeeID, interview.Interviewer, interview.ReasonForExit,
            interview.Feedback, interview.InterviewDate, interview.CreatedAt
        )
    )
    interview.InterviewID = interview_id
    return interview

# -----------------------------------------------------------------
# ExitChecklists Endpoints
# -----------------------------------------------------------------
@app.get("/exit_checklists", response_model=List[ExitChecklist])
async def get_exit_checklists(current_user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitChecklists", ())

@app.post("/exit_checklists", response_model=ExitChecklist, status_code=status.HTTP_201_CREATED)
async def create_exit_checklist(checklist: ExitChecklist, current_user: str = Depends(get_current_user)):
    checklist_id = checklist.ChecklistID or uuid.uuid4()
    if not checklist.CreatedAt:
        checklist.CreatedAt = datetime.utcnow()
    execute_query(
        """
        INSERT INTO ExitChecklists (
            ChecklistID, EmployeeID, TaskCompleted, TaskDescription, CompletionDate, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(checklist_id), checklist.EmployeeID, checklist.TaskCompleted, checklist.TaskDescription,
            checklist.CompletionDate, checklist.Comments, checklist.CreatedAt
        )
    )
    checklist.ChecklistID = checklist_id
    return checklist

# -----------------------------------------------------------------
# ExitSurveys Endpoints
# -----------------------------------------------------------------
@app.get("/exit_surveys", response_model=List[ExitSurvey])
async def get_exit_surveys(current_user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitSurveys", ())

@app.post("/exit_surveys", response_model=ExitSurvey, status_code=status.HTTP_201_CREATED)
async def create_exit_survey(survey: ExitSurvey, current_user: str = Depends(get_current_user)):
    survey_id = survey.SurveyID or uuid.uuid4()
    if not survey.CreatedAt:
        survey.CreatedAt = datetime.utcnow()
    execute_query(
        """
        INSERT INTO ExitSurveys (
            SurveyID, EmployeeID, SurveyDate, QuestionsAnswers, OverallSatisfaction, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(survey_id), survey.EmployeeID, survey.SurveyDate, survey.QuestionsAnswers,
            survey.OverallSatisfaction, survey.Comments, survey.CreatedAt
        )
    )
    survey.SurveyID = survey_id
    return survey
