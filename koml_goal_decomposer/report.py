"""Deterministic rendering with explicit provenance."""
import json

def banner(result):
    sources = result.get("sources", [])
    synthetic = [s["file"] for s in sources if s["synthetic"]]
    real = [s["file"] for s in sources if not s["synthetic"]]
    return "Data provenance | Synthetic fixtures: " + (", ".join(synthetic) or "none") + " | Real operator-entered data (declared by input, ownership unverified): " + (", ".join(real) or "none")

def render(result, format="md"):
    if format == "json":
        return json.dumps({**result, "provenance_banner": banner(result)}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    lines = ["# KOML Goal Decomposer", "", banner(result), "", result["honesty"], "", "## Computed counts", ""]
    lines += [f"- {key}: {value}" for key, value in result["counts"].items()]
    lines += ["", "## Tasks", ""]
    for task in result["tasks"]:
        # JSON quoting keeps multiline titles and control characters unambiguous.
        lines.append(f"- {json.dumps(task['path'], ensure_ascii=False)}: {task['status']} ({task['reason']}); title={json.dumps(task['title'], ensure_ascii=False)}")
    return "\n".join(lines) + "\n"
