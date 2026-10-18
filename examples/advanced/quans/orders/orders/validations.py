from __future__ import annotations

from shop_qua import Rule, RuleType, ValidationRules

from .constants import Status

place_order_validation = ValidationRules(
    body={
        "items": Rule(
            RuleType.ARRAY,
            required=True,
            min=1,
            max=20,
            items=Rule(
                RuleType.OBJECT,
                fields={
                    "product_id": Rule(RuleType.STRING, required=True),
                    "quantity": Rule(RuleType.INTEGER, required=True, min=1, max=100),
                },
            ),
        )
    }
)

list_orders_validation = ValidationRules(query={"status": Rule(RuleType.ENUM, values=tuple(Status))})
