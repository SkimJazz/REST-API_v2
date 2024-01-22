# Libraries and package imports
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local imports
from db import db
from models import StoreModel
from schemas import StoreSchema


blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    """

    Store class representing a single store.
    Two methods: get and delete.
    """
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """Get Store by ID:

        method retrieves a store by its ID.

        :param store_id: The ID of the store to retrieve.
        :type store_id: str
        :return: The store object associated with the given ID.
        :rtype: StoreModel
        """
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required(fresh=True)   # Oooh shit!, fresh access token needed here
    def delete(self, store_id):
        """Delete Store by ID:

        method deletes a store by its ID.

        :param store_id: The ID of the store to delete.
        :type store_id: str
        :return: A message indicating the store has been deleted.
        :rtype: dict
        """
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 200


@blp.route("/store")
class StoreList(MethodView):
    """

    StoreList class represents operations that can be performed on the
    collection of stores.

    Two methods: get and post.
    """
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        """Get all Store data:

        Method retrieves all the stores in the database including:
        store ID, items in stores, name of store and store tag.

        :return: A list of all the store objects in the database.
        :rtype: list
        """
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        """Create new Store:

        Method creates a new store with the provided data:

        :param store_data: The data for the new store.
        :type store_data: dict
        :return: The newly created store object.
        :rtype: StoreModel
        :raises IntegrityError: If a store with the same name already exists.
        :raises SQLAlchemyError: If an error occurred while creating the store.
        """

        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store.")

        return store
