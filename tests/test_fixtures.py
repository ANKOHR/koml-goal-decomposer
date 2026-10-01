import json
from koml_goal_decomposer.fixtures import generate, expectations
from koml_goal_decomposer.cli import load

def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    text = (tmp_path / "goals.jsonl").read_text(encoding="utf-8")
    assert text.startswith("# SYNTHETIC")
    rows = [json.loads(line) for line in text.splitlines()[1:]]
    assert len(rows) == 200 and all(r["synthetic"] is True for r in rows)
    assert json.loads((tmp_path / "expectations.json").read_text())["synthetic"] is True
    assert (tmp_path / "SYNTHETIC.md").read_text().startswith("<!-- SYNTHETIC -->")

def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path)
    result = load(tmp_path)
    assert result["counts"] == {"roots": 200, "nodes": 250, "atomic": 100, "blocked": 100, "decomposed": 50}
    assert result["counts"] == expectations()["counts"]

def test_corrupted_ground_truth_changes_computed_output(tmp_path):
    generate(tmp_path)
    file = tmp_path / "goals.jsonl"
    lines = file.read_text().splitlines()
    record = json.loads(lines[1]); record["work_units"] = 2
    lines[1] = json.dumps(record)
    file.write_text("\n".join(lines) + "\n")
    result = load(tmp_path)
    assert result["counts"]["atomic"] == 99
    assert result["counts"]["blocked"] == 101
    expected = tmp_path / "expectations.json"
    expected.write_text('{"synthetic": true, "counts": {"atomic": 999}}')
    assert load(tmp_path)["counts"]["atomic"] == 99
