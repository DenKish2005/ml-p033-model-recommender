# Repository knowledge graph

This is the complete graphify 0.9.97 snapshot of source commit
`b8505f4f0d7945baebe3d9e897b48df09d3268b9`, refreshed at the user's request on
2026-10-31. It contains **564 nodes, 1124 graph links and 39 communities**.
Graph-only publishing commits do not change the source baseline above; later
source changes are not represented automatically.

The incremental refresh replaces contributions from 3 code/JSON inputs and
5 documents since the previous `b316b5d` snapshot. It includes P033-003 source
cards and P033-004 preprocessing tests/fixes. P033-001 through P033-004 are DONE
within their cards; P033-005 is READY and unstarted, P033-023 remains DECISION.

- Open `graph.html` for the interactive graph; no server is required.
- Read `GRAPH_REPORT.md` for community names, cohesion and navigation questions.
- Use `graph.json` for graph queries and `extraction-audit.json` for raw relationships.
- `health.json` retains 164 unresolved raw AST endpoints and 56 undirected
  same-endpoint collapses. The final exported JSON has no dangling graph links.
- `coverage.json` records complete reading of all 22 source documents, including
  exact last-line receipts for the 5 documents re-extracted in this update.
- `cost.json` explicitly records unavailable host-agent token usage. Cumulative
  reported zeros exclude that unknown usage and do not mean zero actual cost.
- `benchmark.json` is a token-reduction estimate (40.2x on generic sample queries),
  not measured usage savings, answer-quality evidence or ML results.

The full generated directory is included, including extraction cache and manifest.
`.graphify_python` and `.graphify_root` preserve machine-local tool paths, and some
audit/cache records preserve absolute source paths. They are provenance, not portable
project-environment configuration. On another machine, resolve an interpreter that
can import graphify and regenerate these local pointers before using skill commands.
Keep graphify separate from the project's locked Python environment.

Treat the graph as a navigation aid. Verify conclusions against current files and
primary sources; planned work and accepted designs are not implemented behavior.
This refresh represents previously recorded source-review/preprocessing evidence;
it does not perform new source admission, dataset downloads or research benchmarks.
P033-005 was not started. Source semantics, symmetry, benchmark readiness and total
process RSS remain outside the synthetic preprocessing evidence.
