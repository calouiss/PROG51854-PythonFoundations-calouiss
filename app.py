# Library Management System - Assignment 1 & 2
# Assignment 1: GET /items, /health with logging
# Assignment 2: Full CRUD for Books, Readers, Staff + OOP + Monitoring

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from collections import defaultdict
from typing import Dict
import os, logging, time

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Library Management System: Assignment 2",
    contact={
        "name": "Cynthia Ann Louis Banu",
        "email": "banuc@sheridancollege.ca"
    },
)

# ------ models ------
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


# ------- OOP Managers -------
class BaseManager:
    def __init__(self, filename, header):
        self.filename = filename
        self.header = header
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(",".join(header) + "\n")

    def _read(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return [ln.strip().split(",") for ln in f.readlines()[1:] if ln.strip()]

    def _write(self, rows):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(",".join(self.header) + "\n")
            for r in rows:
                f.write(",".join(r) + "\n")

    def list_all(self):
        return self._read()

    def get_one(self, id_):
        for r in self._read():
            if r[0] == id_:
                return r
        return None

    def add(self, data):
        rows = self._read()
        nid = str(max([int(r[0]) for r in rows]) + 1) if rows else "1"
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"{nid},{','.join(data)}\n")
        return nid

    def update(self, id_, data):
        rows, ok = self._read(), False
        for i, r in enumerate(rows):
            if r[0] == id_:
                rows[i] = [id_] + data
                ok = True
                break
        if ok:
            self._write(rows)
        return ok

    def delete(self, id_):
        rows = self._read()
        kept = [r for r in rows if r[0] != id_]
        if len(kept) == len(rows):
            return False
        self._write(kept)
        return True


# Managers for each entity
books = BaseManager("books.csv", ["id", "title", "author", "isbn", "year", "available"])
readers = BaseManager("readers.csv", ["id", "name", "email", "membership_id", "membership_type", "join_date"])
staff = BaseManager("staff.csv", ["id", "name", "position", "email", "phone", "hire_date"])


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


# ====== Assignment 2 ======
# ---- Books ----
@app.get("/books")
def list_books():
    rows = books.list_all()
    return {"books": [
        {"id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "year": r[4], "available": r[5]} for r in rows
    ]}

@app.get("/books/{book_id}")
def get_book(book_id: str):
    r = books.get_one(book_id)
    if r:
        return {"id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "year": r[4], "available": r[5]}
    raise HTTPException(404, "Book not found")

@app.post("/books", status_code=201)
def add_book(b: Book):
    nid = books.add([b.title, b.author, b.isbn, b.year, b.available])
    return {"id": nid, "title": b.title}

@app.put("/books/{book_id}")
def update_book(book_id: str, b: Book):
    if books.update(book_id, [b.title, b.author, b.isbn, b.year, b.available]):
        return {"message": "Book updated"}
    raise HTTPException(404, "Book not found")

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: str):
    if books.delete(book_id):
        return None
    raise HTTPException(404, "Book not found")


# ----Readers----
@app.get("/readers")
def list_readers():
    rows = readers.list_all()
    return {"readers": [
        {"id": r[0], "name": r[1], "email": r[2], "membership_id": r[3], "membership_type": r[4], "join_date": r[5]} for r in rows
    ]}

@app.get("/readers/{reader_id}")
def get_reader(reader_id: str):
    r = readers.get_one(reader_id)
    if r:
        return {"id": r[0], "name": r[1], "email": r[2], "membership_id": r[3], "membership_type": r[4], "join_date": r[5]}
    raise HTTPException(404, "Reader not found")

@app.post("/readers", status_code=201)
def add_reader(a: Reader):
    nid = readers.add([a.name, a.email, a.membership_id, a.membership_type, a.join_date])
    return {"id": nid, "name": a.name}

@app.put("/readers/{reader_id}")
def update_reader(reader_id: str, a: Reader):
    if readers.update(reader_id, [a.name, a.email, a.membership_id, a.membership_type, a.join_date]):
        return {"message": "Reader updated"}
    raise HTTPException(404, "Reader not found")

@app.delete("/readers/{reader_id}", status_code=204)
def delete_reader(reader_id: str):
    if readers.delete(reader_id):
        return None
    raise HTTPException(404, "Reader not found")


# ----Staff----
@app.get("/staff")
def list_staff():
    rows = staff.list_all()
    return {"staff": [
        {"id": r[0], "name": r[1], "position": r[2], "email": r[3], "phone": r[4], "hire_date": r[5]} for r in rows
    ]}

@app.get("/staff/{staff_id}")
def get_staff(staff_id: str):
    r = staff.get_one(staff_id)
    if r:
        return {"id": r[0], "name": r[1], "position": r[2], "email": r[3], "phone": r[4], "hire_date": r[5]}
    raise HTTPException(404, "Staff not found")

@app.post("/staff", status_code=201)
def add_staff(s: Staff):
    nid = staff.add([s.name, s.position, s.email, s.phone, s.hire_date])
    return {"id": nid, "name": s.name}

@app.put("/staff/{staff_id}")
def update_staff(staff_id: str, s: Staff):
    if staff.update(staff_id, [s.name, s.position, s.email, s.phone, s.hire_date]):
        return {"message": "Staff updated"}
    raise HTTPException(404, "Staff not found")

@app.delete("/staff/{staff_id}", status_code=204)
def delete_staff(staff_id: str):
    if staff.delete(staff_id):
        return None
    raise HTTPException(404, "Staff not found")


if __name__ == "__main__":
    import uvicorn
    logging.info("Library Management System")
    uvicorn.run(app, host="127.0.0.1", port=8000)