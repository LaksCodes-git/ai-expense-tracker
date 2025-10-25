#!/usr/bin/env python3
"""
ReceiptToBooks - Simple runner script
"""
import sys
from src.email_processor import EmailProcessor

def main():
    """Run the email processor"""
    processor = EmailProcessor()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        # Run continuously
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        processor.run_continuous(interval)
    else:
        # Run once
        processor.run_once()

if __name__ == "__main__":
    main()