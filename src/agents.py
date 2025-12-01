import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from tools import read_excel_transactions, read_csv_transactions, read_pdf_content, get_current_stock_price

# --- Authentication Setup ---
if "GOOGLE_API_KEY" not in os.environ:
    print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables.")
    print("Please set it in your terminal using: export GOOGLE_API_KEY='your_key_here'")
else:
    print("✅ GOOGLE_API_KEY found in environment.")

# Global Model Configuration
MODEL_NAME = "gemini-2.5-flash-lite" 

def create_fina_sync_agent():
    """
    Factory function to create the agent hierarchy.
    Returns the root 'Dispatcher' agent.
    """
    
    # --- 1. Expense Analyst Agent ---
    expense_agent = LlmAgent(
        name="ExpenseAnalyst",
        model=Gemini(model=MODEL_NAME),
        tools=[read_excel_transactions, read_csv_transactions],
        instruction="""
        You are an expert Expense Analyst.
        Your goal is to analyze transaction data from Excel or CSV files.
        
        When given a file path:
        1. Check the file extension. 
           - If .xlsx/.xls, use `read_excel_transactions`.
           - If .csv, use `read_csv_transactions`.
        2. Check the tool output:
           - If 'status' is 'error', report the error message to the user.
           - If 'status' is 'success', proceed with the 'data' field.
        3. Group expenses by 'Category' and calculate the total sum for each.
        4. Identify the highest spending category.
        5. Return a structured summary of Total Spend and Breakdown by Category.
        """
    )
    
    # --- 2. Investment Analyst Agent ---
    investment_agent = LlmAgent(
        name="InvestmentAnalyst",
        model=Gemini(model=MODEL_NAME),
        tools=[read_pdf_content, get_current_stock_price],
        instruction="""
        You are a Senior Investment Analyst.
        Your goal is to analyze brokerage statements (PDFs) and verify valuations.
        
        When given a file path:
        1. Use `read_pdf_content` to extract text from the report.
           - If 'status' is 'error', stop and report the issue.
        2. Identify stock tickers and quantity of shares held (e.g., "10 shares of AAPL").
        3. IMPORTANT: For every ticker found, use `get_current_stock_price`.
           - Check if 'status' is 'success' before using the price.
        4. Calculate the total current portfolio value based on live prices.
        5. Compare this to the 'Cost Basis' or previous value found in the PDF if available.
        """
    )
    
    # --- 3. The Dispatcher (Root Agent) ---
    dispatcher_agent = LlmAgent(
        name="Dispatcher",
        model=Gemini(model=MODEL_NAME),
        sub_agents=[expense_agent, investment_agent],
        instruction="""
        You are the FinaSync Concierge Dispatcher.
        Your job is to receive new files and route them to the correct specialist.
        
        RULES:
        - If the file is an Excel (.xlsx) OR CSV (.csv) -> Delegate to 'ExpenseAnalyst'.
        - If the file is a PDF -> Delegate to 'InvestmentAnalyst'.
        - If the file type is unknown, reply with "File type not supported."
        
        Always summarize the findings returned by the sub-agents into a final one-sentence confirmation for the user.
        """
    )
    
    return dispatcher_agent