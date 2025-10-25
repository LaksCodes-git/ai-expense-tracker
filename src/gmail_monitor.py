"""
Gmail API integration - monitor inbox for receipt emails
"""
import os
import base64
import pickle
from pathlib import Path
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailMonitor:
    """Monitor Gmail for receipt emails"""
    
    def __init__(self):
        """Initialize Gmail API"""
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth"""
        print("🔐 Authenticating with Gmail...")
        
        creds = None
        
        # Token file stores user's access and refresh tokens
        if GMAIL_TOKEN_PATH.exists():
            print("   Loading saved credentials...")
            creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH), SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("   Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                print("   Opening browser for authorization...")
                print("   📱 Check your browser and authorize the app")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(GMAIL_CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            print("   Saving credentials...")
            with open(GMAIL_TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Connected to Gmail")
    
    def get_unread_receipts(self):
        """
        Get unread emails with receipts
        Looking for emails with:
        - Subject containing: receipt, invoice, order
        - Has attachments (images or PDFs)
        - Is unread
        """
        print("\n📬 Checking for new receipt emails...")
        
        # Search query
        query = 'is:unread has:attachment (subject:receipt OR subject:invoice OR subject:order)'
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("   No new receipt emails found")
                return []
            
            print(f"   Found {len(messages)} potential receipt email(s)")
            
            # Get full message details
            receipt_emails = []
            for msg in messages:
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                receipt_emails.append(full_msg)
            
            return receipt_emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {str(e)}")
            return []
    
    def get_attachments(self, message):
        """Extract attachments from email message"""
        attachments = []
        
        # Get message payload
        payload = message.get('payload', {})
        
        # Check parts for attachments
        parts = payload.get('parts', [])
        
        for part in parts:
            if part.get('filename'):
                filename = part['filename']
                
                # Only get image/PDF attachments
                mime_type = part.get('mimeType', '')
                if not any(t in mime_type for t in ['image', 'pdf']):
                    continue
                
                # Get attachment data
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = self.service.users().messages().attachments().get(
                        userId='me',
                        messageId=message['id'],
                        id=att_id
                    ).execute()
                    data = att['data']
                
                # Decode
                file_data = base64.urlsafe_b64decode(data)
                
                attachments.append({
                    'filename': filename,
                    'data': file_data,
                    'mime_type': mime_type
                })
        
        return attachments
    
    def mark_as_read(self, message_id):
        """Mark email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"⚠️  Could not mark as read: {str(e)}")
            return False
    
    def send_confirmation(self, to_email, expense_data):
        """Send confirmation email after processing receipt"""
        vendor = expense_data.get('vendor', 'Unknown')
        total = expense_data.get('total', 0)
        currency = expense_data.get('currency', 'INR')
        
        subject = f"✅ Receipt Processed: {vendor}"
        body = f"""Your receipt has been processed successfully!

Vendor: {vendor}
Amount: {currency} {total}
Category: {expense_data.get('category', 'Other')}
Date: {expense_data.get('date', 'Unknown')}

Your expense has been added to your Google Sheet.

- ReceiptToBooks
"""
        
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✅ Confirmation email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not send confirmation: {str(e)}")
            return False


def test_gmail():
    """Test Gmail connection"""
    print("\n" + "="*60)
    print("🧪 TESTING GMAIL CONNECTION")
    print("="*60 + "\n")
    
    # Initialize
    monitor = GmailMonitor()
    
    # Check for receipts
    emails = monitor.get_unread_receipts()
    
    print(f"\n📊 Found {len(emails)} receipt email(s)")
    
    if emails:
        print("\n📋 Email details:")
        for email in emails:
            # Get subject
            headers = email['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            print(f"\n  From: {sender}")
            print(f"  Subject: {subject}")
            
            # Check attachments
            attachments = monitor.get_attachments(email)
            print(f"  Attachments: {len(attachments)}")
            for att in attachments:
                print(f"    - {att['filename']} ({att['mime_type']})")
    
    print("\n" + "="*60)
    print("✅ GMAIL TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_gmail()