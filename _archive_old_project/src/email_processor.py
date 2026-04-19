#!/usr/bin/env python3
"""
Email Processing Pipeline for Nuclear Safe Room
Integrates email data extraction and processing into the voice analysis system
"""

import csv
import sqlite3
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter

class EmailProcessor:
    """Processes email data for voice analysis"""

    def __init__(self, status_tracking_path: str, extracted_emails_path: str):
        self.status_tracking_path = Path(status_tracking_path)
        self.extracted_emails_path = Path(extracted_emails_path)

        # Validate files exist
        if not self.status_tracking_path.exists():
            raise FileNotFoundError(f"Status tracking file not found: {status_tracking_path}")
        if not self.extracted_emails_path.exists():
            raise FileNotFoundError(f"Extracted emails file not found: {extracted_emails_path}")

    def load_status_tracking(self) -> Dict[int, str]:
        """Load email status tracking data"""
        status_map = {}

        try:
            with open(self.status_tracking_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email_id = int(row['email_id'])
                    status = row['status']
                    status_map[email_id] = status
        except Exception as e:
            print(f"⚠️  Error loading status tracking: {e}")

        return status_map

    def load_extracted_emails(self) -> Dict[int, Dict]:
        """Load extracted emails data"""
        emails = {}

        try:
            # Use pandas for efficient processing of large CSV
            df = pd.read_csv(self.extracted_emails_path)

            for _, row in df.iterrows():
                email_id = int(row['unique_id'])
                emails[email_id] = {
                    'subject': str(row.get('subject', '')) if not pd.isna(row.get('subject')) else '',
                    'content': str(row.get('content', '')) if not pd.isna(row.get('content')) else '',
                    'date': str(row.get('date', '')) if not pd.isna(row.get('date')) else '',
                    'from': str(row.get('from', '')) if not pd.isna(row.get('from')) else '',
                    'to': str(row.get('to', '')) if not pd.isna(row.get('to')) else '',
                    'message_id': str(row.get('message-id', '')) if not pd.isna(row.get('message-id')) else '',
                    'references': str(row.get('references', '')) if not pd.isna(row.get('references')) else '',
                    'in_reply_to': str(row.get('in-reply-to', '')) if not pd.isna(row.get('in-reply-to')) else ''
                }
        except Exception as e:
            print(f"⚠️  Error loading extracted emails: {e}")

        return emails

    def filter_human_emails(self, status_map: Dict[int, str], emails: Dict[int, Dict]) -> List[Dict]:
        """Filter to get only human-written emails by Omar"""
        human_emails = []

        for email_id, status in status_map.items():
            if status == 'human' and email_id in emails:
                email_data = emails[email_id].copy()
                email_data['email_id'] = email_id
                email_data['status'] = status

                # The status tracking already identified these as human emails by Omar
                # No need to re-filter by from field
                human_emails.append(email_data)

        print(f"📧 Found {len(human_emails)} human emails by Omar")
        return human_emails

    def extract_email_content_for_analysis(self, emails: List[Dict]) -> List[str]:
        """Extract text content from emails for linguistic analysis"""
        texts = []

        for email in emails:
            content = email.get('content', '')
            subject = email.get('subject', '')

            # Handle NaN values
            if pd.isna(content):
                content = ''
            if pd.isna(subject):
                subject = ''

            # Combine subject and content
            full_text = f"{subject}\n{content}" if subject and content else content or subject

            # Clean up email content
            full_text = self._clean_email_text(full_text)

            if full_text.strip():
                texts.append(full_text)

        print(f"📝 Extracted {len(texts)} text samples from emails")
        return texts

    def _clean_email_text(self, text: str) -> str:
        """Clean email text for analysis"""
        # Remove email headers and signatures
        text = re.sub(r'^On.*wrote:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^-+.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Sent from.*$', '', text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove quoted text
        text = re.sub(r'>.*$', '', text, flags=re.MULTILINE)

        return text

    def get_email_statistics(self, emails: List[Dict]) -> Dict:
        """Get statistics about the email dataset"""
        stats = {
            'total_emails': len(emails),
            'total_words': 0,
            'total_characters': 0,
            'date_range': {'earliest': None, 'latest': None},
            'unique_recipients': set(),
            'email_threads': 0
        }

        dates = []
        for email in emails:
            content = email.get('content', '')
            if pd.isna(content):
                content = ''
            words = len(str(content).split())
            chars = len(str(content))

            stats['total_words'] += words
            stats['total_characters'] += chars

            # Extract date
            date_str = email.get('date', '')
            if date_str:
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %z']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            dates.append(date_obj)
                            break
                        except ValueError:
                            continue
                except:
                    pass

            # Extract recipients
            to_field = email.get('to', '')
            if to_field:
                recipients = [r.strip() for r in to_field.split(',')]
                stats['unique_recipients'].update(recipients)

            # Check if this is a reply (thread)
            if email.get('in_reply_to') or email.get('references'):
                stats['email_threads'] += 1

        # Calculate date range
        if dates:
            stats['date_range']['earliest'] = min(dates).isoformat()
            stats['date_range']['latest'] = max(dates).isoformat()

        stats['unique_recipients'] = len(stats['unique_recipients'])

        return stats

    def process_emails_for_voice_analysis(self) -> Tuple[List[str], Dict]:
        """Main processing method - returns texts and statistics"""
        print("🔍 Processing email data for voice analysis...")

        # Load data
        status_map = self.load_status_tracking()
        emails = self.load_extracted_emails()

        print(f"📊 Loaded {len(status_map)} status records and {len(emails)} emails")

        # Filter human emails
        human_emails = self.filter_human_emails(status_map, emails)

        # Extract content
        texts = self.extract_email_content_for_analysis(human_emails)

        # Get statistics
        stats = self.get_email_statistics(human_emails)

        print(f"✅ Email processing complete")
        print(f"   - Total human emails: {stats['total_emails']}")
        print(f"   - Total words: {stats['total_words']:,}")
        print(f"   - Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")

        return texts, stats


def main():
    """Test email processing"""
    # Email file paths
    status_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/status_tracking.csv"
    emails_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"

    try:
        processor = EmailProcessor(status_path, emails_path)
        texts, stats = processor.process_emails_for_voice_analysis()

        print(f"\n📧 Email Statistics:")
        print(f"   Total emails: {stats['total_emails']}")
        print(f"   Total words: {stats['total_words']:,}")
        print(f"   Total characters: {stats['total_characters']:,}")
        print(f"   Unique recipients: {stats['unique_recipients']}")
        print(f"   Email threads: {stats['email_threads']}")
        print(f"   Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")

        # Sample of extracted text
        if texts:
            print(f"\n📝 Sample extracted text (first 200 chars):")
            print(f"   {texts[0][:200]}...")

    except Exception as e:
        print(f"❌ Error processing emails: {e}")


if __name__ == "__main__":
    main()
