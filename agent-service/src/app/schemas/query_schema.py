from pydantic import BaseModel
class QuerySchema(BaseModel):
    query : str
class QueryResponse(BaseModel):
    query: str
    agent_type: str



