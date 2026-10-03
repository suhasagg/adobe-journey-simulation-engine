from collections import Counter
def analyze(results):
    findings=[];paths=Counter();conversions=0;drop=0
    for r in results:
        path=tuple(e["node_id"] for e in r["events"] if e["event_type"]=="ENTER");paths[path]+=1
        conversions+=int(r["converted"]);drop+=int(r["dropped"])
        counts=Counter(m["channel"] for m in r["messages"])
        for ch,n in counts.items():
            if n>=3: findings.append({"kind":"FATIGUE","severity":"MEDIUM",
              "message":f"{n} simulated {ch} contacts for one user","evidence":{"channel":ch,"count":n}})
    total=max(len(results),1)
    if drop: findings.append({"kind":"DROP_OFF","severity":"HIGH","message":f"{drop} users dropped without a matching path",
                              "evidence":{"count":drop}})
    return {"users":len(results),"conversion_rate":conversions/total,"drop_off_rate":drop/total,
            "unique_paths":len(paths),"path_counts":{" -> ".join(k):v for k,v in paths.items()},"findings":findings}
