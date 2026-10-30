# Repository knowledge graph

This is the complete graphify 0.9.97 snapshot of source commit `b316b5d`,
published at the user's request. It contains 492 nodes, 885 graph links and
38 communities. Later repository changes are not represented automatically.

- Open `graph.html` for the interactive graph; no server is required.
- Read `GRAPH_REPORT.md` for community names, cohesion and navigation questions.
- Use `graph.json` for graph queries and `extraction-audit.json` for raw relationships.
- `health.json` retains 155 unresolved raw AST endpoints and 39 undirected
  same-endpoint collapses. The final exported JSON has no dangling graph links.
- `coverage.json` records complete reading of all 22 source documents.
- `cost.json` explicitly records unavailable host-agent token usage. Cumulative
  reported zeros exclude that unknown usage and do not mean zero actual cost.
- `benchmark.json` is a token-reduction estimate, not measured savings or ML results.

The full generated directory is included, including extraction cache and manifest.
`.graphify_python` and `.graphify_root` preserve machine-local tool paths, and some
audit/cache records preserve absolute source paths. They are provenance, not portable
project-environment configuration. On another machine, resolve an interpreter that
can import graphify and regenerate these local pointers before using skill commands.
Keep graphify separate from the project's locked Python environment.

Treat the graph as a navigation aid. Verify conclusions against current files and
primary sources; planned work and accepted designs are not implemented behavior.
No P033-003 source admission, dataset downloads or research benchmarks were performed
to generate or publish this snapshot.
