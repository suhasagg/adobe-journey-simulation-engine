import uuid,random
class SyntheticCustomerGenerator:
    def generate(self,specs):
        out=[]
        for s in specs:
            for i in range(s.count):
                a=dict(s.attributes)
                a.setdefault("customer_id",f"sim-{uuid.uuid4().hex[:12]}")
                a.setdefault("engagement_score",round(random.random(),3))
                a.setdefault("consent",True)
                out.append({"persona":s.name,"attributes":a})
        return out
