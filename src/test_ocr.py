"""
Test if Tesseract OCR can extract text from receipts
"""
import pytesseract
from PIL import Image
import sys
from pathlib import Path

# Import config
from config import RECEIPTS_DIR


def test_ocr(image_path):
    """Extract text from receipt image"""
    # Convert to Path
    image_path = Path(image_path)
    
    print(f"📄 Processing: {image_path.name}")
    print(f"   Full path: {image_path}")
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
    receipt_path = RECEIPTS_DIR / "test1.jpg"
    
    if not receipt_path.exists():
        print(f"❌ Receipt not found: {receipt_path}")
        print(f"💡 Add a receipt image to {RECEIPTS_DIR}/test1.jpg")
        
        # List available receipts
        available = list(RECEIPTS_DIR.glob("*.jpg")) + list(RECEIPTS_DIR.glob("*.png"))
        if available:
            print(f"\n📋 Available receipts:")
            for f in available:
                print(f"   - {f.name}")
            print(f"\n💡 Try: python src/test_ocr.py")
        sys.exit(1)
    
    test_ocr(receipt_path)