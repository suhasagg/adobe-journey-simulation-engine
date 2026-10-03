from pydantic import BaseModel,Field
from typing import Any,Literal
class Edge(BaseModel):
    to:str
    when:dict[str,Any]|None=None
class Node(BaseModel):
    id:str
    type:Literal["start","condition","message","wait","event","conversion","end"]
    config:dict[str,Any]=Field(default_factory=dict)
    edges:list[Edge]=Field(default_factory=list)
class Journey(BaseModel):
    name:str
    start:str
    nodes:list[Node]
class PersonaSpec(BaseModel):
    name:str
    count:int=1
    attributes:dict[str,Any]=Field(default_factory=dict)
class SimulationRequest(BaseModel):
    tenant_id:str="acme"
    journey:Journey
    personas:list[PersonaSpec]
