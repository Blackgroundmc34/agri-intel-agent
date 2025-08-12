# backend/main.py

import os
from dotenv import load_dotenv
import mysql.connector
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# --- Initialize FastAPI App and CORS ---
app = FastAPI()

# Read the frontend origin from environment variables for production security.
# This prevents unauthorized domains from making requests.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
origins = [frontend_origin, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the defined origins list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for API Input ---
class FarmDataRequest(BaseModel):
    farm_location: str
    crop_type: str

# --- Data Functions (Real-World placeholders) ---

def get_weather_data(location: str) -> dict:
    """
    Placeholder function to fetch real-time weather data.
    Replace with a real API call.
    """
    print(f"Fetching mock weather data for {location}")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}


def get_satellite_data(location: str) -> dict:
    """
    Placeholder function to fetch real-time satellite imagery data.
    Replace with a real API call.
    """
    print(f"Fetching mock satellite data for {location}")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}


def query_tidb_history(location: str, crop: str) -> dict:
    """
    Connects to TiDB Serverless, queries historical data, and uses vector search.
    This function should be replaced with your vector search logic.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "4000")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_ca=os.getenv("DB_SSL_CA")
        )
        cursor = connection.cursor(buffered=True)

        query = "SELECT historical_precedent_column FROM historical_data WHERE location = %s AND crop = %s LIMIT 1"
        cursor.execute(query, (location, crop))
        result = cursor.fetchone()
        connection.close()
        
        if result:
            return {"historical_precedent": result[0]}
        else:
            return {"historical_precedent": "No similar historical data found in TiDB."}
            
    except mysql.connector.Error as err:
        print(f"TiDB connection error: {err}")
        return {"historical_precedent": f"Error querying historical data from TiDB: {err}"}

# --- Test Routes ---
@app.get("/")
def read_root():
    return {"message": "Agri-Intel Agent is running!"}

@app.get("/api/db-check")
def check_database_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "4000")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_ca=os.getenv("DB_SSL_CA")
        )
        connection.close()
        return {"status": "success", "message": "Successfully connected to TiDB!"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

# --- AI Analysis Endpoint ---
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

    print("Invoking AI agent...")
    try:
        response = chain.invoke({
            "location": request.farm_location,
            "crop_type": request.crop_type,
            "weather": weather_data['forecast'],
            "satellite": satellite_data['ndvi_analysis'],
            "history": historical_data['historical_precedent']
        })
        print("AI response received.")
        return {"status": "success", "analysis": response.content}
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

# --- Entry Point for Railway ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
