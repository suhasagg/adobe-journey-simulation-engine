from app.expressions import matches
def test_ops():
 assert matches({"tier":"gold"},{"field":"tier","op":"eq","value":"gold"})
 assert matches({"x":5},{"field":"x","op":"gte","value":5})
