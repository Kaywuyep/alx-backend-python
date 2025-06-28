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

pip install -r requirements.txt

# Create a superuser (optional):
python manage.py createsuperuser

# 6️⃣ Run the development server:
python manage.py runserver
```

## set up containerization using docker

- create a dockerfile
- `docker build -t messaging-app .` This tells Docker to build an image and tag it as messaging-app.
- `docker run -p 8000:8000 messaging-app` This maps your local port 8000 to the container's exposed port.
- `pip freeze > requirements.txt` to copy depensencies


```sql
CREATE DATABASE `messaging-app-db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;  -- Verify it was created
EXIT;
```

- Install minikube to set uo kubernetes on windows
```bash
choco install minikube
minikube version
```
- Deploy the Django Messaging App on Kubernetes
```bash
# apply services
kubectl apply -f deployment.yaml
kubectl apply -f mysql-secret.yaml
# Check Status and Logs
kubectl get pods
kubectl get services
kubectl logs <your-django-pod-name>
# start pods
kubectl port-forward service/django-messaging-service 8000:8000
# delete service
kubectl delete deployment messaging-app
kubectl delete pods <pod-name>
kubectl delete service <service-name>
#
```

```bash
docker tag messaging_app-messaging-app:latest kaywuyep/messaging-app:latest

```

```bash
minikube status
minikube start
```