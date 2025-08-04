# backend/main.py

import os
from dotenv import load_dotenv
import mysql.connector
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# New Imports for AI Logic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# --- Initialize FastAPI App and CORS ---
app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for API Input ---
# This defines the structure of the data our frontend will send
class FarmDataRequest(BaseModel):
    farm_location: str
    crop_type: str

# --- Mock Functions to Simulate Real Data ---
# In a real app, these would make API calls. For now, they return fake data.
def get_weather_data(location: str):
    print(f"MOCK: Getting weather for {location}...")
    return {"forecast": "14-day forecast shows high humidity and rising temperatures."}

def get_satellite_data(location: str):
    print(f"MOCK: Getting satellite NDVI data for {location}...")
    return {"ndvi_analysis": "NDVI readings indicate moderate plant stress in Block B."}

def query_tidb_history(location: str, crop: str):
    print(f"MOCK: Querying TiDB for historical data for {location}...")
    # This simulates finding a relevant past event using vector search in TiDB
    return {"historical_precedent": "A similar weather pattern in 2019 led to a downy mildew outbreak."}
# ----------------------------------------------


@app.get("/")
def read_root():
    return {"message": "Agri-Intel Agent is running!"}


@app.get("/api/db-check")
def check_database_connection():
    # This function remains the same, for testing purposes
    try:
        # ... (database connection logic is unchanged) ...
        return {"status": "success", "db_version": "Connected!"}
    except mysql.connector.Error as err:
        return {"status": "error", "error_message": str(err)}


# --- THE CORE AI AGENT ENDPOINT ---
@app.post("/api/get-farm-analysis")
def get_farm_analysis(request: FarmDataRequest):
    """
    This is the main agentic workflow.
    """
    print(f"Received request for analysis: {request}")

    # 1. Gather Data (using our mock functions)
    weather_data = get_weather_data(request.farm_location)
    satellite_data = get_satellite_data(request.farm_location)
    historical_data = query_tidb_history(request.farm_location, request.crop_type)

    # 2. Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

    # 3. Create the Prompt Template
    # This template structures all our data into a clear prompt for the AI.
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

    # 4. Create the LLM Chain
    chain = prompt_template | llm

    # 5. Invoke the Agentic Chain with the data
    print("Invoking AI agent...")
    response = chain.invoke({
        "location": request.farm_location,
        "crop_type": request.crop_type,
        "weather": weather_data['forecast'],
        "satellite": satellite_data['ndvi_analysis'],
        "history": historical_data['historical_precedent']
    })
    print("AI response received.")

    # 6. Return the AI's response
    return {"status": "success", "analysis": response.content}