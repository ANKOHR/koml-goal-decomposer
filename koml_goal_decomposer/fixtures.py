"""Synthetic planted cases. No random generator or seed is used."""
import json
from pathlib import Path

def fixture_records():
    records = []
    for i in range(200):
        kind = i % 4
        node = {"id": f"goal-{i:03d}", "title": f"Synthetic objective {i}", "synthetic": True}
        if kind == 0:
            node.update(acceptance=["Explicit deliverable checked"], work_units=1)
        elif kind == 1:
            node.update(work_units=1)
        elif kind == 2:
            node.update(acceptance=["Explicit deliverable checked"], work_units=2)
        else:
            node["children"] = [{"id": f"task-{i:03d}", "title": "Synthetic child", "acceptance": ["Child checked"], "work_units": 1}]
        records.append(node)
    return records

def expectations():
    # Hand arithmetic: 50 per class; 50 parents each add one atomic child.
    return {"synthetic": True, "counts": {"roots": 200, "nodes": 250, "atomic": 100, "blocked": 100, "decomposed": 50}, "atomic_ids": [f"{prefix}-{i:03d}" for i in range(200) for prefix in (["goal"] if i % 4 == 0 else ["task"] if i % 4 == 3 else [])]}

def generate(directory):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    (path / "goals.jsonl").write_text("# SYNTHETIC fixtures, not real operator data\n" + "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in fixture_records()), encoding="utf-8")
    (path / "expectations.json").write_text(json.dumps(expectations(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (path / "SYNTHETIC.md").write_text("<!-- SYNTHETIC -->\nAll fixture data and expectations are synthetic.\n", encoding="utf-8")
