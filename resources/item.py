# Library and package imports
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

# Local imports
from db import db
from models import ItemModel, StoreModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    """Item resource:

    Item class representing the Item resource used for retrieving, deleting
    and updating items in an existing store.
    """

    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get item by ID:

        Retrieves item from the database using the item's primary key.
        If the item doesn't exist, returns a 404 Not Found error automatically
        using 'query.get_or_404()' from SQLAlchemy. Don't need to check if
        item exists or not as SQLAlchemy does it for us.

        :param item_id: The ID of the item to retrieve.
        :return: The item identified by 'item_id' or a 404 error if it does not exist.
        """
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required(fresh=True)  # fresh access token needed
    def delete(self, item_id):
        """Delete item by ID:

        Method handles the HTTP DELETE request for a specific item
        identified by its 'item_id'.
        It deletes the item from the database and returns a success message.
        If the item does not exist, it returns a 404 error.

        :param item_id: The ID of the item to delete.
        :return: A success message or a 404 error if the item does not exist.
        """
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @jwt_required(fresh=True)  # fresh access token needed
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        """Update item by ID:

        Method handles the HTTP PUT request for a specific item identified by
        its 'item_id'. It updates the item in the database and returns the
        updated item. If the item does not exist, it returns a 404 error.

        Idempotent operation: The operation will produce the same result no
        matter how many times it is repeated. In other words, multiple identical
        requests will have the same effect as a single request.

        :param item_data: The new data for the item.
        :param item_id: The ID of the item to update.
        :return: The updated item or a new item if it did not exist.
        """
        item = ItemModel.query.get(item_id)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
            item.description = item_data["description"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    """ItemList resource:

    ItemList class representing the ItemList resource, used for retrieving all
    items in the database and creating a new item in an existing store.
    """
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items:

        Method handles the HTTP GET request for all items. It retrieves all
        items from the database( all items in all stores) and returns them.

        :return: A list of all items in the database.
        """
        return ItemModel.query.all()

    # @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create new item:

        Method handles HTTP POST request for creating a new item. It
        checks if the store exists and if an item with the same name exists in
        the same store. If the store does not exist or the item already exists,
        it aborts with a 400 error. If the item is successfully created, it
        returns the new item. If an error occurs while inserting the item, it
        aborts with a 500 error.

        SQLALCHEMY ISSUE: SQLAlchemy does not enforce key value constraints
        on the database. It only enforces constraints on the object model.
        This means that if we try to insert an item with a duplicate name
        even if the store_id and price is different, SQLAlchemy will not
        raise an error. This is because the 'name' and 'store_id' are the
        primary key for the item table.

        Using Migrations to create the database will enforce the constraints
        on the database level. However, if we create the database manually,
        SQLAlchemy will not enforce the constraints on the database level.

        :param item_data: The data for the new item.
        :return: Newly created item or an error message if item could not be created.
        """

        # Check if store exists before creating the item
        store = StoreModel.query.get(item_data["store_id"])
        if not store:
            abort(400, message="Store does not exist.")

        # Check if item with same name exists in same store
        item = ItemModel.query.filter_by(name=item_data["name"],
                                         store_id=item_data["store_id"],
                                         description=item_data["description"]).first()

        if item:
            abort(400,
                  message="An item with this name already exists in the store.")

        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item
