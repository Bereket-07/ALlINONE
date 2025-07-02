# Use official Python base image
FROM python:3.10-slim

# Avoid Python writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory inside container
WORKDIR /app

# Install system dependencies (optional, useful for debugging and builds)
RUN apt-get update && apt-get install -y gcc && apt-get clean

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (including .env for now)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI server via uvicorn from src.app
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
