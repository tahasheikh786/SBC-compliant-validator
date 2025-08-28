#!/usr/bin/env python3
"""
Script to update existing SBC records with smart explanations.
This is needed because existing records were created before the explanation feature was added.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_all_records, get_db_connection
from pdf_processor import generate_penalty_explanation

load_dotenv()

def update_existing_records():
    """Update existing records with explanations"""
    try:
        # Get all existing records
        records = get_all_records()
        print(f"Found {len(records)} existing records to update")
        
        if not records:
            print("No records to update")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updated_count = 0
        
        for record in records:
            # Skip records that already have explanations
            if (record.get('penalty_a_explanation') and 
                record.get('penalty_b_explanation') and 
                len(record['penalty_a_explanation']) > 10 and 
                len(record['penalty_b_explanation']) > 10):
                print(f"Skipping record {record['id']} - already has explanations")
                continue
            
            print(f"Updating record {record['id']}: {record['group_name']}")
            
            # Generate explanations based on the penalty values
            # Since we don't have the original PDF text, we'll generate based on the known answers
            explanations = generate_penalty_explanation(
                record['group_name'],
                record['penalty_a'],
                record['penalty_b'],
                f"Company: {record['group_name']}, Essential Coverage: {record['penalty_a']}, Value Standards: {record['penalty_b']}"
            )
            
            # Update the record in the database
            if hasattr(conn, 'execute'):  # SQLite
                cursor.execute('''
                    UPDATE sbc_records 
                    SET penalty_a_explanation = ?, penalty_b_explanation = ?
                    WHERE id = ?
                ''', (explanations['penalty_a_explanation'], explanations['penalty_b_explanation'], record['id']))
            else:  # PostgreSQL
                cursor.execute('''
                    UPDATE sbc_records 
                    SET penalty_a_explanation = %s, penalty_b_explanation = %s
                    WHERE id = %s
                ''', (explanations['penalty_a_explanation'], explanations['penalty_b_explanation'], record['id']))
            
            updated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"Successfully updated {updated_count} records with explanations")
        
    except Exception as e:
        print(f"Error updating records: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_existing_records()
