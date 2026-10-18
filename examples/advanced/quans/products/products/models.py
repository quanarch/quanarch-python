from __future__ import annotations

from shop_qua import FieldDefinition, FieldType, ModelDefinition

from .constants import Model

product_model = ModelDefinition(
    Model.PRODUCTS,
    {
        "name": FieldDefinition(FieldType.STRING, required=True, unique=True),
        "description": FieldDefinition(FieldType.TEXT),
        "price": FieldDefinition(FieldType.NUMBER, required=True),
        "stock": FieldDefinition(FieldType.INTEGER, required=True, default=0),
        "active": FieldDefinition(FieldType.BOOLEAN, required=True, default=True, index=True),
    },
)

#: Stock taken for an order. One per order, so an event delivered twice takes it once.
reservation_model = ModelDefinition(
    Model.RESERVATIONS,
    {
        "order_id": FieldDefinition(FieldType.STRING, required=True, unique=True),
        "items": FieldDefinition(FieldType.JSON, required=True),
        "total": FieldDefinition(FieldType.NUMBER, required=True),
    },
)
