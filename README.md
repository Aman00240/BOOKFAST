# BookFast API 🎟️

**BookFast** is a high-performance, asynchronous REST API for event ticketing, built with **FastAPI** and **PostgreSQL**.

It is designed to handle high-concurrency booking scenarios, ensuring data integrity during "flash sales" where multiple users attempt to book the last ticket simultaneously. The project is fully containerized using **Docker** and includes a comprehensive test suite.

## 🚀 Key Features

* **🔐 Secure Authentication:** Full JWT (JSON Web Token) implementation with password hashing (Bcrypt).
* **🛡️ Concurrency Safety:** Solves the **Race Condition** problem using Database Row Locking (`FOR UPDATE`) to prevent overselling tickets.
* **⚡ Async Database:** Uses `SQLAlchemy` 2.0 with `asyncpg` for non-blocking database operations.
* **🐳 Fully Dockerized:** One command to spin up the API, PostgreSQL Database, and PgAdmin interface.
* **🧪 Automated Testing:** Integration tests using `pytest`.
* **🔄 Database Migrations:** Schema version control using `Alembic`.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI
* **Database:** PostgreSQL 15
* **ORM:** SQLAlchemy (Async)
* **Migrations:** Alembic
* **Containerization:** Docker & Docker Compose
* **Testing:** Pytest, HTTPX

---

## 🏗️ Architecture Highlights

### 1. Handling Race Conditions (The "Overselling" Problem)
A common issue in ticketing systems is when two users request the last seat at the exact same millisecond. Without protection, both bookings succeed, and the event is oversold.

**Solution:** BookFast implements **Atomic Transactions** with Row-Level Locking.
```python
# From bookings.py
query = (
    select(models.Event)
    .where(models.Event.id == ticket_data.event_id)
    .with_for_update()  # 🔒 Locks the row until commit
)
```
This forces the database to process booking requests sequentially for that specific event, guaranteeing consistency.

### 2. Solving the N+1 Query Problem
When fetching tickets, naively loading related events leads to hundreds of database queries.

**Solution:** Used `contains_eager` to join and load related data in a single query.

```python
# From bookings.py cancellation logic
query = (
    select(models.Ticket)
    .join(models.Ticket.event)
    .options(contains_eager(models.Ticket.event)) #  One query instead of two
)
```

## 💻 Getting Started

### Prerequisites
* Docker Desktop installed and running.

### 1. Clone the Repository

```bash
git clone https://github.com/Aman00240/BOOKFAST.git
cd BOOKFAST
```

### 2. Configure Environment

Create a `.env` file in the root directory. You can use the following default values for local development:
```ini
# .env

# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Docker Internal URL
DATABASE_URL=postgresql+asyncpg://admin:SuperSecretStrongPassword123@db:5432/bookfast

# Database Credentials
POSTGRES_USER=admin
POSTGRES_PASSWORD=SuperSecretStrongPassword123
POSTGRES_DB=bookfast

# PgAdmin Credentials
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=root
```

### 3. Run with Docker

Start the entire stack (API, Database, PgAdmin):

```bash
docker-compose up --build
```

Once the containers are running, you can access the services:

* **API:** [http://localhost:8000](http://localhost:8000)
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **PgAdmin:** [http://localhost:5050](http://localhost:5050)


##  Running Tests

The project includes specific tests for Authentication, Event Lifecycle, and Concurrency/Race Conditions.

To run tests inside the Docker container:

```bash
docker-compose exec api pytest -v
```

## 📚 API Documentation

Once the app is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

### Key Endpoints

* **Auth:** `/register`, `/login`
* **Events:** `/events` (GET, POST, PATCH, DELETE)
* **Bookings:**
  * `POST /book` (Requires Auth, handles concurrency)
  * `POST /tickets/{id}/cancel` (ticket cancellation)

