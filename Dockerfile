# Use official Python lightweight image
FROM python:3.12-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
# PYTHONPATH: Ensures the app directory is in the import path
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

RUN mkdir -p logs input output/reports

# Create non-root user
RUN useradd -m -d /home/dprsuser -s /bin/bash dprsuser && \
    chown -R dprsuser:dprsuser /app

# Switch to non-root user
USER dprsuser

# Expose the API port
EXPOSE 8000

# Start the FastAPI application via Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
