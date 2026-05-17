# Enfranchisement scripts

These scripts support the paper's optimal-enfranchisement examples and
checks.  The planner chooses an odd-size franchise, that franchise decides by
strict majority, and welfare is the expected total stake of agents whose
opinion agrees with the chosen outcome.

The problem is that two plausible claims fail under arbitrary full-support
joint opinion distributions:

1. some voting franchise should weakly beat the planner's best constant
   dictatorship;
2. an optimal franchise should be high-stake, meaning it should not include a
   lower-stake agent while excluding a higher-stake one.

The scripts either verify the counterexamples to those claims, verify the
replacement results that hold under iid assumptions, or document how the small
counterexamples can be found mechanically.

## Run the checks

Run the dependency-free verification suite:

```sh
python3 scripts/run_all.py
```

Run individual checks:

```sh
python3 scripts/verify_counterexamples.py
python3 scripts/verify_replacement_results.py
python3 scripts/search_counterexamples.py
```

All verification scripts use only the Python standard library.  Probabilities
are represented exactly with `fractions.Fraction`.

## What each script does

- `common.py` contains the shared model code: binary states, odd franchises,
  strict-majority outcomes, expected welfare, high-stake checks,
  full-support mixtures, and iid formula helpers.  Keeping this shared avoids
  reimplementing the welfare calculation differently across examples.

- `verify_counterexamples.py` checks the paper's two negative examples with
  exact rational arithmetic.  It verifies that the best constant dictatorship
  beats every franchise in the first example, and that the unique optimum is
  not high-stake in the second.  It also adds a small uniform component where
  needed to confirm the examples satisfy full support without changing the
  strict rankings.

- `verify_replacement_results.py` checks the positive replacement claims under
  iid opinions.  It tests the insider-advantage identity, enumerates sample iid
  cases where optimizers are high-stake, checks the balanced-opinion comparison
  against dictatorship, and verifies the fair-coin prefix rule and equal-stakes
  corollary on finite instances.

- `search_counterexamples.py` is a lightweight reproducibility script for the
  counterexamples used in the paper.  It does not run a broad search; it
  replays the small exact candidates and prints the relevant welfare margins.
  This keeps the standard check suite fast and deterministic.

- `explore_counterexamples.py` is the optional exploratory search tool.  It
  uses `scipy.optimize.linprog` to search for sparse distributions, then
  rationalizes them into exact integer-weight candidates that can be moved into
  the dependency-free scripts.  Use it when looking for smaller or cleaner
  examples, not as part of the normal proof check.

Run the exploratory tool with SciPy available, for example:

```sh
UV_CACHE_DIR=/private/tmp/uv-cache uv run --with scipy python scripts/explore_counterexamples.py
```
