from fastapi import APIRouter,Depends,HTTPException
from app.domain import SimulationRequest
from app.security import auth
from app.service import SimulationService
router=APIRouter(prefix="/v1",dependencies=[Depends(auth)])
@router.post("/simulations")
async def simulate(req:SimulationRequest):
    try: users,results,summary=await SimulationService().execute(req)
    except ValueError as e: raise HTTPException(400,str(e))
    return {"summary":summary,"users":users,"results":results}
