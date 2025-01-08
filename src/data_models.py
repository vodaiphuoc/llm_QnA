from pydantic.dataclasses import dataclass
from typing import List

@dataclass
class DocContext:
    content:str
    sim_score:float

@dataclass
class Context:
    contexts = List[DocContext]

    