"""Pure validation and traversal of operator-supplied goal trees."""

class SchemaError(ValueError):
    """Input violates the documented schema."""

MAX_TEXT = 20000
MAX_DEPTH = 64
FIELDS = {"id", "title", "synthetic", "children", "acceptance", "work_units", "max_atomic_units"}

def decompose(records):
    seen = set()
    tasks = []
    def visit(node, path, limit, depth, inherited):
        if depth > MAX_DEPTH:
            raise SchemaError("children: maximum depth 64 exceeded")
        if not isinstance(node, dict):
            raise SchemaError("record: expected object")
        unknown = set(node) - FIELDS
        if unknown:
            raise SchemaError("unknown field: " + sorted(unknown)[0])
        for field in ("id", "title"):
            value = node.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT:
                raise SchemaError(field + ": expected nonempty text of at most 20000 characters")
            if "\u2014" in value:
                raise SchemaError(field + ": em dash forbidden; use a hyphen")
        ident = node["id"]
        if ident in seen:
            raise SchemaError("id: duplicate " + ident)
        seen.add(ident)
        synthetic = node.get("synthetic", inherited)
        if type(synthetic) is not bool:
            raise SchemaError("synthetic: explicit boolean required on each root")
        if inherited is not None and synthetic != inherited:
            raise SchemaError("synthetic: child provenance must match root")
        limit = node.get("max_atomic_units", limit)
        if type(limit) is not int or not 1 <= limit <= 1000000:
            raise SchemaError("max_atomic_units: integer between 1 and 1000000 required")
        units = node.get("work_units")
        if units is not None and (type(units) is not int or not 1 <= units <= 1000000):
            raise SchemaError("work_units: integer between 1 and 1000000 required")
        acceptance = node.get("acceptance", [])
        if not isinstance(acceptance, list) or any(not isinstance(x, str) or not x.strip() or len(x) > MAX_TEXT or "\u2014" in x for x in acceptance):
            raise SchemaError("acceptance: list of nonempty text without em dashes required")
        children = node.get("children", [])
        if not isinstance(children, list):
            raise SchemaError("children: list required")
        current = path + [ident]
        if children:
            status, reason = "decomposed", "explicit children supplied"
        elif not acceptance:
            status, reason = "blocked", "missing acceptance criteria"
        elif units is None:
            status, reason = "blocked", "missing operator-supplied work_units"
        elif units > limit:
            status, reason = "blocked", "exceeds atomic size limit; supply children"
        else:
            status, reason = "atomic", "acceptance and size requirements satisfied"
        tasks.append({"id": ident, "title": node["title"], "path": current, "status": status, "reason": reason, "synthetic": synthetic, "work_units": units, "acceptance": acceptance})
        for child in children:
            visit(child, current, limit, depth + 1, synthetic)
    for root in records:
        visit(root, [], 1, 0, None)
    counts = {name: sum(t["status"] == name for t in tasks) for name in ("atomic", "blocked", "decomposed")}
    return {"schema_version": 1, "counts": {"roots": len(records), "nodes": len(tasks), **counts}, "tasks": tasks, "honesty": "Work units are operator-supplied sizing, not measured time. Time and money saved are unmeasured and are not reported."}
