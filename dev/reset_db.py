"""
Simple database reset script
Deletes all data from transcripts and messages tables
"""

import os
import sys

# Add parent directory to path so we can import db
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db

def reset_database():
    """Reset the database by truncating all tables"""
    print("\n" + "="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60)
    print("\nThis will DELETE ALL DATA from:")
    print("  - transcripts table")
    print("  - messages table")
    print("\nThis action CANNOT be undone!")
    print("="*60)
    
    # Confirmation prompt
    response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nReset cancelled. No changes made.")
        return
    
    try:
        # Connect to database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("\nResetting database...")
        
        # Truncate tables and reset auto-increment counters
        # CASCADE removes dependent data
        cursor.execute("TRUNCATE TABLE transcripts, messages RESTART IDENTITY CASCADE;")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("DATABASE RESET SUCCESSFUL")
        print("="*60)
        print("All data has been deleted.")
        print("Auto-increment counters have been reset.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nERROR resetting database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    reset_database()

