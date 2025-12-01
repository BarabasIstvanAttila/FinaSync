import pandas as pd
import yfinance as yf
from pypdf import PdfReader
import matplotlib.pyplot as plt
import os
from typing import Dict, Any

# Import ToolContext to access session state
from google.adk.tools.tool_context import ToolContext

def read_excel_transactions(file_path: str) -> dict:
    """Reads Excel transactions."""
    try:
        df = pd.read_excel(file_path)
        return {"status": "success", "data": df.to_markdown(index=False)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def read_csv_transactions(file_path: str) -> dict:
    """Reads CSV transactions."""
    try:
        try:
            df = pd.read_csv(file_path)
        except:
            df = pd.read_csv(file_path, sep=';')
        return {"status": "success", "data": df.to_markdown(index=False)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def read_pdf_content(file_path: str) -> dict:
    """Extracts text from PDF."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return {"status": "success", "data": text[:10000]}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def get_current_stock_price(ticker: str) -> dict:
    """Fetches stock price."""
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info.last_price
        return {"status": "success", "price": round(price, 2)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def generate_financial_chart(expenses: float, savings: float, stock_value: float) -> dict:
    """Generates a pie chart and saves it locally."""
    try:
        labels = ['Expenses', 'Savings (Liquidity)', 'Stock Value']
        sizes = [expenses, savings, stock_value]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        plt.figure(figsize=(10, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Monthly Financial Snapshot')
        
        output_path = "financial_snapshot.png"
        plt.savefig(output_path)
        plt.close()
        
        return {
            "status": "success",
            "image_path": os.path.abspath(output_path),
            "message": f"Chart generated at {output_path}"
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# --- NEW SESSION STATE TOOLS ---

def save_financial_finding(tool_context: ToolContext, category: str, summary: str) -> Dict[str, Any]:
    """
    Saves a financial finding (expenses or investments) into the persistent Session State.
    
    Args:
        tool_context: Provided automatically by ADK.
        category: 'expenses' or 'investments'.
        summary: The data/summary text to store.
    """
    # We use a specific prefix to keep state organized
    key = f"financial:{category}"
    tool_context.state[key] = summary
    return {"status": "success", "message": f"Saved data to session state under '{key}'"}

def get_financial_findings(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieves all financial data stored in the current Session State.
    
    Args:
        tool_context: Provided automatically by ADK.
    """
    expenses = tool_context.state.get("financial:expenses", "No expense data yet.")
    investments = tool_context.state.get("financial:investments", "No investment data yet.")
    
    return {
        "status": "success", 
        "data": {
            "expenses": expenses,
            "investments": investments
        }
    }