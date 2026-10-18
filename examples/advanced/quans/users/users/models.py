from __future__ import annotations

from shop_qua import FieldDefinition, FieldType, ModelDefinition

from .constants import Model, Role

user_model = ModelDefinition(
    Model.USERS,
    {
        "email": FieldDefinition(FieldType.STRING, required=True, unique=True),
        "name": FieldDefinition(FieldType.STRING, required=True),
        "password_hash": FieldDefinition(FieldType.STRING, required=True),
        "role": FieldDefinition(FieldType.ENUM, values=tuple(Role), required=True, default=Role.CUSTOMER, index=True),
    },
)
