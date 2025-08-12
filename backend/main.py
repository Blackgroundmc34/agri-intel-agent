# backend/main.py

import os
from dotenv import load_dotenv
import mysql.connector
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# --- Initialize FastAPI App and CORS ---
app = FastAPI()

# Allow frontend origin from Vercel
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")  # fallback to "*" if not set
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for API Input ---
class FarmDataRequest(BaseModel):
    farm_location: str
    crop_type: str

# --- Mock Data Functions ---
def get_weather_data(location: str):
    print(f"MOCK: Getting weather for {location}...")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}

def get_satellite_data(location: str):
    print(f"MOCK: Getting satellite NDVI data for {location}...")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}

def query_tidb_history(location: str, crop: str):
    print(f"MOCK: Querying TiDB for historical data for {location}...")
    return {"historical_precedent": "A similar weather pattern in 2019 led to a downy mildew outbreak."}

@app.get("/")
def read_root():
    return {"message": "Agri-Intel Agent is running!"}

@app.get("/api/db-check")
def check_database_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        connection.close()
        return {"status": "success", "db_version": version[0]}
    except mysql.connector.Error as err:
        return {"status": "error", "error_message": str(err)}

@app.post("/api/get-farm-analysis")
def get_farm_analysis(request: FarmDataRequest):
    print(f"Received request for analysis: {request}")

    weather_data = get_weather_data(request.farm_location)
    satellite_data = get_satellite_data(request.farm_location)
    historical_data = query_tidb_history(request.farm_location, request.crop_type)

    llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert AI agronomist for farmers in the Western Cape, South Africa.
        Your task is to provide a clear, actionable recommendation based on the data provided.

        DATA:
        - Location: {location}
        - Crop Type: {crop_type}
        - 14-Day Weather Forecast: {weather}
        - Satellite NDVI Analysis: {satellite}
        - Historical Precedent from TiDB: {history}

        Based on all of this data, provide a "Risk Assessment" and a "Recommended Action".
        Format your response clearly and concisely.
        """
    )

    chain = prompt_template | llm

    response = chain.invoke({
        "location": request.farm_location,
        "crop_type": request.crop_type,
        "weather": weather_data['forecast'],
        "satellite": satellite_data['ndvi_analysis'],
        "history": historical_data['historical_precedent']
    })

    return {"status": "success", "analysis": response.content}
