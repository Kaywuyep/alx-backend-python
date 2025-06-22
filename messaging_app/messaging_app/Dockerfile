# Use official Python image
FROM python:3.10

# Set working directory in the container
WORKDIR /app

COPY .gitignore .
COPY requirements.txt .
# COPY chats/ ./chats/
# COPY messaging_app/ ./messaging_app/
# COPY manage.py .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the whole project
# Now copy the entire project
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command (optional if using entrypoint script or docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
