# Enfranchisement calculation scripts

This folder contains small, dependency-free Python scripts for the examples
and replacement theorems in the LaTeX notes.

Run everything:

```sh
python3 scripts-codex-gpt5.5-xhigh/run_all.py
```

Run individual checks:

```sh
python3 scripts-codex-gpt5.5-xhigh/verify_counterexamples.py
python3 scripts-codex-gpt5.5-xhigh/verify_replacement_results.py
python3 scripts-codex-gpt5.5-xhigh/search_counterexamples.py
```

All scripts use only the Python standard library.  Probabilities are represented
with `fractions.Fraction` when the examples are rational.

