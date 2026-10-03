import asyncio
from app.expressions import matches
class Simulator:
    def __init__(self,max_steps=100):self.max_steps=max_steps
    async def run_user(self,compiled,user):
        node_id=compiled.start;events=[];messages=[];converted=False
        for seq in range(self.max_steps):
            node=compiled.nodes[node_id]
            events.append({"seq":seq,"node_id":node.id,"event_type":"ENTER","detail":{"type":node.type}})
            if node.type=="message":
                messages.append({"channel":node.config.get("channel","email"),"node":node.id})
            if node.type=="conversion": converted=True
            if node.type=="end" or not node.edges: break
            chosen=None
            for e in node.edges:
                if matches(user["attributes"],e.when):
                    chosen=e;break
            if not chosen:
                events.append({"seq":seq+1,"node_id":node.id,"event_type":"DROP_OFF","detail":{"reason":"no_matching_edge"}})
                return {"events":events,"messages":messages,"converted":converted,"dropped":True}
            node_id=chosen.to
            await asyncio.sleep(0)
        return {"events":events,"messages":messages,"converted":converted,"dropped":False}
