from __future__ import annotations

from shop_qua import FieldDefinition, FieldType, ModelDefinition

from .constants import Model, Status

order_model = ModelDefinition(
    Model.ORDERS,
    {
        "user_id": FieldDefinition(FieldType.STRING, required=True, index=True),
        "status": FieldDefinition(FieldType.ENUM, values=tuple(Status), required=True, default=Status.PENDING),
        "items": FieldDefinition(FieldType.JSON, required=True),
        "lines": FieldDefinition(FieldType.JSON),
        "total": FieldDefinition(FieldType.NUMBER),
        "reason": FieldDefinition(FieldType.STRING),
    },
    indexes=(("user_id", "status"),),
)
