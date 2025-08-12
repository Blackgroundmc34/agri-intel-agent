# agri-intel-agent
Agri-Intel Agent: Your AI Agronomist for Precision Farming
This project is a submission for the TiDB AgentX Hackathon 2025. It demonstrates an intelligent, agentic workflow for precision farming by combining real-time environmental data with historical farming precedents stored in TiDB Cloud. The application provides farmers with clear, actionable recommendations to mitigate risks and optimize crop yields.

🚀 Quick Start (Local Setup)
Follow these steps to get the project up and running on your local machine.

Prerequisites
Node.js (v18 or higher)

Python (v3.9 or higher)

pip

npm or yarn

A TiDB Cloud account with your historical_data table populated.

Your TiDB Cloud connection string and password.

Your Vercel environment variables.

1. Backend Setup
The backend is built with FastAPI.

# Navigate to the backend directory
cd backend

# Install the Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8080


The backend server will now be running on http://localhost:8080.

2. Frontend Setup
The frontend is a Next.js application.

# Navigate to the frontend directory
cd frontend

# Install the Node.js dependencies
npm install

# Start the Next.js development server
npm run dev


The frontend application will be available at http://localhost:3000.

3. Environment Variables
To connect your frontend and backend, you need to set up environment variables for both.

For the backend: Create a .env file in the backend directory with your TiDB Cloud connection details.

TIDB_DATABASE_URL="mysql://<username>:<password>@<host>:<port>/<database>"


For the frontend: Create a .env.local file in the frontend directory to point to your local backend.

NEXT_PUBLIC_API_URL="http://localhost:8080"


🌐 Data Flow and Architecture
The Agri-Intel Agent works as follows:

The user provides a farm_location and crop_type via the Next.js frontend.

The frontend sends this information to the FastAPI backend.

The backend acts as an "agentic" orchestrator:

It calls external APIs to retrieve real-time weather and satellite data for the specified location.

It performs a vector search in TiDB Cloud to find historical precedents and patterns for the given crop_type and environmental conditions.

It uses a Language Model (LLM) to synthesize all of this information into a clear, actionable analysis for the farmer.

The backend sends this final analysis back to the frontend to be displayed.

📄 Submission Details
This project is being submitted for the TiDB AgentX Hackathon.

TiDB Cloud Account Email: zithazweloj@gmail.com

Demo Video URL: https://youtu.be/7sO0fy3UGqI

Open Source License: https://platform.openai.com/ , vercel: https://agri-intel-agent.vercel.app/, Raleway: https://agri-intel-agent-new-production.up.railway.app/
