# main.py
import os
import uvicorn
import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# AI and LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

# --- FastAPI App Initialization ---
app = FastAPI(title="Agri-Intel Agent Backend")

# --- CORS Middleware ---
# Load FRONTEND_ORIGIN from environment variables. It's crucial this is set correctly in Railway.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
origins = [frontend_origin, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for API Input ---
class FarmDataRequest(BaseModel):
    farm_location: str
    crop_type: str

# --- Data Fetching Functions ---
def get_weather_data(location: str) -> dict:
    """Fetches real-time weather data for a given location."""
    print(f"Fetching mock weather data for {location}...")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}

def get_satellite_data(location: str) -> dict:
    """Fetches satellite imagery and NDVI analysis data."""
    print(f"Fetching mock satellite data for {location}...")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}

def query_tidb_history(location: str, crop: str) -> dict:
    """Connects to the TiDB Serverless database and queries historical data."""
    print(f"Connecting to TiDB for historical data for {location}...")
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
        # Capture and report the specific database error
        error_message = f"TiDB connection or query error: {err}"
        print(error_message)
        return {"historical_precedent": error_message}

# --- Health Check Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Agri-Intel Agent is running!"}

# --- Main AI Analysis Endpoint ---
@app.post("/api/get-farm-analysis")
def get_farm_analysis(request: FarmDataRequest):
    print(f"Received request for analysis: {request}")
    weather_data = get_weather_data(request.farm_location)
    satellite_data = get_satellite_data(request.farm_location)
    historical_data = query_tidb_history(request.farm_location, request.crop_type)
    
    # Check for errors from data sources before invoking the LLM
    if "error" in historical_data.get("historical_precedent", "").lower():
        raise HTTPException(status_code=500, detail=historical_data["historical_precedent"])

    try:
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
        # Return a more specific error message from the exception
        error_detail = f"LLM or data processing error: {e}"
        print(f"Error invoking LLM: {e}")
        raise HTTPException(status_code=500, detail=error_detail)

# --- Entry Point for Uvicorn ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
