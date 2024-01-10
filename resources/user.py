"""
`user.py` module.

Contains User related operations such as User Registration, User Login,
and User Management (for testing purposes only).

Classes:
    - UserRegister: Handles the user registration process.
    - UserLogin: Handles the user login process.
    - User: Handles user management operations (for testing purposes only).

Each class is a Flask MethodView and is associated with a specific route for
handling HTTP requests.

This module uses Flask-Smorest for creating API endpoints, Flask-JWT-Extended
for handling JWTs, and Passlib for password hashing. It interacts with the
database through SQLAlchemy ORM.
"""

# Libraries and package imports
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,  # shortcut for get_jwt()["identity"]
    jwt_required,
    get_jwt,
)
from passlib.hash import pbkdf2_sha256

# Local imports
from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", "users", description="Operations on users")


# --------------------------- USER REGISTRATION ---------------------------- #

@blp.route("/register")
class UserRegister(MethodView):
    """
    Class represents the User Registration endpoint. It inherits from
    Flask's MethodView.

    Methods
    -------
    post(user_data: dict) -> Tuple[dict, int]
    Creates a new user in the database.
    """

    @blp.arguments(UserSchema)
    def post(self, user_data):
        """/register - Create user:

        This method handles the POST request at the /register endpoint.

        Parameters
        ----------
        user_data : dict
            A dictionary containing the user's data. It should have the
            following structure:
            {
                "username": <str>,  # The username of the user
                "password": <str>   # The password of the user
            }

        Returns
        -------
        Tuple[dict, int]
            A tuple containing a dictionary and an integer. The dictionary
            contains a message indicating the result of the operation.
            The integer is the HTTP status code of the response.

        Raises
        ------
        HTTPException
            A 409 HTTPException is raised when a user with the same username
            already exists in the database.
        """
        if UserModel.query.filter(
                UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


# --------------------------- USER LOGIN ----------------------------------- #

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        # Check if the user exists and the password is correct:
        #   For the body of the if statement to run, the user must exist
        #   then verify the password making sure it is valid
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")


# --------------------------- USER REFRESH --------------------------------- #

@blp.route("/refresh")
class TokenRefresh(MethodView):
    """Client Token Refresh Endpoint:

    TokenRefresh class represents the token refresh endpoint. Inherits from
    Flask's MethodView. This endpoint allows the client(Insomnia) to refresh
    the users token without requiring them to reauthenticate with the username
    and password.

    Methods
    -------
    post() -> Tuple[dict, int]
        Refreshes the access token for the current user.

    Decorators
    ----------
    jwt_required(refresh=True)
        Ensures that the current user has a valid refresh token before
        allowing them to access the endpoint.
    """

    @jwt_required(refresh=True)
    def post(self):
        """/refresh - Refresh access token:

        This method handles the POST request at the /refresh endpoint. It
        refreshes the access token for the current user.

        Returns
        -------
        Tuple[dict, int]
            A tuple containing a dictionary and an integer. The dictionary
            contains the new access token. The integer is the HTTP status
            code of the response.

        Raises
        ------
        HTTPException
            A 401 HTTPException is raised when the current user does not
            have a valid refresh token.
        """
        # Get the identity of the current user
        current_user = get_jwt_identity()

        # Create a new access token for the current user
        new_token = create_access_token(identity=current_user, fresh=False)

        # Get the JWT ID of the current refresh token
        jti = get_jwt()["jti"]

        # Add the JWT ID to the blocklist
        BLOCKLIST.add(jti)

        # Return the new access token and the HTTP status code
        return {"access_token": new_token}, 200


# ---------------------------- USER LOGOUT --------------------------------- #

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for JWT
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


# -------------- TESTING ONLY - NOT FOR PRODUCTION APP --------------------- #

@blp.route("/user/<int:user_id>")
class User(MethodView):
    """IMPORTANT => TESTING ONLY:

    Testing function for Getting user by ID and Deleting user by ID.

    Useful when testing the Flask app before production. May not want to
    expose it to public users, or they may delete each other's accounts!

    DELETE out this class before deploying!
    """

    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID:"""
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        """Delete user by ID:"""
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
