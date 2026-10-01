import pytest
from koml_goal_decomposer.core import decompose, SchemaError

def node(**updates):
    return {"id": "one", "title": "Goal", "synthetic": False, "acceptance": ["Checked"], "work_units": 1, **updates}

@pytest.mark.parametrize("updates", [{"work_units": -1}, {"work_units": True}, {"work_units": 1000001}, {"title": "x" * 20001}, {"date": "2099-01-01"}, {"amount": -1}, {"synthetic": "true"}, {"children": {}}, {"title": "bad\u2014text"}])
def test_rejects_adversarial_values(updates):
    with pytest.raises(SchemaError):
        decompose([node(**updates)])

def test_duplicate_ids_rejected():
    with pytest.raises(SchemaError, match="duplicate"):
        decompose([node(), node()])

def test_handles_unicode_and_long_inputs():
    title = "目标 café C:\\Users\\henry " + "x" * 19000
    assert decompose([node(title=title)])["tasks"][0]["title"] == title

def test_explicit_recursive_decomposition():
    result = decompose([node(children=[node(id="child", children=[node(id="leaf")])])])
    assert result["counts"] == {"roots": 1, "nodes": 3, "atomic": 1, "blocked": 0, "decomposed": 2}
    assert result["tasks"][-1]["path"] == ["one", "child", "leaf"]

def test_missing_size_is_blocked():
    record = node(); del record["work_units"]
    assert decompose([record])["counts"]["blocked"] == 1

def test_depth_limit():
    record = node(id="0"); cursor = record
    for i in range(1, 66):
        child = node(id=str(i)); cursor["children"] = [child]; cursor = child
    with pytest.raises(SchemaError, match="depth"):
        decompose([record])
