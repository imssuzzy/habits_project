FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.3

# Configuring poetry
RUN poetry config virtualenvs.create false

WORKDIR /apps

# Copying requirements of a project
COPY pyproject.toml poetry.lock ./

# Installing requirements
RUN poetry install --no-root

# Copying actual application
COPY ./apps ./apps

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
