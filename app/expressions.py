def matches(attrs:dict,cond:dict|None)->bool:
    if not cond:return True
    field=cond.get("field");op=cond.get("op","eq");value=cond.get("value");actual=attrs.get(field)
    if op=="eq":return actual==value
    if op=="ne":return actual!=value
    if op=="gt":return actual is not None and actual>value
    if op=="gte":return actual is not None and actual>=value
    if op=="lt":return actual is not None and actual<value
    if op=="in":return actual in value
    raise ValueError(f"unsupported operator {op}")
