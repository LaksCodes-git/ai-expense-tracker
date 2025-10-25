"""
Email-to-Sheet Pipeline: Monitor Gmail → Process Receipts → Update Sheets
"""
import time
from pathlib import Path
from datetime import datetime

from config import RECEIPTS_DIR
from gmail_monitor import GmailMonitor
from process_receipt import process_receipt
from sheets_helper import SheetsManager


class EmailProcessor:
    """Process receipt emails automatically"""
    
    def __init__(self):
        """Initialize all services"""
        print("🚀 Initializing ReceiptToBooks Email Processor...")
        print()
        
        self.gmail = GmailMonitor()
        self.sheets = SheetsManager()
        
        # Make sure receipts directory exists
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        
        print("✅ All services ready")
        print()
    
    def process_single_email(self, email):
        """Process one receipt email"""
        # Get email details
        headers = email['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        email_id = email['id']
        
        print(f"\n{'='*60}")
        print(f"📧 Processing email:")
        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        print(f"{'='*60}\n")
        
        # Get attachments
        attachments = self.gmail.get_attachments(email)
        
        if not attachments:
            print("⚠️  No image attachments found, skipping")
            return False
        
        # Process each attachment
        success_count = 0
        for att in attachments:
            print(f"\n📎 Processing attachment: {att['filename']}")
            
            # Save attachment temporarily
            temp_path = RECEIPTS_DIR / f"temp_{datetime.now().timestamp()}_{att['filename']}"
            with open(temp_path, 'wb') as f:
                f.write(att['data'])
            
            try:
                # Process receipt
                result = process_receipt(temp_path)
                
                if result['status'] == 'success':
                    # Save to sheets
                    self.sheets.add_expense(result['data'])
                    print(f"✅ Receipt processed and saved!")
                    success_count += 1
                else:
                    print(f"❌ Processing failed: {result.get('message')}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
        
        # Mark email as read
        if success_count > 0:
            self.gmail.mark_as_read(email_id)
            
            # Send confirmation (extract sender email)
            sender_email = sender.split('<')[-1].strip('>')
            expense_data = result.get('data', {})
            self.gmail.send_confirmation(sender_email, expense_data)
        
        return success_count > 0
    
    def run_once(self):
        """Check for new emails and process them (one-time run)"""
        print("\n🔍 Checking for new receipt emails...\n")
        
        # Get unread receipts
        emails = self.gmail.get_unread_receipts()
        
        if not emails:
            print("✨ No new receipts to process")
            return 0
        
        print(f"📬 Found {len(emails)} receipt email(s) to process\n")
        
        # Process each email
        processed = 0
        for email in emails:
            if self.process_single_email(email):
                processed += 1
        
        print(f"\n{'='*60}")
        print(f"📊 SUMMARY: Processed {processed}/{len(emails)} email(s)")
        print(f"{'='*60}\n")
        
        return processed
    
    def run_continuous(self, interval=60):
        """Monitor continuously (check every N seconds)"""
        print(f"\n🔄 Starting continuous monitoring (checking every {interval}s)")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_once()
                print(f"😴 Sleeping for {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Stopping email processor...")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("📧 RECEIPTTOBOOKS EMAIL PROCESSOR")
    print("="*60 + "\n")
    
    processor = EmailProcessor()
    
    # Run once for testing
    processor.run_once()


if __name__ == "__main__":
    main()