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

# Allow frontend origin from Vercel or fallback to "*"
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
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

# --- Real Data Functions (Replace Mock Data) ---

def get_weather_data(location: str):
    """
    Fetches real-time weather data for a given location.
    You will need to use a weather API here (e.g., OpenWeatherMap, AccuWeather).
    Remember to handle API keys securely and parse the response.
    """
    # Example using a fictional weather API
    # weather_api_key = os.getenv("WEATHER_API_KEY")
    # url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={location}&days=14"
    # try:
    #     response = requests.get(url)
    #     response.raise_for_status()
    #     data = response.json()
    #     # Extract relevant forecast information and return it
    #     return {"forecast": "Parsed weather data from API..."}
    # except requests.exceptions.RequestException as e:
    #     raise HTTPException(status_code=500, detail=f"Weather API error: {e}")

    # For now, we keep the mock response
    print(f"MOCK: Getting weather for {location}...")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}


def get_satellite_data(location: str):
    """
    Fetches real-time satellite imagery data (e.g., NDVI) for a location.
    You will need to use a satellite data API (e.g., from Planet, Sentinel Hub, etc.).
    This would involve a complex process of getting imagery, analyzing it, and
    returning a meaningful result.
    """
    # For now, we keep the mock response
    print(f"MOCK: Getting satellite NDVI data for {location}...")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}


def query_tidb_history(location: str, crop: str):
    """
    Connects to TiDB Serverless, queries historical data, and uses vector search.
    This function should be where the core logic of finding historical precedents lies.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "4000")), # TiDB Serverless uses port 4000
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_ca='</path/to/your/ca-cert.pem>' # Replace with the path to your SSL certificate
        )
        cursor = connection.cursor(buffered=True)

        # Your TiDB query logic would go here.
        # This is where you would perform a vector search against your historical data.
        # For now, we will perform a simple, illustrative query.
        cursor.execute("SELECT `historical_precedent_column` FROM `historical_data_table` WHERE `location` = %s AND `crop` = %s LIMIT 1", (location, crop))
        result = cursor.fetchone()
        connection.close()

        if result:
            return {"historical_precedent": result[0]}
        else:
            return {"historical_precedent": "No similar historical data found."}

    except mysql.connector.Error as err:
        print(f"TiDB connection error: {err}")
        return {"historical_precedent": "Error querying historical data."}

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
            ssl_ca='</path/to/your/ca-cert.pem>'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        connection.close()
        return {"status": "success", "db_version": version[0]}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

# --- AI Analysis Endpoint ---
@app.post("/api/get-farm-analysis")
def get_farm_analysis(request: FarmDataRequest):
    print(f"Received request for analysis: {request}")

    # Collect data from real sources (or mocks for now)
    try:
        weather_data = get_weather_data(request.farm_location)
        satellite_data = get_satellite_data(request.farm_location)
        historical_data = query_tidb_history(request.farm_location, request.crop_type)
    except HTTPException as e:
        return {"status": "error", "message": e.detail}

    # Setup LLM
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Prompt
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
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
