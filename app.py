# REST API with Flask and Python
# Version: 2
# Author: JB
# Description:
#   - Version 2 of REST API project.
#   - import models module is also not working. It seems that PyCharm will
#     not recognize the module when it is in the same directory as app.py.

import os
from flask_smorest import Api
from flask_migrate import Migrate   # Flask-Migrate includes Alembic
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify

from db import db
from blocklist import BLOCKLIST

from resources.user import blp as UserBlueprint
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint


def create_app(db_url=None):
    """FACTORY PATTERN:

    When called, this function creates a Flask app and registers the
    blueprints for the resources. It also creates the database tables if
    they don't exist.

    Can be used to test the app with a different database URL.
    """
    app = Flask(__name__)  # http://127.0.0.1:5000  (default port)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "REST API v2"
    app.config["API_VERSION"] = "v2"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config[
        "OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"  # http://127.0.0.1:5000/swagger-ui
    app.config[
        "OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL",
                                                                "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize Flask SQLAlchemy extension (take flask app as argument & connect
    # it to SQLAlchemy)
    db.init_app(app)
    migrate = Migrate(app, db)  # migrate not in use, until it is!
    api = Api(app)

    # --------------------------- JWT CONFIGURATION ---------------------------- #

    app.config["JWT_SECRET_KEY"] = "90406336934580040544378782535470379379"
    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        """Check if a token is in the blocklist (i.e. revoked):

        This function checks if a given JWT token is in the blocklist.

        It is decorated with the 'token_in_blocklist_loader' decorator from the
        JWTManager, which means it will be called automatically whenever a
        protected endpoint is accessed. The function will receive the
        decoded JWT header and payload as arguments.

        Args:
            jwt_header (dict): The header of the JWT.
            jwt_payload (dict): The payload of the JWT.

        Returns:
            bool: True if the JWT's 'jti' (JWT ID, a unique identifier for the JWT)
                  is in the blocklist, False otherwise.
        """
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Error message for revoked token:

        function called when a revoked JWT token is used to access a protected
        endpoint (after checking if a token is in the blocklist).

        Decorated with the 'revoked_token_loader' decorator from the JWTManager,
        It will be called automatically whenever a revoked token is used.
        The function will receive the decoded JWT header and payload as arguments.

        Args:
            jwt_header (dict): The header of the JWT.
            jwt_payload (dict): The payload of the JWT.

        Returns:
            tuple: A tuple containing a JSON response with an error message and
            the HTTP status code 401.
        """
        return (
            jsonify(
                {"description": "The token has been revoked.",
                 "error": "token_revoked"}
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.",
                     "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.",
                 "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # --------------------------- END JWT CONFIGURATION ------------------------ #

    # Don't need the following if using Flask-Migrate for database migrations.
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)

    return app
