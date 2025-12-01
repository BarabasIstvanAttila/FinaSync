# FinaSync
FinaSync: The Personal Wealth Concierge -- Financial Report Analysis ADK Project

Managing personal finances is fragmented and time-consuming. My financial data is siloed: expense logs exist in Excel, bank statements are in PDF, and stock portfolio performance is locked in monthly brokerage reports. Manually extracting this data to calculate a simple "Monthly Net Worth" or "Savings Rate" takes hours of data entry and is prone to human error.

 FinaSync is an automated Concierge Agent pipeline. It listens to a specific Google Drive folder, automatically detects new financial documents (PDF/Excel), and deploys specialized sub-agents to extract data, categorize expenses, and analyze stock performance against historical benchmarks. It creates a unified "Monthly Snapshot" and saves the consolidated state, reducing hours of work to zero minutes.

 Instead of one massive agent trying to do everything, break it down into a coordinated team. This is more robust and easier to debug.
* 1. The Dispatcher (Orchestrator): Triggers when files appear. It opens the file just enough to classify it (e.g., "This is a Bank Statement" vs. "This is a Stock Report") and routes it to the correct sub-agent.
* 2. The Expense Analyst: specialized in extracting transaction rows from PDFs/Excels and categorizing them (Groceries, Utilities, etc.).
* 3. The Investment Analyst: specialized in reading stock tickers and quantities from brokerage reports. It can also fetch current market data to verify valuations.
* 4. The CFO (Synthesis Agent): Receives structured data from the Expense and Investment agents. It calculates the final totals (Income - Expenses = Savings) and generates the report.

This codebase is written in Python, uses Google AI Studio and Google Cloud


# Setup

## 1. Create a virtual environment (crucial for isolating dependencies)
```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Google ADK and data libraries
```bash
pip install google-adk pandas openpyxl pypdf yfinance tabulate matplotlib aiosqlite greenlet
```

## API Requirements

### Gemini API Key
Get a key from [Google AI Studio](https://aistudio.google.com/).
Add the key to an `.env` file:
```
GOOGLE_API_KEY="your_actual_api_key"
```

---

## Google Drive MCP Server Setup

The Google Drive MCP Server allows AI to access and search files in your Google Drive.

### Step 1: Google Cloud Project Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/projectcreate)
   - Create a new project

2. **Enable Google Drive API**
   - Navigate to [APIs & Services](https://console.cloud.google.com/workspace-api/products)
   - Enable the **Google Drive API**

3. **Configure OAuth Consent Screen**
   - Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
   - For testing, select "Internal" or "External" (External requires verification for production)
   - Add the OAuth scope: `https://www.googleapis.com/auth/drive.readonly`

4. **Create OAuth Client ID**
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials/oauthclient)
   - Select application type: **Desktop App**
   - Download the JSON file with OAuth keys
   - Rename it to `gcp-oauth.keys.json` and place it in the project root

### Step 2: Authentication

Run the authentication command to save your credentials:

```bash
npx -y @modelcontextprotocol/server-gdrive auth
```

This will:
- Open a browser window for Google authentication
- Ask you to grant read-only access to your Google Drive
- Save credentials to `.gdrive-server-credentials.json`

### Step 3: VS Code MCP Configuration

The MCP configuration is already set up in `.vscode/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "gdrive": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-gdrive"
        ],
        "env": {
          "GDRIVE_CREDENTIALS_PATH": "${workspaceFolder}/.gdrive-server-credentials.json"
        }
      }
    }
  }
}
```

### Google Drive MCP Capabilities

**Tools:**
- `search`: Search for files in Google Drive by query

**Resources:**
- Access files via `gdrive:///<file_id>`
- Google Docs → Markdown
- Google Sheets → CSV
- Google Presentations → Plain text
- Google Drawings → PNG
- Other files → Native format
