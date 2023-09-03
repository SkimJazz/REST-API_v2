from db import db


class StoreModel(db.Model):
    """Model for the stores table in the database.

    'StoreModel' is the parent of 'ItemModel'. When we delete a store, we
    delete all the items in that store. We don't want to delete a store if
    there are items in that store. So we need to delete all the items in that
    store first. We can do that by using 'cascade="all, delete"' in the
    'items' relationship.

    id = db.Column(db.Integer, primary_key=True) -> id is the primary key.
    name = db.Column(db.String(80), unique=True, nullable=False) -> name is
    unique and can't be null.
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic",
    cascade="all, delete") -> one-to-many relationship. 'items' is a list of
    'ItemModel' objects. 'back_populates="store"' -> 'store' is the name of the
    relationship in the 'ItemModel'. 'lazy="dynamic"' -> don't create an object
    for each item in the store when we create a store. 'cascade="all, delete"'
    -> when we delete a store, delete all the items in that store.


    """
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship("ItemModel",
                            back_populates="store",
                            lazy="dynamic",
                            cascade="all, delete")

    tags = db.relationship("TagModel",
                           back_populates="store",
                           lazy="dynamic")
