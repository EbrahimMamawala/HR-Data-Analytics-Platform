import os
import uuid
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    CASSANDRA_HOST = os.getenv("CASSANDRA_HOST")
    CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT"))
    KEYSPACE = os.getenv("CASSANDRA_KEYSPACE")
    
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = cluster.connect()
    session.row_factory = dict_factory
    session.set_keyspace(KEYSPACE)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# -----------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------
app = FastAPI(title="Exit Management API")

# -----------------------------------------------------------------
# Authentication Endpoints
# -----------------------------------------------------------------
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    fake_users_db = {os.getenv("ADMIN_USERNAME"): os.getenv("ADMIN_PASSWORD")}
    if form_data.username in fake_users_db and fake_users_db[form_data.username] == form_data.password:
        access_token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# -----------------------------------------------------------------
# Shutdown Event Handler
# -----------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    session.shutdown()
    cluster.shutdown()
