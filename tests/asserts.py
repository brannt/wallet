from typing import Optional

from pydantic import BaseModel


def model_has_fields(model: Optional[BaseModel], **fields):
    # Allows us to pass results of database operations directly into the function
    assert model is not None

    model_dict = model.dict()
    assert {f: model_dict.get(f) for f in fields} == fields
