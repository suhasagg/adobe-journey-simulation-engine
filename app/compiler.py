from app.domain import Journey
class CompiledJourney:
    def __init__(self,j):
        self.name=j.name; self.start=j.start; self.nodes={n.id:n for n in j.nodes}
class JourneyCompiler:
    def compile(self,j:Journey)->CompiledJourney:
        ids={n.id for n in j.nodes}
        if j.start not in ids: raise ValueError("start node missing")
        for n in j.nodes:
            for e in n.edges:
                if e.to not in ids: raise ValueError(f"edge {n.id}->{e.to} targets missing node")
        self._reject_cycles(j)
        return CompiledJourney(j)
    def _reject_cycles(self,j):
        g={n.id:[e.to for e in n.edges] for n in j.nodes}; seen=set(); stack=set()
        def dfs(x):
            if x in stack: raise ValueError("cycle detected; reference simulator requires acyclic journeys")
            if x in seen:return
            stack.add(x)
            for y in g[x]: dfs(y)
            stack.remove(x);seen.add(x)
        dfs(j.start)
