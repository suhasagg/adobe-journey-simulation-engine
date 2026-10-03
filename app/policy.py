def validate_policy(user,result):
    findings=[]
    if not user["attributes"].get("consent",True) and result["messages"]:
        findings.append({"kind":"POLICY","severity":"HIGH","message":"simulated contact to non-consenting persona",
                         "evidence":{"message_count":len(result["messages"])}})
    return findings
