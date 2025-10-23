"""
Test if Tesseract OCR can extract text from receipts
"""
import pytesseract
from PIL import Image
import sys
from pathlib import Path

def test_ocr(image_path):
    """Extract text from receipt image"""
    print(f"📄 Processing: {image_path}")
    print("=" * 60)
    
    try:
        # Open image
        image = Image.open(image_path)
        print(f"✅ Image loaded: {image.size[0]}x{image.size[1]} pixels")
        
        # Extract text
        print("🔍 Running OCR...")
        text = pytesseract.image_to_string(image)
        
        # Display results
        print("\n📝 EXTRACTED TEXT:")
        print("=" * 60)
        print(text)
        print("=" * 60)
        
        # Basic validation
        if len(text.strip()) > 0:
            print(f"\n✅ SUCCESS! Extracted {len(text)} characters")
            return text
        else:
            print("\n⚠️  WARNING: No text extracted")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with the receipt image
    receipt_path = Path("/Users/lakshmi/codeworkspace/ASPIRATIONAL/ai-expense-tracker/receipts/test1.jpg")
    
    if not receipt_path.exists():
        print(f"❌ Receipt not found: {receipt_path}")
        print("💡 Add a receipt image to receipts/test1.jpg")
        sys.exit(1)
    
    test_ocr(receipt_path)