# KOML Goal Decomposer

A CPU-only, offline Python CLI that recursively traverses explicit goal trees and identifies atomic work. It never generates missing subtasks. Hypothesis: explicit rules and planted tests make decomposition auditable and trustworthy. Acceptance: 200 synthetic roots, exact counts and task identities, deterministic output, and a report under five seconds.

## Quickstart

```powershell
python -m pip install --no-build-isolation --no-deps -e .
kgd fixtures --out demo
kgd run --input demo
kgd report --format md
python -m pytest -q
```

If Windows installs `kgd.exe` outside PATH, add the user Python Scripts directory to PATH or use `python -m koml_goal_decomposer.cli` in place of `kgd`.

No runtime dependencies, network calls, models, GPU workloads, or randomness. No random seed is needed. Run commands from the same directory, or supply `--state` on run and report. JSON is UTF-8, outputs use deterministic ordering and no timestamps. Input file hashes provide traceability. Timings in EVIDENCE.md are measured locally and are not CLI estimates.

## Input format

Input directories contain JSON objects or arrays in `.json`, or one root per line in `.jsonl`. JSONL permits comment lines beginning with `#`. Reserved `expectations.json` and `SYNTHETIC.md` are fixture metadata, never task inputs. CSV and YAML are rejected with a named format error. Other file extensions are ignored.

Each root requires `id`, `title`, and boolean `synthetic`. Children inherit provenance and must not contradict it. IDs are unique across the complete input. Text must be nonempty, at most 20000 characters, and contain no em dash. Unicode and Windows path strings are supported. Unknown fields, including amounts and dates, are rejected: this domain has no monetary or date calculations. Negative, boolean, floating point, or excessive work units are rejected.

Optional fields: `children` (list), `acceptance` (list of nonempty strings), `work_units` (integer 1 to 1000000), `max_atomic_units` (same range, inherited, default 1). Work units are operator-declared hypothetical sizing, never measured duration. Maximum depth is 64. Parents with children are decomposed. Leaves with criteria and supplied units within the limit are atomic. Other leaves are blocked with a reason. Parent units are not summed, and no duration or cost totals are fabricated.

Five-record hand-written example, save as `own/goals.json`:

```json
[
  {"id":"a","title":"Ship checklist","synthetic":false,"children":[
    {"id":"b","title":"Write checklist","acceptance":["Checklist reviewed"],"work_units":1},
    {"id":"c","title":"Review checklist","acceptance":["Review recorded"],"work_units":1}
  ]},
  {"id":"d","title":"Undefined objective","synthetic":false},
  {"id":"e","title":"Large objective","synthetic":false,"acceptance":["Done"],"work_units":3}
]
```

This is an illustrative example, not shipped real Henry data. It contains five nodes and three roots. Real trials use Henry's manually entered data and remain local.

## Subcommands

- `kgd fixtures --out demo`: generate labelled synthetic data and hand-computed expectations.
- `kgd run --input demo --state results.json`: compute results and atomically save them.
- `kgd report --state results.json --format json --out report.json`: render JSON or Markdown with provenance.
- `kgd decompose --input demo`: print the recursive tree with atomic and blocked decisions.
- `kgd validate --input demo`: validate schema and print the complete computed JSON results.

Every subcommand supports `--help` with examples. Missing inputs return exit 2 and a usage hint. Parse errors name file and line. Schema errors name field and file; cross-file duplicate IDs name the directory. Bad report paths return a named write error and leave no partial files. Invalid runs preserve the previous state; rerun successfully before using that state for new data. State is a local generated artifact and should not be manually altered.

## Architecture

```text
local JSON/JSONL -> CLI parser and provenance hashes -> pure core validation/traversal
                                                    -> atomic result file
atomic result file -> report renderer -> Markdown/JSON -> stdout or atomic file
fixture generator -> labelled 200 roots + independent expected counts and IDs
```

## Honesty boundary and labelling

All results derive from supplied tree structure and declared criteria. The tool does not discover, predict, estimate, or verify task completion. Atomic means eligible under the declared rule, not objectively guaranteed executable. Time and money saved are unmeasured and are not reported. Synthetic JSONL has a header comment and every root has `synthetic: true`; JSON expectations have `synthetic: true` (JSON has no comment syntax); Markdown metadata has a synthetic comment. Reports list real declarations and synthetic sources separately, including input hashes in JSON. Real ownership is declared by the operator, not authenticated. Empty input reports zeros and no sources.

## Evidence and improvement hook

See EVIDENCE.md for planted outcomes and measured local validation. Four groups of 50 roots produce 100 atomic leaves, 100 blocked leaves, and 50 decomposed parents, totalling 250 nodes. Expectations are hand arithmetic and independent ID lists, not generated by the engine. Tests mutate inputs to show outputs are computed.

After two weeks of real use, Henry records run frequency and hand-checks a sample of classification decisions. Metric: incorrect decisions divided by reviewed decisions. Record sample IDs, expected and actual decisions, reviewer, dates, and numerator/denominator locally. An empty sample is unmeasured, never zero error. If error exceeds 10 percent, fix the largest demonstrated failure cause or kill with a recorded reason. If unused, kill or record a justified fix and rerun the trial.

Verdict is pending the two-week evidence window. No real usage, revenue, buyer interest, or time savings has been measured. Afterwards record expand for daily use or revenue, integrate for demonstrated sibling overlap, commercialise for demonstrated buyer willingness, maintain for portfolio evidence, or kill for non-use or failed acceptance. Do not imply the pending verdict is a completed real-world validation.
