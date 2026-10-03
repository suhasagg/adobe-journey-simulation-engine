import hmac
from fastapi import Header,HTTPException
from app.config import settings
async def auth(x_api_key:str=Header(...)):
    if not hmac.compare_digest(x_api_key,settings.api_key): raise HTTPException(401,"invalid credential")
