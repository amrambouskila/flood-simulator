const { emit, getToolFilePath, readHookPayload, toPosixPath } = require("./hookUtils.cjs");

const RULES = [
  {
    test: (p) => p.endsWith("/models.py"),
    context:
      "MODELS.PY EDITED — Verify: (1) all formulas match standard radiometric dating equations, (2) constants are named and documented, (3) units documented on every parameter, (4) no magic numbers in computation, (5) domain variable names used (P, D, lam, R, A), (6) type annotations on all methods, (7) epoch evolution conserves parent+daughter mass, (8) update docs/versions.md if behavior changed.",
  },
  {
    test: (p) => p.endsWith("/simulation.py"),
    context:
      "SIMULATION.PY EDITED — Verify: (1) CarbonSimulation references valid model APIs, (2) type annotations on all methods, (3) no stale references to create_model() or the old API, (4) numerical results consistent with FloodAdjustedModel.",
  },
  {
    test: (p) => p.endsWith("/app.py"),
    context:
      "APP.PY EDITED — Verify: (1) slider ranges match the parameter table in CLAUDE.md Section 7, (2) all tabs still render, (3) no hard-coded display values — derive from models, (4) Plotly charts configured correctly.",
  },
];

async function main() {
  const payload = await readHookPayload();
  const f = toPosixPath(getToolFilePath(payload));
  if (!f) return;
  const m = RULES.find((r) => r.test(f));
  if (m) emit({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: m.context } });
}

main().catch((e) => {
  process.stderr.write(`[hook] post-tool-use failed: ${e.message}\n`);
  process.exitCode = 0;
});
