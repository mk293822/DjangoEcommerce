# Django E-Commerce

A fully functional **e-commerce web application** built with **Django**.  
This project supports product management, shopping cart functionality, checkout, and media handling.

---

## Features

- **Product Management** – Add, edit, delete, and view products with multiple images.  
- **Shopping Cart** – Add products to cart, update quantities, and remove items.  
- **Checkout** – Complete orders with a simple checkout flow.  
- **User Authentication** – Registration, login, password reset, and profile management.  
- **Admin Dashboard** – Manage products, orders, and users via Django Admin.  
- **Media Handling** – Supports local storage or Supabase cloud storage.  
- **Responsive Design** – Works on mobile, tablet, and desktop.  

---

## Tech Stack

- **Backend**: Django, Django REST Framework  
- **Frontend**: React (optional)  
- **Database**: SQLite (default) or PostgreSQL  
- **Storage**: Local media folder or Supabase (optional)  
- **Other**: Python, pip, virtualenv  

---

## Prerequisites

- Python 3.10+  
- pip  
- virtualenv  
- Node.js & npm (if using React frontend)  

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mk293822/DjangoEcommerce.git
   cd DjangoEcommerce

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux / Mac
   venv\Scripts\activate

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Debug to True in settings**
   ```bash
   DEBUG=TRUE

5. **Apply migrations**
   ```bash
   python manage.py migrate
   
6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   
7. **Run the development server**
   ```bash
   python manage.py runserver
   
8. **Open your browser at**
   ```bash
   http://127.0.0.1:8000




   
