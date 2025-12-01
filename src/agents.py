import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from tools import (
    read_excel_transactions, 
    read_csv_transactions, 
    read_pdf_content, 
    get_current_stock_price,
    generate_financial_chart,
    save_financial_finding,
    get_financial_findings
)
from utils import get_project_root

# --- FIX: Robust Imports for MCP ---
McpTool = None
StdioServerParameters = None

try:
    # 1. Try importing McpTool
    try:
        from google.adk.tools import McpTool
    except ImportError:
        from google.adk.tools.mcp_tool import McpTool

    # 2. Try importing StdioServerParameters (Critical for config)
    try:
        from mcp import StdioServerParameters
    except ImportError:
        try:
            from modelcontextprotocol import StdioServerParameters
        except ImportError:
            print("⚠️ Warning: 'mcp' library not found. Installing it might fix the issue.")
            StdioServerParameters = None

except ImportError as e:
    print(f"⚠️ Warning: MCP dependencies missing: {e}")
    print("👉 MCP features (Google Drive) will be disabled.")
    McpTool = None

# --- Authentication Setup ---
if "GOOGLE_API_KEY" not in os.environ:
    print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables.")
    print("Please set it in your terminal using: export GOOGLE_API_KEY='your_key_here'")
else:
    print("✅ GOOGLE_API_KEY found in environment.")

MODEL_NAME = "gemini-2.5-flash-lite" 

def create_fina_sync_agent():
    """
    Factory function to create the agent hierarchy using Sequential Pipeline + Session State.
    Order: Investment -> Expense -> CFO.
    """
    
    gemini_model = Gemini(model=MODEL_NAME)

    # --- MCP Tool Setup (Google Drive) ---
    google_drive_tool = None
    if McpTool and StdioServerParameters:
        try:
            # Get the project root for credentials path
            project_root = get_project_root()
            credentials_path = os.path.join(project_root, ".gdrive-server-credentials.json")
            
            # Verify credentials exist
            if not os.path.exists(credentials_path):
                print(f"⚠️ Google Drive credentials not found at: {credentials_path}")
                print("👉 Run: npx -y @modelcontextprotocol/server-gdrive auth")
            else:
                # 1. Define the connection parameters matching .vscode/mcp.json
                cmd = "npx"
                args = ["-y", "@modelcontextprotocol/server-gdrive"]
                
                # Set up environment with credentials path
                env = os.environ.copy()
                env["GDRIVE_CREDENTIALS_PATH"] = credentials_path

                # 2. Create StdioServerParameters
                server_params = StdioServerParameters(
                    command=cmd, 
                    args=args, 
                    env=env
                )

                # 3. Initialize McpTool with connection params
                try:
                    # Modern ADK usage
                    google_drive_tool = McpTool(
                        connection_params=server_params, 
                        name="google_drive"
                    )
                except TypeError:
                    try:
                        # Alternative ADK usage
                        google_drive_tool = McpTool(
                            server_params=server_params, 
                            name="google_drive"
                        )
                    except TypeError:
                        # Fallback: Pass params directly
                        google_drive_tool = McpTool(
                            command=cmd, 
                            args=args, 
                            env=env, 
                            name="google_drive"
                        )

                print("✅ MCP Tool 'google_drive' initialized.")
                print(f"   Using credentials: {credentials_path}")

        except Exception as e:
            print(f"⚠️ Failed to initialize MCP Tool: {e}")
            print("ℹ️ Continuing without Google Drive support.")
            google_drive_tool = None
    elif McpTool and not StdioServerParameters:
        print("⚠️ MCP library missing StdioServerParameters. Install with: pip install mcp")
    else:
        print("ℹ️ MCP Tool not available. Google Drive features disabled.")

    # --- 1. Investment Analyst Agent ---
    investment_agent = LlmAgent(
        name="InvestmentAnalyst",
        model=gemini_model,
        tools=[read_pdf_content, get_current_stock_price, save_financial_finding],
        instruction="""
        You are Step 1: Investment Analysis.
        
        Task:
        1. Identify the file path in the user's request.
        2. Check if the file is a PDF (.pdf).
           - YES: Process it, calculate Portfolio Value.
             CRITICAL: Call `save_financial_finding(category='investments', summary=...)`.
           - NO: Do nothing analysis-wise.
        
        Output: "Step 1 Complete. Passing file: <file_path>"
        """
    )

    # --- 2. Expense Analyst Agent ---
    expense_agent = LlmAgent(
        name="ExpenseAnalyst",
        model=gemini_model,
        tools=[read_excel_transactions, read_csv_transactions, save_financial_finding],
        instruction="""
        You are Step 2: Expense Analysis.
        
        Task:
        1. Look for "Passing file: <file_path>" in the context.
        2. Check if that file is Excel/CSV.
           - YES: Process it, analyze spend.
             CRITICAL: Call `save_financial_finding(category='expenses', summary=...)`.
           - NO: Do nothing analysis-wise.
        
        Output: "Step 2 Complete. Cache updated."
        """
    )

    # --- 3. CFO ---
    cfo_tools = [generate_financial_chart, get_financial_findings]
    if google_drive_tool:
        cfo_tools.append(google_drive_tool)

    cfo_agent = LlmAgent(
        name="CFO",
        model=gemini_model,
        tools=cfo_tools,
        instruction="""
        You are Step 3: The CFO. 
        You are ACTION-ORIENTED. Do not ask for more data. Work with what you have.

        Task:
        1. Call `get_financial_findings` to retrieve session data.
        2. Parse the data:
           - Extract Total Expenses (Default to 0.0 if missing/not found).
           - Extract Total Stock Value (Default to 0.0 if missing/not found).
           - Calculate Savings (Income - Expenses). Assume Income $5000.
        
        MANDATORY ACTIONS (Do not skip):
        3. Call `generate_financial_chart` using the extracted numbers (even if they are 0).
        4. IF the Google Drive tool is available:
           - Use gdrive_search to find or verify a 'Financial Reports' folder.
           - Use gdrive_read_file to check existing reports if needed.
           - Upload the chart image ('financial_snapshot.png') to Google Drive.
           - Create a text summary report and upload it as well.
        
        Final Output: 
        - Confirm the chart was generated.
        - Confirm if the Google Drive upload was successful (or skipped if unavailable).
        - Provide the financial summary.
        """
    )

    # --- Root Pipeline ---
    pipeline_agent = SequentialAgent(
        name="FinaSyncPipeline",
        sub_agents=[investment_agent, expense_agent, cfo_agent]
    )
    
    return pipeline_agent