# Django Messaging App

A simple messaging API built with Django and Django REST Framework. It supports conversations between users, message sending, and user profiles.

---

## 🚀 Features

- User registration & profile management
- Create and list conversations
- Send and list messages within conversations
- Online status and last seen tracking
- RESTful API endpoints for easy integration

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default) – easily switch to PostgreSQL/MySQL in production
- **Authentication:** DRF's default authentication (can be extended to JWT)

---

## ⚙️ Setup & Installation

1️⃣ **Clone the repository:**

```bash
git clone https://github.com/your-username/django-messaging-app.git
cd django-messaging-app
python -m venv venv
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional):
python manage.py createsuperuser

# 6️⃣ Run the development server:
python manage.py runserver
```
