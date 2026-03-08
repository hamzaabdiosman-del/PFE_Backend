# FastAPI Backend for Care Database

This is a FastAPI backend for the 'care' MySQL database.

## Prerequisites

- Python 3.8+
- MySQL (via XAMPP)
- The 'care' database imported in phpMyAdmin

## Installation

1. Install Python from https://www.python.org/downloads/

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

1. Ensure XAMPP MySQL is running.

2. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

3. Open http://127.0.0.1:8000/docs for the interactive API documentation.

## API Endpoints

- **Clients**: `/clients/` (GET, POST), `/clients/{id}` (GET, PUT, DELETE)
- **Commandes**: `/commandes/` (GET, POST), `/commandes/{user_id}/{produit_id}` (GET, PUT, DELETE)
- **Details Commande**: `/details_commande/` (GET, POST), `/details_commande/{id}` (GET, PUT, DELETE)
- **Paiements**: `/paiements/` (GET, POST), `/paiements/{id}` (GET, PUT, DELETE)
- **Services**: `/services/` (GET, POST), `/services/{id}` (GET, PUT, DELETE)

## Database Configuration

Update `database.py` if your MySQL credentials differ:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost/care"
```