# 🌾 Farm2Market

A Django-based web application that connects **farmers** directly with **buyers**, enabling streamlined product listings, cart management, order tracking, and logistics coordination — eliminating the need for middlemen.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [URL Routes](#url-routes)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)

---

## Overview

Farm2Market is a full-stack web platform built with **Django 6** and **PostgreSQL** (via Supabase). It supports two distinct user roles — **Farmer** and **Buyer** — each with their own dedicated dashboards, workflows, and views.

---

## Features

### 🧑‍🌾 Farmer
- Register with farm name, location, and bio
- Dashboard with product management (add, edit, view stock)
- Receive and manage orders (confirm, reject, assign logistics, dispatch, mark delivered)
- View in-stock / out-of-stock product statistics
- Real-time notification badges for new pending orders

### 🛒 Buyer
- Register with delivery address
- Browse and search products by name or category
- Add products to cart (supports **session-based cart** for unauthenticated users)
- Cart merges into account on login
- Checkout groups items by farmer and creates separate orders
- View order history and status updates
- Confirm receipt to complete an order
- Notification badges for delivered orders

### 🔔 Shared
- Role-based access control on all views
- Notifications system (per-user, per-order messages)
- Responsive UI with shared base template and footer
- Admin panel with all models registered

---

## 📸 Screenshots

Add your project screenshots to showcase the UI and functionality. Upload images to the `images/` folder and add them below:

### Farmer Dashboard
<img src="./images/4.jpeg" alt="Farmer Dashboard" width="600" />

### Buyer Dashboard
<img src="./images/9.jpeg" alt="Buyer Dashboard" width="600" />

### Product Listing
<img src="./images/5.jpeg" alt="Product Listing" width="600" />

### Cart Page
<img src="./images/6.jpeg" alt="Shopping Cart" width="600" />

---

## Tech Stack

| Layer        | Technology                             |
|--------------|----------------------------------------|
| Backend      | Django 6.0.3                           |
| Database     | PostgreSQL (Supabase) / SQLite (local) |
| Auth         | Django built-in authentication         |
| Image Upload | Pillow 12.2                            |
| Templates    | Django Templates (HTML/CSS/JS)         |

---

## Project Structure

```
Farm2Market/                  ← Root repo
├── Farm2Market/              ← Django project root
│   ├── Farm2Market/          ← Django config package
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── f2m_app/              ← Main Django app
│   │   ├── models.py         ← All data models
│   │   ├── views.py          ← All view logic (~727 lines)
│   │   ├── urls.py           ← App URL patterns
│   │   ├── admin.py          ← Admin registrations
│   │   ├── context_processors.py  ← Cart count & notifications
│   │   └── migrations/
│   ├── templates/
│   │   ├── base.html         ← Shared base layout
│   │   └── F2M/
│   │       ├── home.html
│   │       ├── register.html
│   │       ├── login.html
│   │       ├── products.html
│   │       ├── cart.html
│   │       ├── edit_product.html
│   │       ├── farmer_dashboard.html
│   │       ├── farmer_profile.html
│   │       ├── buyer_dashboard.html
│   │       ├── buyer_profile.html
│   │       └── footer.html
│   ├── media/                ← Uploaded product images
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                  ← Local secrets (not committed)
│   └── .env.example
├── Reports/
│   ├── Project_Proposal.pdf
│   ├── SRS.pdf
│   └── Project Progress Report.pdf
└── README.md
```

---

## Data Models

### `Profile`
Extends Django's built-in `User` model with a role.

| Field              | Type      | Description                          |
|--------------------|-----------|--------------------------------------|
| `user`             | OneToOne  | Linked Django `User`                 |
| `role`             | CharField | `farmer` or `buyer`                  |
| `farm_name`        | CharField | Farmer-only: farm name               |
| `farm_location`    | CharField | Farmer-only: farm location           |
| `bio`              | TextField | Farmer-only: bio                     |
| `delivery_address` | TextField | Buyer-only: delivery address         |

### `Category`
Product categories (created via the admin panel).

### `Product`
Listed by farmers; browsable by buyers.

| Field            | Type         | Description                    |
|------------------|--------------|--------------------------------|
| `farmer`         | ForeignKey   | Owning farmer profile          |
| `category`       | ForeignKey   | Product category               |
| `name`           | CharField    |                                |
| `price_per_unit` | IntegerField | Price in local currency        |
| `stock_quantity` | IntegerField | Available stock                |
| `unit`           | CharField    | e.g., kg, piece                |
| `image`          | ImageField   | Stored under `product_images/` |

### `Cart` / `CartItem`
One cart per buyer. Cart items track quantity and link to products.  
Anonymous users get a **session-based cart** that merges on login.

### `Order` / `OrderItem`
Orders are created per-farmer on checkout with a price snapshot.

**Order Status Flow:**
```
PENDING → CONFIRMED → ASSIGNED → OUT_FOR_DELIVERY → DELIVERED → COMPLETED
                                                              ↗
PENDING → REJECTED
PENDING → CANCELLED (by buyer)
```

### `Logistic`
Delivery service providers (e.g., Pathao, Steadfast) — assigned by farmers at the `CONFIRMED` stage.

### `Notification`
Per-user, per-order messages surfaced via context processors as navbar badges.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd Farm2Market
```

### 2. Create & activate a virtual environment

```bash
py -m venv my_env
my_env\Scripts\activate   # Windows
```

### 3. Install dependencies

Navigate to the directory containing `manage.py`:

```bash
cd Farm2Market
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your values:

```bash
copy .env.example .env
```

Edit `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

> **Tip:** Leave `DATABASE_URL` unset to use a local SQLite database for development.

### 5. Download media files

Download the `media/` folder from:  
📁 [Google Drive – Media Folder](https://drive.google.com/drive/folders/1gz0SvMe0pYM71-PdeljfQt_BYKn3_1tH)

Place it in the same directory as `manage.py` (`Farm2Market/media/`).

### 6. Run migrations

```bash
# First-time or after model changes:
python manage.py makemigrations
python manage.py migrate

# If models are unchanged:
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. (Optional) Add categories and logistics via Admin

Visit `http://127.0.0.1:8000/admin/` to:
- Add product `Category` entries (e.g., Vegetables, Fruits, Grains)
- Add `Logistic` providers (e.g., Pathao, Steadfast, Uber)

---

## Environment Variables

| Variable       | Required | Description                                         |
|----------------|----------|-----------------------------------------------------|
| `SECRET_KEY`   | Yes      | Django secret key for cryptographic signing         |
| `DEBUG`        | No       | `True` for development, `False` for production      |
| `DATABASE_URL` | No       | PostgreSQL connection string; defaults to SQLite    |

---

## Running the App

```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000/**

---

## Reports & Documentation

Project documents are located in the `/Reports` directory:

- 📄 `Project_Proposal.pdf` — Initial project proposal
- 📄 `SRS.pdf` — Software Requirements Specification
- 📄 `Project Progress Report.pdf` — Progress report