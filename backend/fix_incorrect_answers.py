#!/usr/bin/env python3
"""
Script to fix incorrect answers in the database and regenerate explanations.
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

def fix_incorrect_answers():
    """Fix incorrect answers in the database"""
    try:
        # Get all existing records
        records = get_all_records()
        print(f"Found {len(records)} records to check")
        
        if not records:
            print("No records to check")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fixed_count = 0
        
        for record in records:
            penalty_a = record.get('penalty_a', '')
            penalty_b = record.get('penalty_b', '')
            
            # Check for incorrect answers
            needs_fix = False
            new_penalty_a = penalty_a
            new_penalty_b = penalty_b
            
            # Fix "S" to "Yes" for Minimum Value Standards
            if penalty_b == 'S':
                print(f"Fixing record {record['id']}: penalty_b from 'S' to 'Yes'")
                new_penalty_b = 'Yes'
                needs_fix = True
            
            # Fix any other invalid answers
            if penalty_a not in ['Yes', 'No']:
                print(f"Fixing record {record['id']}: penalty_a from '{penalty_a}' to 'Unknown'")
                new_penalty_a = 'Unknown'
                needs_fix = True
                
            if penalty_b not in ['Yes', 'No'] and penalty_b != 'S':
                print(f"Fixing record {record['id']}: penalty_b from '{penalty_b}' to 'Unknown'")
                new_penalty_b = 'Unknown'
                needs_fix = True
            
            if needs_fix:
                # Generate new explanations based on corrected answers
                explanations = generate_penalty_explanation(
                    record['group_name'],
                    new_penalty_a,
                    new_penalty_b,
                    f"Company: {record['group_name']}, Essential Coverage: {new_penalty_a}, Value Standards: {new_penalty_b}"
                )
                
                # Update the record in the database
                if hasattr(conn, 'execute'):  # SQLite
                    cursor.execute('''
                        UPDATE sbc_records 
                        SET penalty_a = ?, penalty_b = ?, 
                            penalty_a_explanation = ?, penalty_b_explanation = ?
                        WHERE id = ?
                    ''', (new_penalty_a, new_penalty_b, 
                          explanations['penalty_a_explanation'], 
                          explanations['penalty_b_explanation'], 
                          record['id']))
                else:  # PostgreSQL
                    cursor.execute('''
                        UPDATE sbc_records 
                        SET penalty_a = %s, penalty_b = %s, 
                            penalty_a_explanation = %s, penalty_b_explanation = %s
                        WHERE id = %s
                    ''', (new_penalty_a, new_penalty_b, 
                          explanations['penalty_a_explanation'], 
                          explanations['penalty_b_explanation'], 
                          record['id']))
                
                fixed_count += 1
            else:
                print(f"Record {record['id']}: {record['group_name']} - No fixes needed")
        
        conn.commit()
        conn.close()
        
        print(f"Successfully fixed {fixed_count} records")
        
    except Exception as e:
        print(f"Error fixing records: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_incorrect_answers()
