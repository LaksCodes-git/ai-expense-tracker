"""
Test if OpenAI can extract structured data from receipt text
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Sample messy OCR text (replace with your actual OCR output)
SAMPLE_TEXT = """
STARBUCKS
123 Main Street
Mumbai, MH 400001

Date: 22/10/2025
Time: 14:30

Grande Latte        ₹450.00
Croissant          ₹250.00
-----------------------------
Subtotal           ₹700.00
Tax (5%)            ₹35.00
-----------------------------
TOTAL              ₹735.00

Thank you!
"""

def extract_receipt_data(receipt_text):
    """Use AI to extract structured data from messy OCR text"""
    
    print("🤖 Sending to OpenAI...")
    print("=" * 60)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper, good enough
            messages=[
                {
                    "role": "system",
                    "content": """You are a receipt data extractor. 
                    Extract these fields from receipt text:
                    - vendor: merchant/store name
                    - date: transaction date (YYYY-MM-DD format)
                    - total: total amount paid (number only, no currency)
                    - currency: INR, USD, etc.
                    - category: Food, Transport, Shopping, Services, or Other
                    - items: list of items purchased (if visible)
                    
                    Return as JSON. Use null if field not found."""
                },
                {
                    "role": "user",
                    "content": f"Extract data from this receipt:\n\n{receipt_text}"
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse result
        result = json.loads(response.choices[0].message.content)
        
        print("✅ AI EXTRACTION SUCCESSFUL!")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with sample text
    print("📝 Input text:")
    print(SAMPLE_TEXT)
    print()
    
    # Extract data
    extract_receipt_data(SAMPLE_TEXT)