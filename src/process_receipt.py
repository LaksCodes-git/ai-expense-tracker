"""
Main receipt processing pipeline: Image → OCR → AI → Structured Data
"""
import os
import json
from pathlib import Path
import pytesseract
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Import configuration
from config import OPENAI_API_KEY, RECEIPTS_DIR, GOOGLE_SHEET_ID
from sheets_helper import SheetsManager

load_dotenv()
# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def process_receipt(image_path):
    """
    Complete pipeline: Receipt image → Structured JSON
    
    Args:
        image_path: str or Path object pointing to receipt image
    """
    # Convert to Path object for consistent handling
    image_path = Path(image_path)
    
    if not image_path.exists():
        return {
            "status": "error",
            "message": f"Image not found: {image_path}"
        }
    
    print(f"\n{'='*60}")
    print(f"🎯 PROCESSING: {image_path.name}")
    print(f"   Full path: {image_path}")
    print(f"{'='*60}\n")
    
    # Step 1: OCR
    print("📸 Step 1: Running OCR...")
    try:
        image = Image.open(image_path)
        raw_text = pytesseract.image_to_string(image)
        print(f"✅ Extracted {len(raw_text)} characters")
    except Exception as e:
        return {"status": "error", "message": f"OCR failed: {str(e)}"}
    
    # Step 2: AI Extraction
    print("\n🤖 Step 2: AI extraction...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Extract receipt data as JSON:
                    {
                        "vendor": "merchant name",
                        "date": "YYYY-MM-DD",
                        "total": number,
                        "currency": "INR/USD/etc",
                        "category": "Food|Transport|Shopping|Services|Other",
                        "tax": number or null,
                        "items": ["item1", "item2"] or null
                    }
                    Use null for missing fields."""
                },
                {
                    "role": "user",
                    "content": f"Receipt text:\n\n{raw_text}"
                }
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        print("✅ Data extracted successfully")
        
    except Exception as e:
        return {"status": "error", "message": f"AI extraction failed: {str(e)}"}
    
    # Step 3: Return result
    result = {
        "status": "success",
        "data": data,
        "raw_text": raw_text,
        "confidence": "high" if len(raw_text) > 50 else "low"
    }
    
    print(f"\n{'='*60}")
    print("📊 FINAL RESULT:")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2))
    print(f"{'='*60}\n")
    
    return result

def test_multiple_receipts():
    """Test with all receipts in receipts/ folder"""
    
    print(f"\n📁 Looking for receipts in: {RECEIPTS_DIR}")
    
    if not RECEIPTS_DIR.exists():
        print(f"❌ Receipts directory not found: {RECEIPTS_DIR}")
        print("💡 Creating directory...")
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ Directory created. Add some receipt images and try again.")
        return
    
    receipt_files = list(RECEIPTS_DIR.glob("*.jpg")) + list(RECEIPTS_DIR.glob("*.png"))
    
    if not receipt_files:
        print(f"❌ No receipt images found in {RECEIPTS_DIR}")
        print("💡 Add some receipt images (jpg/png) to test")
        return
    
    print(f"\n🧪 Testing with {len(receipt_files)} receipt(s)\n")
    
    results = []
    for receipt_file in receipt_files:
        result = process_receipt(receipt_file)  # Now using Path object
        results.append({
            "file": receipt_file.name,
            "status": result["status"],
            "data": result.get("data")
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 TEST SUMMARY")
    print(f"{'='*60}")
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")
    print(f"📊 Success Rate: {successful/len(results)*100:.1f}%")
    print(f"{'='*60}\n")
    
    return results

# Add this new function
def process_and_save_receipt(image_path):
    """
    Complete pipeline: Image → OCR → AI → Google Sheets
    """
    print(f"\n{'='*60}")
    print(f"🎯 PROCESSING & SAVING: {image_path}")
    print(f"{'='*60}\n")
    
    # Step 1: Process receipt (existing function)
    result = process_receipt(image_path)
    
    if result['status'] != 'success':
        print(f"❌ Processing failed: {result.get('message')}")
        return result
    
    # Step 2: Save to Google Sheets
    print("\n💾 Saving to Google Sheets...")
    try:
        sheets_manager = SheetsManager()
        sheets_manager.add_expense(result['data'])
        print("✅ Saved to Google Sheets!")
    except Exception as e:
        print(f"⚠️  Warning: Could not save to sheets: {str(e)}")
        # Don't fail completely if sheets fails
    
    return result


# Update the test function at the bottom
def test_full_pipeline():
    """Test complete pipeline with Google Sheets"""
    # receipts_dir = Path("receipts")
    # receipt_files = list(receipts_dir.glob("*.jpg")) + list(receipts_dir.glob("*.png"))
    print(f"\n📁 Looking for receipts in: {RECEIPTS_DIR}")
    
    if not RECEIPTS_DIR.exists():
        print(f"❌ Receipts directory not found: {RECEIPTS_DIR}")
        print("💡 Creating directory...")
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ Directory created. Add some receipt images and try again.")
        return
    
    receipt_files = list(RECEIPTS_DIR.glob("*.jpg")) + list(RECEIPTS_DIR.glob("*.png"))
    
    if not receipt_files:
        print("❌ No receipt images found in receipts/ folder")
        return
    
    print(f"\n🧪 Testing FULL PIPELINE with {len(receipt_files)} receipt(s)\n")
    
    # Initialize sheets (create headers if needed)
    sheets_manager = SheetsManager()
    sheets_manager.setup_sheet()
    
    # Process each receipt
    for receipt_file in receipt_files:
        process_and_save_receipt(receipt_file)
        print()  # Blank line between receipts
    
    print(f"\n{'='*60}")
    print("✅ ALL RECEIPTS PROCESSED AND SAVED!")
    print(f"{'='*60}")
    print("\n🔗 Check your Google Sheet:")
    print(f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit")
    print()


if __name__ == "__main__":
    # Run full pipeline test
    test_full_pipeline()
    
# if __name__ == "__main__":
#     # Run tests
#     test_multiple_receipts()