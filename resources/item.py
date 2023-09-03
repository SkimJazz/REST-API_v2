import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get an item by id:

        Retrieves the item from the database using the item's primary key.
        If the item doesn't exist, returns a 404 Not Found error automatically
        using 'query.get_or_404()' from SQLAlchemy. Don't need to check if
        item exists or not as SQLAlchemy does it for us.
        """
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        """Delete an item by id:"""
        item = ItemModel.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        """Update an item by id:

        Idempotent operation: The operation will produce the same result no
        matter how many times it is repeated. In other words, multiple identical
        requests will have the same effect as a single request.
        """

        item = ItemModel.query.get(item_id)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create a new item:

        ISSUE: An item can't be created with a duplicate name and store_id
        even if the 'price' is different. This is because the 'name' and
        'store_id' are the primary key for the item table. This is a
        limitation of the current design.
        """

        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item
