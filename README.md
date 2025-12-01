# FinaSync
Financial Report Analysis ADK Project

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

### Environment Variables (Optional)

Add these to your `.env` file if needed:
```
GOOGLE_CLIENT_ID="your_google_cloud_client_id"
GOOGLE_CLIENT_SECRET="your_google_cloud_client_secret"
```

