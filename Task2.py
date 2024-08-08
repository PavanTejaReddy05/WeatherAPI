from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
import Secretkey as SK
from jose import jwt,JWTError
import requests
from fastapi.middleware.cors import CORSMiddleware

client=AsyncIOMotorClient("mongodb+srv://bogireddyptr5:Bogireddyptr5@cluster0.uq0feuh.mongodb.net/TokenAuth")
DB=client.get_database("TokenAuth")
clts=DB.get_collection("Task2")

class Signup(BaseModel):
    First_Name:str
    Last_Name:str
    UserName:str
    Password:str
    Ph_No:int

class Login(BaseModel):
    UserName:str
    Password:str

Pwd_Context=CryptContext(schemes=["bcrypt"],deprecated="auto")
ALGORITHM="HS256"
secret_key=SK.secret_key_login
Bearer=HTTPBearer()

async def hash(password:str):
    return Pwd_Context.hash(password)

app=FastAPI()
origins=[
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/Signup")
async def SignUp(S:Signup):
    hashed_Pwd=await hash(S.Password)
    S.Password=hashed_Pwd
    dtls=await clts.insert_one(S.dict())
    return {"Message":"User Registration Successfull","Details":S}

class Signin(BaseModel):
    UserName: str
    Password: str

async def Vrfy_Tkn(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
@app.post("/Signin")
async def LogIn(signin:Signin):
    user_data=await clts.find_one({"UserName":signin.UserName})
    hashed_password = user_data.get("Password")
    if user_data and Pwd_Context.verify(signin.Password, hashed_password):
        now=datetime.utcnow()
        exp=now+timedelta(minutes=2)
        payload={"Sub":signin.UserName,"iat":now,"exp":exp}
        token=jwt.encode(payload,secret_key,algorithm=ALGORITHM)
        return{"AccessToken":token,"Message":"Login Successfull"}
    else:
        return{"Message":"Invalid Credentials"}
    
@app.get("/UserDetails")
async def get_dtls(UserName:str,credentials:HTTPAuthorizationCredentials=Depends(Bearer)):
# async def get_dtls(UserName:str):
    token=credentials.credentials
    username=await Vrfy_Tkn(token)
    if username:
        user_data=await clts.find_one({"UserName":UserName})
        user_data["_id"] = str(user_data["_id"])
        return {"Message":"Token is Active","Details":user_data}
    

@app.get('/getDetails')
async def getDetails(Name:str,city :str,credentials:HTTPAuthorizationCredentials=Depends(Bearer)):
# async def getDetails(Name:str,city :str):
    token=credentials.credentials
    # print(f"Received token: {token}")
    payload= await Vrfy_Tkn(token)
    # if LogIn.now<LogIn.exp:
    if payload and datetime.utcnow() < datetime.fromtimestamp(payload["exp"]):
    # if username:
        APIkey="c6d66259c7b3e8ac74233b0a42e2a485"
        city_name=city
        
        url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={APIkey}"
        response=requests.get(url)
        data=response.json()
        
        details={
            "City":data["name"],
            "Description":data["weather"][0]["description"],
            "Temperature":data["main"]["temp"],
            "Humidity":data["main"]["humidity"],
            "Wind":data["wind"]["speed"],
            "Visibility in Meters":data["visibility"]
        }
        result=f"Msg:Hello {Name}"
        return result,{"Weather":details}
        return{"Message":message}
    else:
        msg="Token_Expired"
        return msg

