import json
import time
from koml_goal_decomposer.cli import main
from koml_goal_decomposer.fixtures import generate

def test_run_completes_on_fixture(tmp_path):
    generate(tmp_path / "input")
    start = time.perf_counter()
    assert main(["run", "--input", str(tmp_path / "input"), "--state", str(tmp_path / "state.json")]) == 0
    assert main(["report", "--state", str(tmp_path / "state.json"), "--format", "md", "--out", str(tmp_path / "report.md")]) == 0
    assert time.perf_counter() - start < 5

def test_empty_input_renders_without_traceback(tmp_path, capsys):
    state = tmp_path / "state.json"
    assert main(["run", "--input", str(tmp_path), "--state", str(state)]) == 0
    assert main(["report", "--state", str(state)]) == 0
    assert "nodes: 0" in capsys.readouterr().out

def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "bad.json").write_text('{\n broken}')
    assert main(["validate", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and "bad.json: line 2" in error

def test_determinism_byte_identical(tmp_path):
    generate(tmp_path / "input")
    for name in ("a", "b"):
        assert main(["run", "--input", str(tmp_path / "input"), "--state", str(tmp_path / name)]) == 0
    assert (tmp_path / "a").read_bytes() == (tmp_path / "b").read_bytes()

def test_cli_smoke_all_subcommands(tmp_path, capsys):
    source = str(tmp_path / "input"); state = str(tmp_path / "state")
    for args in (["fixtures", "--out", source], ["run", "--input", source, "--state", state], ["report", "--state", state], ["decompose", "--input", source], ["validate", "--input", source]):
        assert main(args) == 0
    import pytest
    for sub in ("fixtures", "run", "report", "decompose", "validate"):
        with pytest.raises(SystemExit) as exc:
            main([sub, "--help"])
        assert exc.value.code == 0
    assert "Example:" in capsys.readouterr().out

def test_missing_input(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err

def test_report_write_failure_no_partial_files(tmp_path, capsys):
    source = tmp_path / "input"; generate(source)
    state = tmp_path / "state"
    main(["run", "--input", str(source), "--state", str(state)])
    before = sorted(p.name for p in tmp_path.iterdir())
    assert main(["report", "--state", str(state), "--out", str(tmp_path)]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert sorted(p.name for p in tmp_path.iterdir()) == before

def test_five_record_handwritten_input(tmp_path):
    rows = [{"id": str(i), "title": "Manually entered example", "synthetic": False, "acceptance": ["Checked"], "work_units": 1} for i in range(5)]
    (tmp_path / "goals.json").write_text(json.dumps(rows))
    state = tmp_path / "result"
    assert main(["run", "--input", str(tmp_path), "--state", str(state)]) == 0
    assert json.loads(state.read_text())["counts"]["atomic"] == 5
