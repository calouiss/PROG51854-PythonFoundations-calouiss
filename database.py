# Database setup for Assignment 3

import sqlite3
import csv

DATABASE = "library.db"

def create_tables():
    # Create connection
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books(
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT,
        year TEXT,
        available TEXT)
    ''')
    
    # Create readers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readers(
        reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        membership_id TEXT,
        membership_type TEXT,
        join_date TEXT)
    ''')
    
    # Create staff table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff(
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        hire_date TEXT)
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables created successfully")

def migrate_csv_to_db():
    # Migrate data from CSV to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Migrate books
    try:
        with open('books.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("INSERT INTO books (title, author, isbn, year, available) VALUES (?, ?, ?, ?, ?)",
                             (row['title'], row['author'], row['isbn'], row['year'], row['available']))
        conn.commit()
        print("Books migrated")
    except Exception as e:
        print(f"Error migrating books: {e}")
    
    # Migrate readers
    try:
        with open('readers.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("INSERT INTO readers (name, email, membership_id, membership_type, join_date) VALUES (?, ?, ?, ?, ?)",
                             (row['name'], row['email'], row['membership_id'], row['membership_type'], row['join_date']))
        conn.commit()
        print("Readers migrated")
    except Exception as e:
        print(f"Error migrating readers: {e}")
    
    # Migrate staff
    try:
        with open('staff.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("INSERT INTO staff (name, position, email, phone, hire_date) VALUES (?, ?, ?, ?, ?)",
                             (row['name'], row['position'], row['email'], row['phone'], row['hire_date']))
        conn.commit()
        print("Staff migrated")
    except Exception as e:
        print(f"Error migrating staff: {e}")
    
    conn.close()
    print("Migration completed")

if __name__ == "__main__":
    create_tables()
    migrate_csv_to_db()