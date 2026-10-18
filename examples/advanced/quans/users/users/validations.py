from __future__ import annotations

from shop_qua import Rule, RuleType, ValidationRules

from .constants import Role

register_validation = ValidationRules(
    body={
        "email": Rule(RuleType.EMAIL, required=True, max=120),
        "name": Rule(RuleType.STRING, required=True, min=2, max=60),
        "password": Rule(RuleType.STRING, required=True, min=8, max=100),
    }
)

login_validation = ValidationRules(
    body={
        "email": Rule(RuleType.EMAIL, required=True),
        "password": Rule(RuleType.STRING, required=True, max=100),
    }
)

role_validation = ValidationRules(body={"role": Rule(RuleType.ENUM, values=tuple(Role), required=True)})
