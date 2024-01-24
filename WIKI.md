# Contributing to REST API v2 Project

## How to run the Dockerfile LOCALLY with Gunicorn

1. Clone the repository
2. Run `docker build -t name-of-image .` to build the image (name of image MUST be lowercase
3. Running a Volume Container in Windows:
```
docker run -p 5000:5000 -w /app -v "/c/Users/yourusername/FULL_PATH_TO_APP_IN_PROJECT_FOLDER:/app" NAME_IMAGE sh -c "flask run --host 0.0.0.0"

```

> Docker needs the Absolute Path to the app in the project folder. Path must be in double quotes.


Running a Volume on Mac:

