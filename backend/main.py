# main.py
# This is a complete and production-ready FastAPI application for Railway.

import os
import uvicorn
import mysql.connector
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# AI and LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from a .env file for local development
# Railway will handle these variables automatically in production
load_dotenv()

# --- FastAPI App Initialization ---
app = FastAPI(title="Agri-Intel Agent Backend")

# --- CORS Middleware ---
# This is a crucial step for allowing your Vercel frontend to access this API.
# The FRONTEND_ORIGIN environment variable is used for production,
# while localhost is included for local development and testing.
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
# This defines the expected structure of the JSON payload for the analysis endpoint.
class FarmDataRequest(BaseModel):
    farm_location: str
    crop_type: str

# --- Data Fetching Functions ---
# These functions are placeholders for real-world API calls to fetch data.
# In a real application, you would replace these with actual requests.

def get_weather_data(location: str) -> dict:
    """Fetches real-time weather data for a given location."""
    print(f"Fetching mock weather data for {location}...")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}

def get_satellite_data(location: str) -> dict:
    """Fetches satellite imagery and NDVI analysis data."""
    print(f"Fetching mock satellite data for {location}...")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}

def query_tidb_history(location: str, crop: str) -> dict:
    """
    Connects to the TiDB Serverless database and queries historical data.
    This demonstrates connecting to the database using environment variables.
    """
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
        # Placeholder query - replace with your actual vector search logic
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

# --- Health Check Endpoint ---
@app.get("/")
def read_root():
    """A simple health check to confirm the API is running."""
    return {"message": "Agri-Intel Agent is running!"}

# --- Database Connection Test Endpoint ---
@app.get("/api/db-check")
def check_database_connection():
    """Checks the connection to the TiDB database."""
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
        raise HTTPException(status_code=500, detail=f"TiDB connection error: {err}")

# --- Main AI Analysis Endpoint ---
@app.post("/api/get-farm-analysis")
def get_farm_analysis(request: FarmDataRequest):
    """
    The main endpoint that orchestrates the data collection and
    passes it to the LLM for a final analysis and recommendation.
    """
    print(f"Received request for analysis: {request}")

    # Step 1: Collect data from various sources
    weather_data = get_weather_data(request.farm_location)
    satellite_data = get_satellite_data(request.farm_location)
    historical_data = query_tidb_history(request.farm_location, request.crop_type)

    # Step 2: Set up the LLM
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Step 3: Define the prompt template for the LLM
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

    # Step 4: Create a LangChain chain and invoke the LLM
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

# --- Entry Point for Uvicorn ---
if __name__ == "__main__":
    # Railway sets the PORT environment variable. We default to 8080 for local testing.
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

