import json
from koml_goal_decomposer.cli import load
from koml_goal_decomposer.fixtures import generate, expectations
from koml_goal_decomposer.report import render

def test_report_matches_ground_truth_exact(tmp_path):
    generate(tmp_path)
    assert json.loads(render(load(tmp_path), "json"))["counts"] == expectations()["counts"]

def test_report_zero_false_positives(tmp_path):
    generate(tmp_path)
    actual = {t["id"] for t in load(tmp_path)["tasks"] if t["status"] == "atomic"}
    expected = set(expectations()["atomic_ids"])
    assert actual == expected

def test_report_carries_provenance_banner(tmp_path):
    generate(tmp_path)
    for format in ("md", "json"):
        assert "Data provenance | Synthetic fixtures: goals.jsonl" in render(load(tmp_path), format)

def test_hypothetical_figures_labelled(tmp_path):
    for format in ("md", "json"):
        output = render(load(tmp_path), format)
        assert "operator-supplied sizing, not measured time" in output
        assert "saved are unmeasured" in output

def test_no_em_dashes_in_outputs(tmp_path):
    generate(tmp_path)
    for format in ("md", "json"):
        assert "\u2014" not in render(load(tmp_path), format)

def test_mixed_provenance(tmp_path):
    (tmp_path / "real.json").write_text('{"id":"real","title":"Real declaration","synthetic":false}')
    (tmp_path / "fake.json").write_text('{"id":"fake","title":"Fixture","synthetic":true}')
    output = render(load(tmp_path))
    assert "Synthetic fixtures: fake.json" in output
    assert "ownership unverified): real.json" in output
