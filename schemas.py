from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    """Schema for item without store info:

    'PlainItemSchema' doesn't know anything about "stores" and doesn't deal
    with stores at all. It is used when we want to include a 'nested' item
    with in a store, but we don't want to include any information about the
    store itself.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ItemSchema(PlainItemSchema):
    """Schema for item with store info:

    'ItemSchema' inherits from 'PlainItemSchema' (have all fields from
    PlainItemSchema). When ItemSchema is used we're going to pass in
    'store_id' field when receiving data from client. And when sending
    data to the client we're going to include 'store' field (a nested
    field).


     'required=True' -> pass in store_id when receiving data from client.
     'load_only=True' -> don't include store_id when sending data to client.
     'dump_only=True' -> include 'store' when sending data to client.
    """
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ItemUpdateSchema(Schema):
    """Schema for item update:"""
    # name = fields.Str()
    # price = fields.Float()
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class StoreSchema(PlainStoreSchema):
    """Schema for store with items:

    'StoreSchema' inherits from 'PlainStoreSchema'. When StoreSchema is used
    we're going to include 'items' field (a nested field) when sending data
    to the client. We're not going to receive 'items' from the client.
    """
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)
