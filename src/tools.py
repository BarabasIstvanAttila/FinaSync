import pandas as pd
import yfinance as yf
from pypdf import PdfReader
import matplotlib.pyplot as plt
import os
import json
import datetime

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

def generate_financial_chart(expenses: float, savings: float, stock_value: float) -> dict:
    """
    Generates a financial overview chart (Pie Chart) comparing Liquidity (Expenses + Savings) vs Stock Assets.
    It saves the chart as 'financial_snapshot.png' in the current directory.

    Args:
        expenses: Total monthly expenses.
        savings: Total calculated savings (Income - Expenses).
        stock_value: Total value of stock portfolio.

    Returns:
        dict: {"status": "success", "image_path": "..."}
    """
    try:
        # Data preparation
        labels = ['Expenses', 'Savings (Liquidity)', 'Stock Value']
        sizes = [expenses, savings, stock_value]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Monthly Financial Snapshot: Liquidity vs Assets')
        
        output_path = "financial_snapshot.png"
        plt.savefig(output_path)
        plt.close()
        
        return {
            "status": "success",
            "image_path": os.path.abspath(output_path),
            "message": f"Chart generated successfully at {output_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to generate chart: {str(e)}"
        }

def update_monthly_cache(category: str, summary: str) -> dict:
    """
    Updates the monthly cache with new findings.
    
    Args:
        category: 'expenses' or 'investments'.
        summary: The text summary or data returned by the analyst.
        
    Returns:
        dict: {"status": "success", "message": "..."}
    """
    cache_file = "fina_cache.json"
    try:
        # Load existing cache or create new
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                try:
                    cache = json.load(f)
                except json.JSONDecodeError:
                    cache = {}
        else:
            cache = {}
            
        # Update timestamp and data
        cache["last_updated"] = str(datetime.datetime.now())
        cache[category] = summary
        
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=4)
            
        return {"status": "success", "message": f"Successfully updated cache for {category}."}
    except Exception as e:
        return {"status": "error", "error_message": f"Cache update failed: {str(e)}"}

def get_monthly_cache() -> dict:
    """
    Retrieves the current month's cached financial data.
    
    Returns:
        dict: {"status": "success", "data": {...}}
    """
    cache_file = "fina_cache.json"
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            return {"status": "success", "data": cache}
        else:
            return {"status": "success", "data": {}, "message": "Cache is empty."}
    except Exception as e:
        return {"status": "error", "error_message": f"Cache retrieval failed: {str(e)}"}