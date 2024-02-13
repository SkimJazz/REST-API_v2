# Dockerfile for REST API with Flask and Python
# Image provides a runtime environment for Linux containers with Python 3.10
# for local development and production environments.

FROM python:3.10
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

# Use docker-entrypoint.sh to run migrations then start Gunicorn process
CMD ["/bin/bash", "docker-entrypoint.sh"]