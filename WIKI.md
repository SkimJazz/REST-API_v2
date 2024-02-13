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

## Limitations

The following limitations are related to the deployment of the app on Render.com. These limitations are not present
when running the app locally.

### Render.com: Free Web Service Deployment 

**Persistent Disk Storage** is not available on Render's free Web Service for API deployment. https://docs.render.com/disks

The database will be reset every time the app is deployed but also restarted upon accessing any endpoint that requires
a JWT token. This is because the database is empty and the user does not exist. This is not a problem for the 
app itself, but is a problem for testing the API's endpoints when using the Render.com URL and Swagger-ui docs.

Each time a JWT token is requested by an endpoint that requiers it, the database will be reset and the token will be 
invalid even after registering, athenticating, and refreshing the token regardless of a successful deployment. 
Using Insomnia on your local machine to test the endpoints will work as the database is not reset. In addition, using 
a PostgreSQL database on ElephantSQL and having the app connect to it via Render's Environment Variables will also not
work.

**Solution**: Use a paid Web Service deployment on Render.com or use a different deployment service.


### REST API Question 1:

This REST API project is deployed to Render and ElephantSQL for the database. I need to include a 
local database for this project. Currently DATABASE_URL is connected to ElephantSQL development
server.  Is it possible to include the flask CLI commants for creating a local database and seeding 
it with tables with data from models and include a DATABASE_URI as well as a DATABASE_URL in the 
app.config[SQLALCAMEY_DATABASE_URI]?



### Answer 1:
Yes, it is possible to include a local database and seed it with tables with data from models. 
You can use SQLite for local development. You can also include both DATABASE_URI and 
DATABASE_URL in the app.config['SQLALCHEMY_DATABASE_URI'].  First, you need to install 
Flask-Migrate if you haven't done so. Flask-Migrate is an extension that handles SQLAlchemy
database migrations for Flask applications using Alembic. You can install it using pip:

```python
# pip install Flask-Migrate
```

Then, you can modify your create_app function in app.py to check if the app is running in a 
development environment and use the local SQLite database in that case:

```python
def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "REST API v2"
    app.config["API_VERSION"] = "v2"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if os.getenv('FLASK_ENV') == 'development':
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///data.db'
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL")

    # rest of your code
```

In the above code, if the FLASK_ENV environment variable is set to 'development', the app will use 
a local SQLite database (sqlite:///data.db). Otherwise, it will use the DATABASE_URL from the 
environment variables.  Next, you can use Flask-Migrate to handle database migrations. 
You can initialize it in your create_app function:

```python
from flask_migrate import Migrate

def create_app(db_url=None):
    # your code

    db.init_app(app)
    migrate = Migrate(app, db)  # this line

    # your code
```

Now, you can use the flask db init, flask db migrate, and flask db upgrade commands to initialize 
the migration repository, generate a migration script, and apply the migration to the database, 
respectively.  To seed the database with data from your models, you can create a separate Python 
script that imports your models and the database instance, creates some instances of your models, 
and adds them to the database. Here is an example:

```python
from app import db
from models import MyModel

def seed_db():
    # create some instances of your models
    instance1 = MyModel(field1='value1', field2='value2')
    instance2 = MyModel(field1='value3', field2='value4')

    # add them to the session
    db.session.add(instance1)
    db.session.add(instance2)

    # commit the session to write the changes to the database
    db.session.commit()

if __name__ == '__main__':
    seed_db()
```

You can run this script manually whenever you want to seed your database.

### REST API Question 2:

How can I run the Flask CLI commands to create a local database and seed it with tables?

### Answer 2:

To run the Flask CLI commands for creating a local database and seeding it with tables, 
you need to use the terminal or command prompt. Here are the steps:
1. Initialize the migration repository. This creates a new directory (migrations/) that will 
contain the migration scripts:

```text
flask db init
```
2. Generate a migration script. This will create a new script in the migrations/versions/ directory:

```text
flask db migrate -m "Initial migration"
```

3. Apply the migration to the database. This will create the tables in the database:

```text
flask db upgrade
```

To seed the database with data from your models, you can create a Python script 
(let's call it seed_db.py) and run it:

```python
from app import db
from models import MyModel

def seed_db():
    # create some instances of your models
    instance1 = MyModel(field1='value1', field2='value2')
    instance2 = MyModel(field1='value3', field2='value4')

    # add them to the session
    db.session.add(instance1)
    db.session.add(instance2)

    # commit the session to write the changes to the database
    db.session.commit()

if __name__ == '__main__':
    seed_db()
```
To run the script, use the following command:

```text
# python seed_db.py
```
Remember to replace MyModel, field1, value1, etc. with your actual model names and data.

### REST API Question 3:

How can I check if the app is running in a development environment in Flask?

### Answer 3:

In Flask, you can check if the app is running in a development environment by checking the value 
of the FLASK_ENV environment variable. This variable is typically set in the .flaskenv file or in 
your system's environment variables.  Here's how you can do it:

```python
if os.getenv('FLASK_ENV') == 'development':
    # The app is running in a development environment
    # You can put your development-specific code here
```

In this code, os.getenv('FLASK_ENV') retrieves the value of the FLASK_ENV environment variable. 
If it's equal to 'development', then the app is running in a development environment.

### REST API Question 4:

How can I configure the Flask CLI commands for database migrations?

### Answer 4:

To configure the Flask CLI commands for database migrations, you need to use the Flask-Migrate 
extension. You have already imported it in your app.py file.  Here's how you can set it up:

1. Initialize Flask-Migrate with your application and the database instance. This is usually done 
in your application factory function. In your case, it's the create_app function.

```python
from flask_migrate import Migrate

def create_app(db_url=None):
    # your existing code

    db.init_app(app)
    migrate = Migrate(app, db)  # initialize Flask-Migrate

    # rest of your code
```

2. Now, you can use the Flask CLI commands for database migrations. Here are the most commonly used
commands:

- `flask db init:` This will create a new migrations folder in your project, which will contain all
your migration scripts.
- `flask db migrate -m "your message":` This will generate an automatic migration script based on 
  the changes detected on your models. The -m option allows you to add a message to the migration script.
- `flask db upgrade:` This will apply the migration to the database, creating or modifying the 
  tables as needed.

Remember to run these commands in your terminal from the root directory of your project.

### REST API Question 5:

Yes, both DATABASE_URL and DATABASE_URI can exist in the same .env file. These are just environment 
variables and you can have as many as you need. They can be used to store different database 
connection strings. For example, DATABASE_URL could be used for your production database, and 
DATABASE_URI could be used for your development database.  Here's an example of what your .env 
file could look like:

```python
#DATABASE_URL=postgresql://username:password@production_host/production_db
#DATABASE_URI=sqlite:///development.db
```

Remember to update your create_app function in app.py to use the correct environment variable 
based on the environment (development or production) your app is running in.