# Local measured evidence

Measured on 2026-10-01, Python 3.12.10, Windows, CPU only.

- pytest: 31 passed.
- Three separate installed kgd processes (fixtures, run, Markdown report): 0.593705 seconds.
- Separate JSON report process: 0.177547 seconds.
- Computed counts: {"atomic": 100, "blocked": 100, "decomposed": 50, "nodes": 250, "roots": 200}.
- Exact atomic ID set equals 100 planted IDs: zero false positives and zero missed atomic cases, on synthetic data only.
- Mutating one supplied work size changes atomic count to 99 and blocked count to 101. Altering the expectations file does not influence computation.
- Repeated runs produce byte-identical state; JSON state includes source hashes and no timestamps.

These are local measured results, not production claims. No real-use accuracy, time saved, money saved, buyer interest, or revenue has been measured. The two-week improvement trial and final verdict are pending.
