from __future__ import annotations

from shop_qua import Rule, RuleType, ValidationRules

list_products_validation = ValidationRules(
    query={
        "search": Rule(RuleType.STRING, max=60),
        "limit": Rule(RuleType.INTEGER, min=1, max=100),
        "offset": Rule(RuleType.INTEGER, min=0),
    }
)

create_product_validation = ValidationRules(
    body={
        "name": Rule(RuleType.STRING, required=True, min=2, max=80),
        "description": Rule(RuleType.STRING, max=1000),
        "price": Rule(RuleType.NUMBER, required=True, min=0.01, max=100000),
        "stock": Rule(RuleType.INTEGER, min=0, max=100000),
    }
)

update_product_validation = ValidationRules(
    body={
        "name": Rule(RuleType.STRING, min=2, max=80),
        "description": Rule(RuleType.STRING, max=1000),
        "price": Rule(RuleType.NUMBER, min=0.01, max=100000),
        "active": Rule(RuleType.BOOLEAN),
    }
)

restock_validation = ValidationRules(body={"quantity": Rule(RuleType.INTEGER, required=True, min=1, max=10000)})
