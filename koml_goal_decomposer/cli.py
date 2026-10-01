"""Local file CLI. Errors are named and writes replace atomically."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import decompose, SchemaError
from .fixtures import generate
from .report import render

class InputError(ValueError):
    pass

def load(directory):
    path = Path(directory)
    if not path.is_dir():
        raise InputError(f"MissingInput: {path}; use kgd fixtures --out <dir> or supply an existing directory")
    records, sources = [], []
    for file in sorted(path.iterdir()):
        if file.name in ("expectations.json", "SYNTHETIC.md"):
            continue
        if file.suffix not in (".json", ".jsonl"):
            if file.suffix.lower() in (".csv", ".yaml", ".yml"):
                raise InputError(f"SchemaError: {file.name}: line 1: unsupported format; use JSON or JSONL")
            continue
        if "\u2014" in file.name:
            raise InputError("SchemaError: filename: line 1: em dash forbidden; rename the input file")
        raw = file.read_bytes()
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise InputError(f"ParseError: {file.name}: line {raw[:exc.start].count(bytes([10])) + 1}: invalid UTF-8") from exc
        rows = []
        try:
            if file.suffix == ".jsonl":
                for line, text in enumerate(content.splitlines(), 1):
                    if text.strip() and not text.lstrip().startswith("#"):
                        try:
                            rows.append((line, json.loads(text)))
                        except json.JSONDecodeError as exc:
                            raise InputError(f"ParseError: {file.name}: line {line}: {exc.msg}") from exc
            else:
                data = json.loads(content)
                rows = [(1, row) for row in data] if isinstance(data, list) else [(1, data)]
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: {file.name}: line {exc.lineno}: {exc.msg}") from exc
        for line, row in rows:
            try:
                decompose([row])
            except SchemaError as exc:
                raise InputError(f"SchemaError: {file.name}: line {line}: {exc}") from exc
            records.append(row)
        for synthetic in sorted({r["synthetic"] for _, r in rows}):
            sources.append({"file": file.name, "sha256": hashlib.sha256(raw).hexdigest(), "synthetic": synthetic})
    try:
        result = decompose(records)
    except SchemaError as exc:
        raise InputError(f"SchemaError: input directory {path}: line 1: {exc}") from exc
    result["sources"] = sources
    return result

def atomic_write(path, content):
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=target.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(content)
        os.replace(temporary, target)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Recursively classify explicit goals without inventing tasks")
    subs = parser.add_subparsers(dest="command", required=True)
    fixture = subs.add_parser("fixtures", help="Generate 200 labelled synthetic roots", epilog="Example: kgd fixtures --out demo")
    fixture.add_argument("--out", required=True)
    for command, description in [("run", "Compute and store the complete task tree"), ("decompose", "Print the recursive task tree"), ("validate", "Validate all goals and report counts")]:
        sub = subs.add_parser(command, help=description, description=description, epilog=f"Example: kgd {command} --input demo")
        sub.add_argument("--input", required=True)
        if command == "run":
            sub.add_argument("--state", default=".kgd-results.json")
    report = subs.add_parser("report", help="Render computed results with provenance", epilog="Example: kgd report --format md")
    report.add_argument("--format", choices=["md", "json"], default="md")
    report.add_argument("--state", default=".kgd-results.json")
    report.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 SYNTHETIC goal records; work units are illustrative sizing, not measured time.")
        elif args.command in ("run", "decompose", "validate"):
            result = load(args.input)
            if args.command == "run":
                atomic_write(args.state, render(result, "json"))
                print("Computed results stored in " + args.state + ". Time and money saved are unmeasured.")
            elif args.command == "decompose":
                print(render(result), end="")
            else:
                print(render(result, "json"), end="")
        else:
            state = Path(args.state)
            if not state.is_file():
                raise InputError(f"MissingInput: {state}; first run kgd run --input <dir>")
            try:
                result = json.loads(state.read_text(encoding="utf-8"))
                output = render(result, args.format)
            except (ValueError, KeyError, TypeError) as exc:
                raise InputError(f"SchemaError: {state}: line 1: invalid result state; rerun kgd run") from exc
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
        return 0
    except (InputError, SchemaError, OSError, RecursionError) as exc:
        label = "WriteError" if isinstance(exc, OSError) else "InputError"
        print(f"{label}: {exc}".replace("\u2014", "-"), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
