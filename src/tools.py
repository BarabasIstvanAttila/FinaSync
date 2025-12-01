import pandas as pd
import yfinance as yf
from pypdf import PdfReader

def read_excel_transactions(file_path: str) -> dict:
    """
    Reads an Excel file containing financial transactions.
    Assumes columns: 'Date', 'Description', 'Category', 'Amount'.
    
    Args:
        file_path: The local path to the .xlsx file.
        
    Returns:
        dict: {"status": "success", "data": "markdown_string"} or {"status": "error", "error_message": "..."}
    """
    try:
        df = pd.read_excel(file_path)
        return {
            "status": "success", 
            "data": df.to_markdown(index=False)
        }
    except Exception as e:
        return {
            "status": "error", 
            "error_message": f"Error reading Excel file: {str(e)}"
        }

def read_csv_transactions(file_path: str) -> dict:
    """
    Reads a CSV file containing financial transactions.
    Robustly handles different delimiters (comma, semicolon).
    
    Args:
        file_path: The local path to the .csv file.
        
    Returns:
        dict: {"status": "success", "data": "markdown_string"} or {"status": "error", "error_message": "..."}
    """
    try:
        # Try reading with default comma
        try:
            df = pd.read_csv(file_path)
        except:
            # Fallback for European CSVs that might use semicolons
            df = pd.read_csv(file_path, sep=';')
            
        return {
            "status": "success", 
            "data": df.to_markdown(index=False)
        }
    except Exception as e:
        return {
            "status": "error", 
            "error_message": f"Error reading CSV file: {str(e)}"
        }

def read_pdf_content(file_path: str) -> dict:
    """
    Extracts text from a PDF file (e.g., a brokerage report).
    
    Args:
        file_path: The local path to the .pdf file.
        
    Returns:
        dict: {"status": "success", "data": "extracted_text"} or {"status": "error", "error_message": "..."}
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return {
            "status": "success", 
            "data": text[:10000] # Limit context window usage
        }
    except Exception as e:
        return {
            "status": "error", 
            "error_message": f"Error reading PDF file: {str(e)}"
        }

def get_current_stock_price(ticker: str) -> dict:
    """
    Fetches the current market price for a given stock ticker symbol.
    
    Args:
        ticker: The stock symbol (e.g., 'AAPL', 'GOOGL').
        
    Returns:
        dict: {"status": "success", "price": float} or {"status": "error", "error_message": "..."}
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info is often faster than history()
        price = stock.fast_info.last_price
        return {
            "status": "success", 
            "price": round(price, 2)
        }
    except Exception as e:
        return {
            "status": "error", 
            "error_message": f"Could not fetch price for {ticker}: {str(e)}"
        }