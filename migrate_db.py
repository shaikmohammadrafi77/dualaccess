#!/usr/bin/env python3
"""
Database Migration Script for Dual Access Login Test
This script adds the 'deleted' and 'deleted_at' columns to the File table
"""

import os
import sqlite3
from datetime import datetime

def migrate_database():
    """Add deleted columns to the File table"""
    
    # Database path
    db_path = 'dual_access_cloud.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the application first to create the database.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'deleted' not in columns:
            print("Adding 'deleted' column to files table...")
            cursor.execute("ALTER TABLE files ADD COLUMN deleted BOOLEAN DEFAULT 0")
            print("✅ 'deleted' column added successfully!")
        else:
            print("✅ 'deleted' column already exists!")
            
        if 'deleted_at' not in columns:
            print("Adding 'deleted_at' column to files table...")
            cursor.execute("ALTER TABLE files ADD COLUMN deleted_at DATETIME")
            print("✅ 'deleted_at' column added successfully!")
        else:
            print("✅ 'deleted_at' column already exists!")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()
    print("\nPress Enter to exit...")
    input()
