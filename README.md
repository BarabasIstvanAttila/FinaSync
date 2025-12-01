# FinaSync
Financial Report Analysis ADK Project

This codebase is written in Pyton, uses Google AI Studio and Google Cloud


# Setup

## 1. Create a virtual environment (crucial for isolating dependencies)
python3 -m venv venv
source venv/bin/activate

## 2. Install Google ADK and data libraries
pip install google-adk pandas openpyxl pypdf yfinance tabulate matplotlib aiosqlite greenlet

### API Requirements
Needs a Gemini API Key.

Get a key from Google AI Studio.
Add the key to an .env file e.g. GOOGLE_API_KEY="your_actual_api_key"

For Google Drive MCP tool needs Google Cloud Keys
Add teh keys to .env file e.g:
GOOGLE_CLIENT_ID="your_google_cloud_client_id"
GOOGLE_CLIENT_SECRET="your_google_cloud_client_secret"

