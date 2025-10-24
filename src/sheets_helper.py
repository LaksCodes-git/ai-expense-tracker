"""
Google Sheets integration - write expense data to spreadsheet
"""
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Import configuration
from config import CREDENTIALS_PATH, GOOGLE_SHEET_ID

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
load_dotenv()



# SHEET_ID = os.getenv('GOOGLE_SHEET_ID')



class SheetsManager:
    """Manage Google Sheets operations"""
    
    def __init__(self):
        """Initialize Google Sheets API client"""
        print("🔐 Authenticating with Google Sheets...")
        print(f"   Using credentials: {CREDENTIALS_PATH}")
        
        # Load credentials (using absolute path)
        creds = service_account.Credentials.from_service_account_file(
            str(CREDENTIALS_PATH), scopes=SCOPES
        )
        
        # Build service
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
        
        print("✅ Connected to Google Sheets")
        
    def setup_sheet(self):
        """Create headers if sheet is empty"""
        print("📋 Setting up sheet headers...")
        
        headers = [
            'Date',
            'Vendor',
            'Category',
            'Total',
            'Currency',
            'Tax',
            'Items',
            'Processed At'
        ]
        
        # Write headers to A1:H1
        body = {
            'values': [headers]
        }
        
        self.sheet.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='A1:H1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print("✅ Headers created")
    
    def add_expense(self, expense_data):
        """
        Add expense to sheet
        
        expense_data format:
        {
            'vendor': 'Starbucks',
            'date': '2025-10-22',
            'total': 735.00,
            'currency': 'INR',
            'category': 'Food',
            'tax': 35.00,
            'items': ['Latte', 'Croissant']
        }
        """
        print(f"📝 Adding expense: {expense_data.get('vendor', 'Unknown')}")
        
        # Prepare row data
        row = [
            expense_data.get('date', ''),
            expense_data.get('vendor', ''),
            expense_data.get('category', 'Other'),
            expense_data.get('total', 0),
            expense_data.get('currency', 'INR'),
            expense_data.get('tax', ''),
            ', '.join(expense_data.get('items', [])) if expense_data.get('items') else '',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        # Append to sheet
        body = {
            'values': [row]
        }
        
        result = self.sheet.values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='A:H',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Expense added to row {result.get('updates', {}).get('updatedRange', '')}")
        return result
    
    def get_all_expenses(self):
        """Get all expenses from sheet"""
        result = self.sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='A:H'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return []
        
        # Skip header row
        return values[1:]


def test_sheets():
    """Test Google Sheets integration"""
    print("\n" + "="*60)
    print("🧪 TESTING GOOGLE SHEETS INTEGRATION")
    print("="*60 + "\n")
    
    # Initialize
    manager = SheetsManager()
    
    # Setup headers
    manager.setup_sheet()
    
    # Test data
    test_expense = {
        'vendor': 'Test Cafe',
        'date': '2025-10-23',
        'total': 500.00,
        'currency': 'INR',
        'category': 'Food',
        'tax': 25.00,
        'items': ['Coffee', 'Sandwich']
    }
    
    # Add test expense
    print("\n📤 Adding test expense...")
    manager.add_expense(test_expense)
    
    # Read back
    print("\n📥 Reading expenses from sheet...")
    expenses = manager.get_all_expenses()
    print(f"✅ Found {len(expenses)} expense(s)")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE - Check your Google Sheet!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_sheets()