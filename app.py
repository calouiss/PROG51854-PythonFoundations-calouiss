# Library Management System - Assignments 1, 2, 3
# Assignment 1: GET /items, /health with logging
# Assignment 2: Full CRUD + OOP + Monitoring
# Assignment 3: Database Integration and JSON Handling

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from collections import defaultdict
from typing import Dict
import os, logging, time, sqlite3

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Library Management System: Assignments 1, 2, 3",
    contact={
        "name": "Cynthia Ann Louis Banu",
        "email": "banuc@sheridancollege.ca"
    },
)

DATABASE = "library.db"

# ------ Models ------
class Book(BaseModel):
    title: str
    author: str
    isbn: str
    year: str
    available: str

class Reader(BaseModel):
    name: str
    email: str
    membership_id: str
    membership_type: str
    join_date: str

class Staff(BaseModel):
    name: str
    position: str
    email: str
    phone: str
    hire_date: str

# Database helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -----Monitoring-----
app.state.request_counts: Dict[str, int] = defaultdict(int)
app.state.error_count: int = 0
app.state.endpoint_error_counts: Dict[str, int] = defaultdict(int)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    method, path = request.method, request.url.path
    logging.info(f"{method} {path} - Request received")
    start = time.perf_counter()

    try:
        response = await call_next(request)
        duration = int((time.perf_counter() - start) * 1000)
        app.state.request_counts[f"{method} {path}"] += 1
        logging.info(f"{method} {path} - Response: {response.status_code} OK - {duration}ms")
        return response
    except Exception:
        app.state.error_count += 1
        app.state.endpoint_error_counts[path] += 1
        logging.exception(f"{method} {path} - ERROR (unhandled)")
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

@app.get("/metrics")
def metrics():
    return {
        "requests_per_endpoint": dict(app.state.request_counts),
        "errors_total": app.state.error_count,
        "errors_per_endpoint": dict(app.state.endpoint_error_counts),
    }

# ====== Assignment 1 ======
@app.get("/items")
def get_items():
    try:
        with open("books.txt", "r", encoding="utf-8") as f:
            books_data = [ln.strip() for ln in f if ln.strip()]
        logging.info(f"GET /items - Returned {len(books_data)} books")
        return books_data
    except FileNotFoundError:
        logging.error("books.txt not found")
        raise HTTPException(404, "Books file not found")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ====== Assignment 3 (Database) ======

# ---- Books ----
@app.get("/books")
def list_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    
    return {"books": [
        {"book_id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "year": r[4], "available": r[5]} 
        for r in rows
    ]}

@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE book_id=?", (book_id,))
    r = cursor.fetchone()
    conn.close()
    
    if r:
        return {"book_id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "year": r[4], "available": r[5]}
    raise HTTPException(404, "Book not found")

@app.post("/books", status_code=201)
def add_book(b: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, isbn, year, available) VALUES (?, ?, ?, ?, ?)",
                  (b.title, b.author, b.isbn, b.year, b.available))
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    return {"book_id": book_id, "title": b.title}

@app.put("/books/{book_id}")
def update_book(book_id: int, b: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET title=?, author=?, isbn=?, year=?, available=? WHERE book_id=?",
                  (b.title, b.author, b.isbn, b.year, b.available, book_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return {"message": "Book updated"}
    raise HTTPException(404, "Book not found")

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id=?", (book_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return None
    raise HTTPException(404, "Book not found")

# ----Readers----
@app.get("/readers")
def list_readers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readers")
    rows = cursor.fetchall()
    conn.close()
    
    return {"readers": [
        {"reader_id": r[0], "name": r[1], "email": r[2], "membership_id": r[3], "membership_type": r[4], "join_date": r[5]} 
        for r in rows
    ]}

@app.get("/readers/{reader_id}")
def get_reader(reader_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readers WHERE reader_id=?", (reader_id,))
    r = cursor.fetchone()
    conn.close()
    
    if r:
        return {"reader_id": r[0], "name": r[1], "email": r[2], "membership_id": r[3], "membership_type": r[4], "join_date": r[5]}
    raise HTTPException(404, "Reader not found")

@app.post("/readers", status_code=201)
def add_reader(a: Reader):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO readers (name, email, membership_id, membership_type, join_date) VALUES (?, ?, ?, ?, ?)",
                  (a.name, a.email, a.membership_id, a.membership_type, a.join_date))
    conn.commit()
    reader_id = cursor.lastrowid
    conn.close()
    return {"reader_id": reader_id, "name": a.name}

@app.put("/readers/{reader_id}")
def update_reader(reader_id: int, a: Reader):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE readers SET name=?, email=?, membership_id=?, membership_type=?, join_date=? WHERE reader_id=?",
                  (a.name, a.email, a.membership_id, a.membership_type, a.join_date, reader_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return {"message": "Reader updated"}
    raise HTTPException(404, "Reader not found")

@app.delete("/readers/{reader_id}", status_code=204)
def delete_reader(reader_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM readers WHERE reader_id=?", (reader_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return None
    raise HTTPException(404, "Reader not found")

# ----Staff----
@app.get("/staff")
def list_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff")
    rows = cursor.fetchall()
    conn.close()
    
    return {"staff": [
        {"staff_id": r[0], "name": r[1], "position": r[2], "email": r[3], "phone": r[4], "hire_date": r[5]} 
        for r in rows
    ]}

@app.get("/staff/{staff_id}")
def get_staff(staff_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,))
    r = cursor.fetchone()
    conn.close()
    
    if r:
        return {"staff_id": r[0], "name": r[1], "position": r[2], "email": r[3], "phone": r[4], "hire_date": r[5]}
    raise HTTPException(404, "Staff not found")

@app.post("/staff", status_code=201)
def add_staff(s: Staff):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO staff (name, position, email, phone, hire_date) VALUES (?, ?, ?, ?, ?)",
                  (s.name, s.position, s.email, s.phone, s.hire_date))
    conn.commit()
    staff_id = cursor.lastrowid
    conn.close()
    return {"staff_id": staff_id, "name": s.name}

@app.put("/staff/{staff_id}")
def update_staff(staff_id: int, s: Staff):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET name=?, position=?, email=?, phone=?, hire_date=? WHERE staff_id=?",
                  (s.name, s.position, s.email, s.phone, s.hire_date, staff_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return {"message": "Staff updated"}
    raise HTTPException(404, "Staff not found")

@app.delete("/staff/{staff_id}", status_code=204)
def delete_staff(staff_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return None
    raise HTTPException(404, "Staff not found")

if __name__ == "__main__":
    import uvicorn
    logging.info("Library Management System - Assignments 1, 2, 3")
    uvicorn.run(app, host="127.0.0.1", port=8000)