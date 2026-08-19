# Personal Expense Tracking and Financial Analytics Web Portal

A simple MCA mini project built with Flask, SQLite, Bootstrap, and Chart.js.

## Purpose

The portal allows a registered user to record received amounts and spending, view a recent transaction summary, and analyse category-wise financial data for the current month or a selected date range.

## Quick start

1. Create a virtual environment: `python -m venv .venv`
2. Activate it on Windows: `.venv\\Scripts\\activate`
3. Install packages: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Open `http://127.0.0.1:5000` in a browser.

The application creates `expense_portal.db` automatically. Register a new account before adding transactions.

## Project contents

- `app.py`: Flask routes, authentication, transaction handling, and dashboard queries.
- `schema.sql`: Database tables, sample inserts, and reusable SQL queries.
- `templates/`: HTML pages.
- `static/`: CSS and JavaScript files.
- `docs/`: Academic project documents, review material, and viva preparation.

## Academic note

Replace sample screenshots, student details, guide details, institution details, and actual test results before submission. Never include real passwords or personal financial data in the report.
