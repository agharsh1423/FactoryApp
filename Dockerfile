# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Collect static files (safe to run during build)
RUN python manage.py collectstatic --noinput

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Use entrypoint script to run migrations before starting
ENTRYPOINT ["/app/entrypoint.sh"]

# Railway sets PORT env var, but we'll use Procfile for the actual command
CMD ["gunicorn", "factory_project.wsgi:application", "--bind", "0.0.0.0:8000", "--log-file", "-"]
