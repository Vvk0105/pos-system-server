# Machine Test – Restaurant POS System (Django + React)

## Overview
A Point of Sale (POS) system for restaurant table management,
order handling, and payment processing.

This project meets all requirements mentioned in the assignment.

---

## Tech Stack
- Backend: Django, Django REST Framework
- Frontend: React (React Router, Axios)
- Database: SQLite

---

## Features Implemented

### ✔ Table Management
- List all tables with status (available / occupied)
- When an order is created → table becomes occupied
- After payment → table becomes available again

### ✔ Menu Management
- Menu items grouped by categories
- Only available items listed

### ✔ Orders
- Create new order with items
- Add items to existing order
- View full order details
- Prevent creating new order for already-occupied table
  (fetch active order automatically)

### ✔ Billing
- Automatic calculation of:
  - Subtotal
  - 5% tax
  - Final total
- Bill generation endpoint

### ✔ Payments
- Cash / Card options
- After payment:
  - Order marked paid
  - Table becomes available

### ✔ Dashboard
- List all active (unpaid) orders
- Quick access to billing

---

## How to Run

### 1. Clone & Install
git clone https://github.com/Vvk0105/pos-system-server.git

pip install -r requirements.txt
python manage.py migrate

### 2. Run Backend
python manage.py runserver


### 3. Run Frontend
git clone https://github.com/Vvk0105/pos-system-client.git

npm i
npm run dev


## Backend API Endpoints

### Tables
- GET `/api/tables/`
- POST `/api/tables/:id/occupy/`

### Menu
- GET `/api/menu/`

### Orders
- POST `/api/orders/`
- PUT `/api/orders/:id/add-items/`
- GET `/api/orders/:id/`
- GET `/api/orders/active/`
- POST `/api/orders/:id/complete/`
- GET `/api/orders/table/:table_id/active/` ← used by frontend

### Payments
- POST `/api/payments/`
