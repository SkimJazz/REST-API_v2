# REST API with Flask and Python
# Version: 2
# Author: JB
# Description:
#   - Version 2 of REST API project.
#   - import models module is also not working. It seems that PyCharm will
#     not recognize the module when it is in the same directory as app.py.

import os

from flask import Flask
from flask_smorest import Api

from db import db
import models

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
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize Flask SQLAlchemy extension (take flask app as argument & connect
    # it to SQLAlchemy)
    db.init_app(app)
    api = Api(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)

    return app

# @app.get("/store")
# def get_stores():
#     """/store Get all store data"""
#     return {"stores": list(stores.values())}
#
#
# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     """/store/<id> Get store data by ID"""
#     try:
#         # Here you might also want to add the items in this store
#         # We'll do that later on in the course
#         return stores[store_id]
#     except KeyError:
#         abort(404, message="Store not found")
#
#
# @app.post("/store")
# def create_store():
#     """/store Create new store"""
#     store_data = request.get_json()
#     if "name" not in store_data:
#         abort(
#             400,
#             message="Bad request. Ensure 'name' is included in the JSON payload.",
#         )
#     for store in stores.values():
#         if store_data["name"] == store["name"]:
#             abort(400, message=f"Store already exists.")
#
#     store_id = uuid.uuid4().hex
#     store = {**store_data, "id": store_id}
#     stores[store_id] = store
#
#     return store
#
#
# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#     """/store/<id> Delete store by ID"""
#     try:
#         del stores[store_id]
#         return {"message": "Store deleted."}
#     except KeyError:
#         abort(404, message="Store not found.")
#
#
# @app.get("/item")
# def get_all_items():
#     """/item Get all item data"""
#     return "Docker volume active"
#     # return {"items": list(items.values())}
#
#
# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     """/item/<id> Get item by ID"""
#     try:
#         return items[item_id]
#     except KeyError:
#         abort(404, message="Item not found")
#
#
# @app.post("/item")
# def create_item():
#     """/item Create item"""
#     item_data = request.get_json()
#     if (
#             "price" not in item_data
#             or "store_id" not in item_data
#             or "name" not in item_data
#     ):
#         abort(
#             400,
#             message="Bad request. Ensure 'price', 'store_id', and 'name' are included in the JSON payload.",
#         )
#     for item in items.values():
#         if (
#                 item_data["name"] == item["name"]
#                 and item_data["store_id"] == item["store_id"]
#         ):
#             abort(400, message=f"Item already exists.")
#
#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id": item_id}
#     items[item_id] = item
#
#     return item, 201
#
#
# @app.put("/item/<string:item_id>")
# def update_item(item_id):
#     """/item/<id> Update item by ID"""
#     item_data = request.get_json()
#     # There's  more validation to do here!
#     # Like making sure price is a number, and also both items are optional
#     # You should also prevent keys that aren't 'price' or 'name' to be passed
#     # Difficult to do with an if statement...
#     if "price" not in item_data or "name" not in item_data:
#         abort(
#             400,
#             message="Bad request. Ensure 'price', and 'name' are included in the JSON payload.",
#         )
#     try:
#         item = items[item_id]
#         item |= item_data
#
#         return item
#     except KeyError:
#         abort(404, message="Item not found.")
#
#
# @app.delete("/item/<string:item_id>")
# def delete_item(item_id):
#     """/item/<id> Delete item by ID"""
#     try:
#         del items[item_id]
#         return {"message": "Item deleted."}
#     except KeyError:
#         abort(404, message="Item not found.")
