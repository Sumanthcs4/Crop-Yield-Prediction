FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install awscli and cleanup to keep image small
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start app
CMD ["python", "app.py"]
