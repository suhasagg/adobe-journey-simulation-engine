import asyncio
from app.compiler import JourneyCompiler
from app.personas import SyntheticCustomerGenerator
from app.engine import Simulator
from app.analyzers import analyze
from app.policy import validate_policy
class SimulationService:
    async def execute(self,request):
        compiled=JourneyCompiler().compile(request.journey)
        users=SyntheticCustomerGenerator().generate(request.personas)
        sem=asyncio.Semaphore(50)
        async def one(u):
            async with sem:
                r=await Simulator().run_user(compiled,u)
                r["policy_findings"]=validate_policy(u,r)
                return u,r
        pairs=await asyncio.gather(*(one(u) for u in users))
        results=[r for _,r in pairs]
        summary=analyze(results)
        summary["findings"] += [f for _,r in pairs for f in r["policy_findings"]]
        return users,results,summary
