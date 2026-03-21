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

# Run tests by default if no command is provided, or the CLI can be passed
# Since this is a CLI tool, setting the entrypoint to the Python CLI module
ENTRYPOINT ["python", "-m", "cli.main"]

# Default arguments for the entrypoint (can be overridden by docker run)
CMD ["--help"]
