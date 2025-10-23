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

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def process_receipt(image_path):
    """
    Complete pipeline: Receipt image → Structured JSON
    """
    print(f"\n{'='*60}")
    print(f"🎯 PROCESSING: {image_path}")
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
    receipts_dir = Path("/Users/lakshmi/codeworkspace/ASPIRATIONAL/ai-expense-tracker/receipts")
    receipt_files = list(receipts_dir.glob("*.jpg")) + list(receipts_dir.glob("*.png"))
    
    if not receipt_files:
        print("❌ No receipt images found in receipts/ folder")
        print("💡 Add some receipt images (jpg/png) to test")
        return
    
    print(f"\n🧪 Testing with {len(receipt_files)} receipt(s)\n")
    
    results = []
    for receipt_file in receipt_files:
        result = process_receipt(receipt_file)
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

if __name__ == "__main__":
    # Run tests
    test_multiple_receipts()