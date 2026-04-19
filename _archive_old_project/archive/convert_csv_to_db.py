#!/usr/bin/env python3
"""
Convert massive CSV to clean SQLite database
Just two columns: sender, content
"""

import csv
import sqlite3
import sys
import os
from pathlib import Path

def convert_csv_to_db():
    """Convert the massive email CSV to a clean database"""

    csv_file = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
    db_file = "/Users/khamel83/dev/Speech/emails_clean.db"

    print(f"Converting {csv_file} to {db_file}")

    # Increase CSV field size limit
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)

    # Create database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            content TEXT,
            is_omar INTEGER DEFAULT 0
        )
    ''')

    # Process CSV in chunks
    chunk_size = 10000
    processed_rows = 0
    omar_count = 0
    total_count = 0

    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)

        batch = []

        for row in reader:
            processed_rows += 1

            # Extract content
            content = ''
            for col_name in ['content', 'body', 'text', 'message', 'email_content']:
                if col_name in row and row[col_name]:
                    content = str(row[col_name]).strip()
                    break

            if content and len(content) > 20:  # Only substantial content
                # Extract sender info
                sender = ''
                for col_name in ['from', 'sender', 'Name']:
                    if col_name in row and row[col_name]:
                        sender = str(row[col_name]).strip()
                        break

                # Check if Omar
                is_omar = 0
                sender_lower = sender.lower()
                if any(name in sender_lower for name in ['omar', 'zoheri', '847', '312']):
                    is_omar = 1
                    omar_count += 1

                batch.append((sender, content, is_omar))
                total_count += 1

                # Insert batch
                if len(batch) >= chunk_size:
                    cursor.executemany(
                        'INSERT INTO emails (sender, content, is_omar) VALUES (?, ?, ?)',
                        batch
                    )
                    conn.commit()
                    batch = []
                    print(f"Processed {processed_rows:,} rows, saved {total_count:,} emails ({omar_count:,} from Omar)")

        # Insert remaining batch
        if batch:
            cursor.executemany(
                'INSERT INTO emails (sender, content, is_omar) VALUES (?, ?, ?)',
                batch
            )
            conn.commit()

    # Final stats
    cursor.execute('SELECT COUNT(*) FROM emails')
    total_emails = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM emails WHERE is_omar = 1')
    omar_emails = cursor.fetchone()[0]

    print(f"\n=== CONVERSION COMPLETE ===")
    print(f"Total emails: {total_emails:,}")
    print(f"Omar's emails: {omar_emails:,}")
    print(f"Database: {db_file}")

    conn.close()
    return db_file

if __name__ == "__main__":
    convert_csv_to_db()
