from app.compiler import JourneyCompiler
from app.domain import Journey
def test_compile():
 j=Journey.model_validate({"name":"x","start":"a","nodes":[{"id":"a","type":"start","edges":[{"to":"b"}]},{"id":"b","type":"end"}]})
 assert JourneyCompiler().compile(j).start=="a"
