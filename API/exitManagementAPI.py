import os
import uuid
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from pydantic import BaseModel

# -----------------------------------------------------------------
# JWT Configuration
# -----------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------------------------------------------
# Cassandra Connection
# -----------------------------------------------------------------
try:
    cassandra_host = os.getenv("CASSANDRA_HOST")
    cassandra_port = int(os.getenv("CASSANDRA_PORT"))
    cluster = Cluster([cassandra_host], port=cassandra_port)
    session = cluster.connect()
    session.row_factory = dict_factory
    session.set_keyspace(os.getenv("CASSANDRA_KEYSPACE"))
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# -----------------------------------------------------------------
# Pydantic Models
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
    CreatedAt: datetime

class ExitInterview(BaseModel):
    InterviewID: Optional[UUID] = None
    EmployeeID: int
    Interviewer: str
    ReasonForExit: str
    Feedback: str
    InterviewDate: date
    CreatedAt: datetime

class ExitChecklist(BaseModel):
    ChecklistID: Optional[UUID] = None
    EmployeeID: int
    TaskCompleted: bool
    TaskDescription: str
    CompletionDate: Optional[date] = None
    Comments: str
    CreatedAt: datetime

class ExitSurvey(BaseModel):
    SurveyID: Optional[UUID] = None
    EmployeeID: int
    SurveyDate: date
    QuestionsAnswers: str
    OverallSatisfaction: int
    Comments: str
    CreatedAt: datetime

# -----------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------
app = FastAPI(title="Exit Management API")

# -----------------------------------------------------------------
# Authentication Endpoints
# -----------------------------------------------------------------
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    fake_users_db = {"admin": "password"}
    if form_data.username in fake_users_db and fake_users_db[form_data.username] == form_data.password:
        access_token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# -----------------------------------------------------------------
# Database Helper Functions
# -----------------------------------------------------------------
def fetch_all(query: str, params: tuple = ()):
    try:
        rows = session.execute(query, params)
        return list(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def execute_query(query: str, params: tuple):
    try:
        session.execute(query, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------
# ResignationRequests Endpoints
# -----------------------------------------------------------------
@app.get("/resignation_requests", response_model=List[ResignationRequest])
def get_resignation_requests(user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ResignationRequests;")

@app.post("/resignation_requests", response_model=ResignationRequest)
def create_resignation_request(request: ResignationRequest, user: str = Depends(get_current_user)):
    request_id = request.RequestID or uuid.uuid4()
    execute_query("""
        INSERT INTO ResignationRequests (
            RequestID, EmployeeID, NoticeDate, EffectiveDate, Reason, Status, ApprovedBy, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request_id, request.EmployeeID, request.NoticeDate, request.EffectiveDate,
        request.Reason, request.Status, request.ApprovedBy, request.Comments, request.CreatedAt
    ))
    request.RequestID = request_id
    return request

# -----------------------------------------------------------------
# ExitInterviews Endpoints
# -----------------------------------------------------------------
@app.get("/exit_interviews", response_model=List[ExitInterview])
def get_exit_interviews(user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitInterviews;")

@app.post("/exit_interviews", response_model=ExitInterview)
def create_exit_interview(interview: ExitInterview, user: str = Depends(get_current_user)):
    interview_id = interview.InterviewID or uuid.uuid4()
    execute_query("""
        INSERT INTO ExitInterviews (
            InterviewID, EmployeeID, Interviewer, ReasonForExit, Feedback, InterviewDate, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        interview_id, interview.EmployeeID, interview.Interviewer, interview.ReasonForExit,
        interview.Feedback, interview.InterviewDate, interview.CreatedAt
    ))
    interview.InterviewID = interview_id
    return interview

# -----------------------------------------------------------------
# ExitChecklists Endpoints
# -----------------------------------------------------------------
@app.get("/exit_checklists", response_model=List[ExitChecklist])
def get_exit_checklists(user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitChecklists;")

@app.post("/exit_checklists", response_model=ExitChecklist)
def create_exit_checklist(checklist: ExitChecklist, user: str = Depends(get_current_user)):
    checklist_id = checklist.ChecklistID or uuid.uuid4()
    execute_query("""
        INSERT INTO ExitChecklists (
            ChecklistID, EmployeeID, TaskCompleted, TaskDescription, CompletionDate, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        checklist_id, checklist.EmployeeID, checklist.TaskCompleted,
        checklist.TaskDescription, checklist.CompletionDate, checklist.Comments, checklist.CreatedAt
    ))
    checklist.ChecklistID = checklist_id
    return checklist

# -----------------------------------------------------------------
# ExitSurveys Endpoints
# -----------------------------------------------------------------
@app.get("/exit_surveys", response_model=List[ExitSurvey])
def get_exit_surveys(user: str = Depends(get_current_user)):
    return fetch_all("SELECT * FROM ExitSurveys;")

@app.post("/exit_surveys", response_model=ExitSurvey)
def create_exit_survey(survey: ExitSurvey, user: str = Depends(get_current_user)):
    survey_id = survey.SurveyID or uuid.uuid4()
    execute_query("""
        INSERT INTO ExitSurveys (
            SurveyID, EmployeeID, SurveyDate, QuestionsAnswers, OverallSatisfaction, Comments, CreatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        survey_id, survey.EmployeeID, survey.SurveyDate, survey.QuestionsAnswers,
        survey.OverallSatisfaction, survey.Comments, survey.CreatedAt
    ))
    survey.SurveyID = survey_id
    return survey

# -----------------------------------------------------------------
# Shutdown Event Handler
# -----------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    session.shutdown()
    cluster.shutdown()
