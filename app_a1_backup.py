# Library Management System - Assignment 1
# Simple FastAPI application with logging and health check

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging - similar to Ex4_2BasicLoggingWithFile.py
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
    #placeholder for timestamp :%(asctime)s
    #placeholder for level: %(levelname)s
    #placeholder for message:%(message)s
)

# Create FastAPI app
app = FastAPI()

# Route to get all books - similar to Ex4_3FlaskJson.py
@app.get("/items")
def get_items():
    logging.info("Request: GET /items")
    
    try:
        # Read books from file
        with open('books.txt', 'r') as file:
            books = [line.strip() for line in file if line.strip()]
        
        logging.info(f"Response: 200 OK - Returned {len(books)} books")
        return JSONResponse(content=books, status_code=200)
    
    except FileNotFoundError:
        logging.error("Response: 404 - books.txt file not found")
        return JSONResponse(content={"error": "Books file not found"}, status_code=404)
    
    except Exception as e:
        logging.error(f"Response: 500 - Error: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

# Health check endpoint
@app.get("/health")
def health_check():
    logging.info("Request: GET /health")
    logging.info("Response: 200 OK - Health check passed")
    return JSONResponse(content={"status": "ok"}, status_code=200)

# Run the application
if __name__ == "__main__":
    import uvicorn
    logging.info("Starting Library Management System API")
    uvicorn.run(app, host="127.0.0.1", port=8000)