import json,pathlib,jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[1]

def test_all_contracts_are_valid_json_schemas():
    for path in (ROOT/"contracts").glob("*.schema.json"):
        schema=json.loads(path.read_text())
        assert schema["$schema"]=="https://json-schema.org/draft/2020-12/schema"
        jsonschema.Draft202012Validator.check_schema(schema)
