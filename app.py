# Library Management System - Assignments 1, 2, 3 & 4
# Assignment 1: GET /items, /health with logging
# Assignment 2: Full CRUD + OOP + Monitoring
# Assignment 3: Database Integration and JSON Handling
# Assignment 4: Security, Compliance, and Metrics Simulation

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, ValidationError
from collections import defaultdict
from typing import Dict
import os, logging, time, sqlite3, json
from datetime import datetime, timedelta
from jose import jwt

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

# ====== Assignment 4 ======

# ---- Secrets Management ----
def get_secret(secret_name, secrets_file="secrets.json"):
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        return secrets.get(secret_name)
    except Exception as e:
        logging.error(f"Secrets error: {e}")
        return None

# ---- Input Validation ----
class SecureBook(BaseModel):
    title: str
    author: str
    stock: int

def validate_book_data(data):
    try:
        book = SecureBook(**data)
        return True, book.dict()
    except ValidationError as e:
        return False, str(e)

# ---- JWT Simulation ----
SECRET_KEY = "supersecretkey"

def create_jwt(payload):
    payload["exp"] = datetime.utcnow() + timedelta(minutes=10)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True, decoded
    except Exception as e:
        return False, str(e)

# ---- Compliance Check ----
def check_compliance(resource):
    if resource.get("encrypted"):
        return "COMPLIANT"
    return "NON_COMPLIANT"

def evaluate_all_resources(resources):
    results = {}
    for r in resources:
        results[r["name"]] = check_compliance(r)
    return results

# ---- Metrics ----
a4_metrics = {"api_requests": 0, "errors": 0}

def log_event(message, is_error=False):
    logging.info(message)
    a4_metrics["api_requests"] += 1
    if is_error:
        a4_metrics["errors"] += 1

# ---- Optional Remediation ----
def remediate(resource):
    if not resource.get("encrypted"):
        resource["encrypted"] = True
        log_event(f"Resource {resource['name']} remediated")
    return resource

# ---- Endpoints ----
@app.get("/assignment4/secrets")
def get_secret_endpoint():
    return {"DatabasePassword": get_secret("DatabasePassword")}

@app.post("/assignment4/validate")
def validate_endpoint(data: dict):
    return validate_book_data(data)

@app.get("/assignment4/token")
def token_endpoint():
    return {"token": create_jwt({"user": "student"})}

@app.post("/assignment4/verify")
def verify_endpoint(body: dict):
    return verify_jwt(body.get("token"))

@app.get("/assignment4/compliance")
def compliance_endpoint():
    resources = [
        {"name": "bucket1", "encrypted": True},
        {"name": "bucket2", "encrypted": False},
        {"name": "bucket3", "encrypted": False}
    ]
    return evaluate_all_resources(resources)

@app.get("/assignment4/metrics")
def metrics_endpoint():
    log_event("Metrics accessed")
    return a4_metrics

@app.get("/assignment4/remediate")
def remediate_endpoint():
    resource = {"name": "bucket2", "encrypted": False}
    return remediate(resource)


# ---- Dashboard ----
@app.get("/assignment4/dashboard", response_class=HTMLResponse)
def dashboard_charts():

    import plotly.graph_objects as go
    import plotly.express as px

    # -------- DATA --------
    statuses = ["200 OK", "301 Redirect", "404 Not Found", "500 Server Error"]
    counts   = [120, 25, 15, 5]

    days     = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
    totals   = [50, 60, 55, 70, 60]
    errors   = [5, 7, 6, 8, 5]

    # -------- BAR CHART --------
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=statuses, y=counts,
                             marker_color=["green", "blue", "orange", "red"]))
    bar_fig.update_layout(title="Status Code Counts", height=350)

    # -------- PIE CHART --------
    pie_fig = px.pie(
        names=statuses,
        values=counts,
        title="Status Distribution",
        color=statuses,
        color_discrete_map={
            "200 OK": "green",
            "301 Redirect": "blue",
            "404 Not Found": "orange",
            "500 Server Error": "red"
        }
    )
    pie_fig.update_layout(height=350)

    # -------- LINE CHART --------
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=days, y=totals,
                                  mode="lines+markers",
                                  name="Total Requests"))
    line_fig.add_trace(go.Scatter(x=days, y=errors,
                                  mode="lines+markers",
                                  name="Error Requests"))
    line_fig.update_layout(title="Requests Over Time", height=350)

    # -------- HTML PAGE --------
    return f"""
    <html>
    <head>
        <title>Assignment 4 Dashboard</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            .chart-row {{ display: flex; gap: 30px; }}
        </style>
    </head>
    <body>
        <h1>Assignment 4 Dashboard</h1>

        <div class="chart-row">
            <div>{bar_fig.to_html(include_plotlyjs='cdn', full_html=False)}</div>
            <div>{pie_fig.to_html(include_plotlyjs=False, full_html=False)}</div>
        </div>

        <div style="margin-top: 20px;">
            {line_fig.to_html(include_plotlyjs=False, full_html=False)}
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    logging.info("Library Management System - Assignments 1, 2, 3 & 4")
    uvicorn.run(app, host="127.0.0.1", port=8000)
