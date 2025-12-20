FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ca-certificates
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt ./

# Install Python dependencies
# Use --trusted-host to work around SSL issues in CI environments
RUN pip install --no-cache-dir --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org && \
    pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
