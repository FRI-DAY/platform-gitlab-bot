from typing import List

import yaml
from pydantic import BaseModel


class BranchPromotionConfig(BaseModel):
    source: str
    target: str
    labels: List[str] = []


class Config(BaseModel):
    promote_branches: List[BranchPromotionConfig]


def load_from_yaml(data):
    obj = yaml.safe_load(data)
    return Config.parse_obj(obj)
