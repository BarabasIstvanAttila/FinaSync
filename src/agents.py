import os
# Added SequentialAgent to imports
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from tools import (
    read_excel_transactions, 
    read_csv_transactions, 
    read_pdf_content, 
    get_current_stock_price,
    generate_financial_chart,
    update_monthly_cache,
    get_monthly_cache
)

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
    Factory function to create the agent hierarchy using a Sequential Pipeline.
    Order: Investment -> Expense -> CFO.
    Returns the root 'SequentialAgent'.
    """
    
    gemini_model = Gemini(model=MODEL_NAME)

    # --- 1. Investment Analyst Agent (Step 1) ---
    # Writes directly to cache. Passes file path to next agent.
    investment_agent = LlmAgent(
        name="InvestmentAnalyst",
        model=gemini_model,
        tools=[read_pdf_content, get_current_stock_price, update_monthly_cache],
        instruction="""
        You are Step 1 in the financial pipeline: Investment Analysis.
        
        Task:
        1. Identify the file path in the user's request.
        2. Check if the file is a PDF (.pdf).
           - YES: Use `read_pdf_content`. Identify tickers/shares. Calculate Portfolio Value.
             Then call `update_monthly_cache(category='investments', summary=...)`.
           - NO: Do nothing regarding analysis.
        
        CRITICAL OUTPUT RULE: 
        Regardless of whether you processed the file or not, you MUST end your response by repeating the file path so the next agent can use it.
        Format: "Step 1 Complete. Passing file: <file_path>"
        """
    )

    # --- 2. Expense Analyst Agent (Step 2) ---
    # Writes directly to cache.
    expense_agent = LlmAgent(
        name="ExpenseAnalyst",
        model=gemini_model,
        tools=[read_excel_transactions, read_csv_transactions, update_monthly_cache],
        instruction="""
        You are Step 2 in the financial pipeline: Expense Analysis.
        
        Task:
        1. Look at the input text from the previous agent to find the "Passing file: <file_path>" section.
        2. Check if that file is an Excel (.xlsx) or CSV (.csv).
           - YES: Use `read_excel_transactions` or `read_csv_transactions`. Analyze Total Spend.
             Then call `update_monthly_cache(category='expenses', summary=...)`.
           - NO: Do nothing regarding analysis.
        
        Output: Confirm that Step 2 is done and the cache is updated.
        """
    )

    # --- 3. CFO (Step 3) ---
    # Reads the cache and reports.
    cfo_agent = LlmAgent(
        name="CFO",
        model=gemini_model,
        tools=[generate_financial_chart, get_monthly_cache],
        instruction="""
        You are Step 3: The Chief Financial Officer (CFO).
        
        Task:
        1. The previous agents have already populated the cache.
        2. Call `get_monthly_cache` to retrieve the FULL monthly picture (Expenses + Investments).
        3. Parse the data from the cache:
           - Extract Total Expenses.
           - Extract Total Stock Value.
           - Calculate Savings (Income - Expenses). Assume Income $5000 if unknown.
        4. Call `generate_financial_chart` with these numbers.
        5. Write a final monthly snapshot report and provide the chart path.
        """
    )

    # --- 4. Root Pipeline (Sequential) ---
    # Executes the agents strictly in order.
    pipeline_agent = SequentialAgent(
        name="FinaSyncPipeline",
        sub_agents=[investment_agent, expense_agent, cfo_agent]
    )
    
    return pipeline_agent